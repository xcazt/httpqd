# https独立系统

安装命令：wget https://raw.githubusercontent.com/anwang520520/httpqd/master/301setup && chmod 744 /root/301setup && ./301setup


服务器重启或者服务停止：cd /root/301system/bin && ./setup &

# httpqd

http抢答301

使用方法： 第一步下载运行软件：
````
wget https://raw.githubusercontent.com/anwang520520/httpqd/master/z301/z301
````
第二步开权限：
````
chmod 777 /root/z301
````
再运行下列代码
````
nohup ./z301
````
访问地址：http://ip:8090 
管理账号：admin 
管理密码：admin888



# centos

wget https://raw.githubusercontent.com/anwang520520/httpqd/master/xz-libs-5.2.2-1.el7.x86_64.rpm

sudo rpm -Uvh xz-libs-5.2.2-1.el7.x86_64.rpm

sudo reboot

wget https://raw.githubusercontent.com/anwang520520/httpqd/master/xz-5.2.2-1.el7.x86_64.rpm

