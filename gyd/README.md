# cdn过移动墙

系统：centos7
配置：双核2G

2921a95e-045e-67e4-dce2-ac7c681df975

## ⒈下载：
````
wget https://raw.githubusercontent.com/anwang520520/httpqd/master/gyd/gyd && chmod 744 /root/gyd

````
## ⒉环境安装
````
yum install -y python3 python3-devel gcc gcc-c++ git libnetfilter* libffi-devel && pip3 install --upgrade pip && pip3 install scapy netfilterqueue
````
## ⒊后台运行：
````
nohup ./gyd > gyd.log 2>&1 &
````
