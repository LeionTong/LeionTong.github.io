---
title: GRUB2引导启动项手动修复实战
date: 2021-08-20T18:00:00.000Z
tags: linux
---

# GRUB2引导启动项手动修复实战
### Pre

> 注意如果开机进入的是`grub-rescue`命令行需要先使用救急控制台修复到 normal 模式，具体修复方式参见[https://wiki.archlinux.org/title/GRUB_(简体中文)#使用救急控制台](https://wiki.archlinux.org/title/GRUB_(简体中文)#使用救急控制台)，操作摘录如下：

GRUB 应急控制台里可用的命令有 `insmod`，`ls`，`set` 和 `unset`。这个例子里用了 `set` 和 `insmod`。`set` 用来修改变量，`insmod` 用来载入模组以添加功能。

首先，用户必须知道启动分区 (`/boot`) 所在位置（是一个独立的分区或者是根目录下的子目录），然后设置：
```sh
grub rescue> set prefix=(hdX,Y)/boot/grub
```
其中 X 是物理驱动器的编号，而 Y 是分区的编号。
**注意：** 如果启动分区是个独立的分区，要在路径中省略 `/boot`（例如键入 `set prefix=(hdX,Y)/grub`）。

通过加载 `linux` 模组来扩展命令行的功能：
```sh
grub rescue> insmod i386-pc/linux.mod
```
或者直接
```sh
grub rescue> insmod linux
```

这个模组会启动对我们熟悉的 `linux` 和 `initrd` 命令的支持。

***
## /boot未单独分区，CentOS 7 系统为例：

### 1. 进入到 GRUB2 命令行，手动引导启动：

```shell
grub > search --file /boot/grub2/grub.cfg
 hd0,msdos6
grub > search --file /etc/centos-release
 hod0,msdos6
grub > set root=(hd0,6)
grub > linux /boot/vmlinuz-3.10.0-1127.el7.x86_64 root=/dev/sda6  #可用TAB键补全目录和文件名
grub > initrd /boot/initramfs-3.10.0-1127.el7.x86_64.img
grub > boot
```

> 可通过ls和cat等grub内置命令帮助辨识OS类型：
>
> ls (hd0,6)/etc/sysconfig/network-scripts/
>
> cat ifcfg-*  ...

***
## /boot是单独分区，lfs 系统为例：

### 1. 进入到 GRUB2 命令行，手动引导启动：

```shell
grub > search --file /grub/grub.cfg
 hd0,msdos4
grub > search --file /etc/lfs-release
 hd0,msdos8 hd0,msdos7
grub > cat (hd0,7)/etc/lsb-release
DISTRIB_RELEASE=9.0
DISTRIB_DESCRIPTION=Linux From Scratch
grub > set root=(hd0,4)
grub > linux (hd0,4)/vmlinuz-5.2.8-lfs-9.0 root=/dev/sda7  #此处需要单独指明/boot所在分区，而且注意内核文件在该分区的根目录下，因此不能写成`linux (hd0,4)/boot/vmlinuz...`。
grub > boot
```

### 2. 进入到 lfs 系统，修正 GRUB2 配置文件：

```shell
vi /boot/grub/grub.cfg
...
set root=(hd0,4)
linux /vmlinuz-5.2.8-lfs-9.0 root=/dev/sda7 ....
...
```

***
## /boot未单独分区，Ubuntu 18.04 系统为例：

### 1. 进入到 GRUB2 命令行，手动引导启动：

```shell
grub > search --file /boot/grub/grub.cfg
 hd0,msdos8
grub > search --file /etc/lsb-release
 hod0,msdos8 hd0,msdos7
grub > cat (hd0,8)/etc/lsb-release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=20.4
DISTRIB_CODENAME=focal
DISTRIB_DESCRIPTION="Ubuntu 20.04.3 LTS"
grub > set root=(hd0,8)
grub > linux /boot/vmlinuz-5.11.0-27-generic root=/dev/sda8  #可用TAB键补全目录和文件名
grub > initrd /boot/initrd.img-5.11.0-27-generic
grub > boot
```

### 2. 进入到 CentOS 系统，修正 GRUB2 引导记录和配置文件：

```shell
sudo grub-install /dev/sda
sudo grub-mkconfig -o /boot/grub/grub.cfg
```


## Refer：
- [GNU GRUB Manual 2.06](https://www.gnu.org/savannah-checkouts/gnu/grub/manual/grub/grub.html)
章节：5.4.2 GNU/Linux；
章节：6.4 Multi-boot manual config
- https://wiki.archlinux.org/title/GRUB
章节：[使用 GRUB 命令行](https://wiki.archlinux.org/title/GRUB_(简体中文)#使用_GRUB_命令行)
章节：[使用救急控制台](https://wiki.archlinux.org/title/GRUB_(简体中文)#使用救急控制台)

## Note:
实验环境分区状况：
hd0,msdos6	CentOS
hd0,msdos7	LFS
hd0,msdos8	Ubuntu
hd0,msdos4	LFS-boot
