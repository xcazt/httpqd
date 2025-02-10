#!/usr/bin/env python3
import signal
import sys
import logging
import asyncio
from scapy.all import *
from netfilterqueue import NetfilterQueue
import argparse
from collections import defaultdict
import traceback

# 设置日志配置
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


class TCPModifier:
    def __init__(self, window_size, window_scale, confusion_times):
        self.window_size = window_size
        self.window_scale = window_scale
        self.confusion_times = confusion_times
        self.edit_times = defaultdict(int)
        self.loop = asyncio.get_event_loop()

    def clear_window_scale(self, ip_layer):
        """清除TCP选项中的WScale"""
        if ip_layer.haslayer(TCP):
            tcp_layer = ip_layer[TCP]
            tcp_layer.options = [opt for opt in tcp_layer.options if opt[0] != 'WScale']
        return ip_layer

    def update_checksum(self, ip_pkt):
        """更新校验和"""
        del ip_pkt[IP].chksum
        del ip_pkt[TCP].chksum
        return bytes(ip_pkt)

    async def send_payloads(self, ip):
        """异步发送混淆数据包"""
        tasks = []
        for i in range(1, self.confusion_times + 1):
            _win_size = self.window_size if i != self.confusion_times else 65535
            ack_packet = IP(src=ip.dst, dst=ip.src) / TCP(
                sport=ip[TCP].dport,
                dport=ip[TCP].sport,
                flags="A",
                ack=ip[TCP].seq + i,
                window=_win_size,
                options=[('WScale', self.window_scale), ('NOP', '')] * 5
            )
            tasks.append(self.loop.run_in_executor(None, send, ack_packet, False))
        await asyncio.gather(*tasks)

    def clean_edit_times(self):
        """定期清理 edit_times 中未使用的键值"""
        keys_to_remove = []
        for key, count in self.edit_times.items():
            if count > 100:  # 自定义条件，假设超过 100 次后清理
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.edit_times[key]

    def modify_window(self, pkt):
        """修改TCP窗口大小"""
        try:
            ip = IP(pkt.get_payload())
            if ip.haslayer(TCP):
                key = (ip.dst, ip[TCP].dport)  # 使用元组作为键
                sa_flag = False

                if ip[TCP].flags == "SA":  # SYN-ACK 包
                    self.edit_times[key] = 1
                    ip = self.clear_window_scale(ip)
                    ip[TCP].window = self.window_size
                    sa_flag = True
                else:  # 其他 TCP 包
                    if key not in self.edit_times:
                        self.edit_times[key] = 1
                    if ip[TCP].flags in ["FA", "PA", "A"]:
                        ip[TCP].window = self.window_size if self.edit_times[key] <= 6 else 28960
                        self.edit_times[key] += 1

                # 更新校验和并设置包负载
                pkt.set_payload(self.update_checksum(ip))

                # 如果是 SYN-ACK 包，则发送混淆数据包
                if sa_flag and self.confusion_times > 0:
                    asyncio.run_coroutine_threadsafe(self.send_payloads(ip), self.loop)
            pkt.accept()
        except Exception:
            logging.error(f"Error processing packet: {traceback.format_exc()}")
            pkt.drop()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='TCP Window Size Modifier')
    parser.add_argument('-q', '--queue', type=int, required=True, help='iptables Queue Number')
    parser.add_argument('-w', '--window_size', type=int, required=True, help='TCP Window Size')
    parser.add_argument('-s', '--window_scale', type=int, help='TCP Window Scale', default=7)
    parser.add_argument('-c', '--confusion_times', type=int, help='Number of Confusion Packets', default=7)
    parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='WARNING',
                        help='Set the log level')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper(), logging.WARNING))
    modifier = TCPModifier(args.window_size, args.window_scale, args.confusion_times)

    # 启动事件循环
    loop = modifier.loop
    loop.create_task(loop.run_in_executor(None, modifier.clean_edit_times))  # 替代 asyncio.to_thread

    nfqueue = NetfilterQueue()
    nfqueue.bind(args.queue, modifier.modify_window)

    try:
        logging.info("Starting netfilter_queue process...")
        nfqueue.run()
    except KeyboardInterrupt:
        pass
    finally:
        nfqueue.unbind()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))
    main()
