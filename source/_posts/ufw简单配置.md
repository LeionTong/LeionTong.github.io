---
title: Linux上的防火墙前端 - 配置 ufw 允许 KDE Connect
date: 2022-04-01T15:30:00.000Z
tags: Linux
---


# Linux上的防火墙前端 - 简单配置 ufw 允许 KDE Connect
Allow KDE Connect through firewall

Firewalld
```
sudo firewall-cmd --zone=public --permanent --add-port=1714-1764/tcp
sudo firewall-cmd --zone=public --permanent --add-port=1714-1764/udp
sudo systemctl restart firewalld.service
```

UFW firewall
```
sudo ufw allow 1714:1764/udp
sudo ufw allow 1714:1764/tcp
sudo ufw reload
```

Refer：
https://www.incredigeek.com/home/allow-kde-connect-through-firewall/

# 配置 ufw 允许 hotspot

1. 首先需要在ufw中开启数据包转发。
需要调整两个配置文件，将 /etc/default/ufw 文件默认转发策略的值更改为“ACCEPT”：

```
sudo vim /etc/default/ufw

...
DEFAULT_FORWARD_POLICY="ACCEPT"
...
```

然后编辑/etc/ufw/sysctl.conf并取消注释：

```
sudo vim /etc/ufw/sysctl.conf

...
net/ipv4/ip_forward=1  
net/ipv6/conf/default/forwarding=1  
...
```

2. 将规则添加到 /etc/ufw/before.rules 文件中。默认规则只配置过滤表，并且启用伪装nat表需要配置。将以下内容添加到文件顶部的标题注释之后：

```
sudo vim /etc/ufw/before.rules

...
# nat Table rules
*nat
:POSTROUTING ACCEPT [0:0]

# Forward traffic from wlp58s0 through enp0s20f0u2u1.
-A POSTROUTING -s 10.42.0.0/24 -o enp0s20f0u2u1 -j MASQUERADE

# don't delete the 'COMMIT' line or these nat table rules won't be processed
COMMIT
...
```

3. 最后，禁用并重新启用 ufw 以应用更改：
```
sudo ufw disable && sudo ufw enable
```

Refer：
https://ubuntu.com/server/docs/security-firewall
