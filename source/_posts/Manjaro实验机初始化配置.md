# Manjaro_xfce实验机初始化配置

```sh
# 启动 sshd 服务
# sudo sh -c "echo 'PermitRootlogin yes' >> /etc/ssh/sshd_config"
sudo systemctl enable sshd
sudo systemctl start sshd
```

```sh
#设置笔记本合上盖子不黑屏
sudo sh -c "sed -i 's/IgnoreLid=false/IgnoreLid=true/' /etc/UPower/UPower.conf"

sudo systemctl restart upower.service
```
同时：
```sh
#设置笔记本合上盖子不休眠
sudo sh -c "echo 'HandleLidSwitch=ignore' >> /etc/systemd/logind.conf"
or:
sudo sh -c "sed -i 's/#HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf"

sudo systemctl restart systemd-logind
```

参考：
[[Ubuntu实验机初始配置]]
[[K.nowledge/Linux_OS/A-lINUX-BOX/SSH～Firewall~iptables~ufw~SELinux/SSH密钥注入远程主机]]

