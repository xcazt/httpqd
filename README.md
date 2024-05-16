# httpqd
http抢答301


使用方法：
第一步下载运行软件：

wget https://raw.githubusercontent.com/anwang520520/httpqd/master/redi301

第二步开权限：

chmod 777 /root/redi301


第二步运行下列代码

nohup ./redi301 -a 0.0.0.0:80 -t http://www.hao123.com

把80改成你想要监控的端口，http://www.hao123.com改成你的目标地址！
