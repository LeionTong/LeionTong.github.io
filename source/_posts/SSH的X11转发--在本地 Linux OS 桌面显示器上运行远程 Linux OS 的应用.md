---
title: SSH的X11转发--在本地 Linux OS 桌面显示器上运行远程 Linux OS 的应用
date: 2020-07-05T19:39:26.000Z
tags: linux
---

# SSH的X11转发--在本地 Linux OS 桌面显示器上运行远程 Linux OS 的应用

## 原理

> SSH的X11转发原理--来自ssh的manpage：
     如果 ForwardX11 变量设为 “yes” (或参见后面对 -X 和 -x 选项的描述), 并且用户正在使用 X11 (设置了 DISPLAY 环境变量), 和 X11 显示器的连接将自动以这种形式转发到远端: 任何用 shell 或命令启动的 X11 程序将穿过加密的通道, 从本地机器连接真正的 X 服务器. 用户不应该手动设置 DISPLAY.  可以在命令行上, 也可以在配置文件中设置 X11 连接的转发.
     ssh 设置的 DISPLAY 值将指向服务器, 但是显示器号大于零. 这很自然, 因为 ssh 在服务器上创建了一个 “proxy” X 服务器,把连接通过加密通道转发出去.

从原理来讲，对于用户login来说，本地主机是客户端（SSH Client），远程主机是服务端（SSH Server）；对于X11程序来说，本地主机是服务端(X Server)，远程主机是客户端(X Client)。

从实际使用体验来说，是用户在本地主机通过 SSH Client 登录到启用了 X11 转发功能的远程主机的 SSH Server 上执行 GUI 图形界面程序，此时本地主机的显示器(X Server DISPLAY)上会呈现远程主机的GUI程序的图形界面。

## 预准备

|  Linux |  SSH协议中的角色  |  X协议中的角色  |  OS  |  IP  |
|-|-|-|-|-|
|  本地Linux操作系统  |  SSH Client  |  X Server  |  ArchLinux  |  172.18.253.70  |
|  远程Linux操作系统  |  SSH Server  |  X Client  |  CentOS  |  172.18.253.19  |

## 本地Linux操作系统(X Server)操作

1. 安装依赖：
xauth用于授权，fonts用于字体显示。
Arch系统，执行：
`sudo pacman -S xorg-xauth xorg-fonts-*`
其他发行版软件包名称可能是 `xorg-x11-xauth` 和 `xorg-x11-fonts-*`。

<!-- more --> 

## 远程Linux操作系统(X Client)操作

1. 配置sshd
```
sudo vim /etc/ssh/sshd_config
...
X11Forwarding yes	#允许X11转发
X11UseLocalhost no	#禁止将X11转发请求绑定到本地回环地址上
AddressFamily inet	#（可选）强制使用IPv4通道。
...
```

2. 重启服务：`systemctl restart sshd`

3. 安装实验用GUI程序，采用 xclock，一个简单的时钟。
CentOS系统，执行：
`sudo yum install xclock`

## 实验

本地Linux操作系统(X Server)通过ssh连接远程Linux操作系统(X Client)，注意选项 -X
`ssh -X 172.18.253.19 xclock`
此时会直接在本地的X Server DISPLAY上（也就是本地的显示器上）打开xclock的GUI图形界面。

当然也可以`ssh -X 172.18.253.19`登录后执行xclock命令，同样的效果。


