---
title: Ubuntu_Desktop实验机初始配置
date: 2021-08-20T14:04:00.000Z
tags: linux
---

# Ubuntu_Desktop实验机初始化配置

```sh
#安装 sshd 服务
sudo apt install openssh-server -y
sudo sh -c "echo 'PermitRootlogin yes' >> /etc/ssh/sshd_config"
sudo systemctl start opensshd
```

```
#设置默认启动目标
sudo systemctl set-default multi-user.target  #默认为 graphical.target
```
<!-- more -->

```sh
#设置笔记本合上盖子不休眠
sudo sh -c "echo 'HandleLidSwitch=ignore' >> /etc/systemd/logind.conf"
or:
sudo sh -c "sed -i 's/#HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf"

sudo systemctl restart systemd-logind
```


参阅：
[[K.nowledge/Linux_OS/A-lINUX-BOX/SSH～Firewall~iptables~ufw~SELinux/SSH密钥注入远程主机]]

### "SysV 运行级别" 与 "systemd 启动目标" 之间的映射关系

Mapping between runlevels and systemd targets：
```
   ┌──────────────┬───────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────┐
   │SysV Runlevel │ systemd Target                                        │ Notes                                                                                         │
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │0             │ runlevel0.target, poweroff.target                     │ Halt the system.                                                                              │
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │1, s, single  │ runlevel1.target, rescue.target                       │ Single user mode.                                                                             │
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │2, 4          │ runlevel2.target, runlevel4.target, multi-user.target │ User-defined/Site-specific runlevels. By default, identical to 3.                             │ 
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │3             │ runlevel3.target, multi-user.target                   │ Multi-user, non-graphical. Users can usually login via multiple consoles or via the network.  │
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │5             │ runlevel5.target, graphical.target                    │ Multi-user, graphical. Usually has all the services of runlevel 3 plus a graphical login.     │
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │6             │ runlevel6.target, reboot.target                       │ Reboot                                                                                        │ 
   ├──────────────┼───────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┤
   │emergency     │ emergency.target                                      │ Emergency shell                                                                               │
   └──────────────┴───────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────┘
```

> Refer: https://wiki.archlinux.org/title/Systemd#Mapping_between_SysV_runlevels_and_systemd_targets


