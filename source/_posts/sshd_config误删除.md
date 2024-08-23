---
title: sshd_config误删除如何恢复？
date: 2021-04-01T15:30:00.000Z
tags: Linux
---

# sshd_config误删除如何恢复？

方法1，拷贝默认配置文件：
```
cp /usr/share/openssh/sshd_config /etc/ssh/
```

记得校正配置，例如：
```
#PermitRootLogin prohibit-password
PermitRootLogin yes
X11Forwarding yes
```
<!-- more -->
方法2，卸载重装软件包：
```
apt purge openssh-server
apt install openssh-server

```

