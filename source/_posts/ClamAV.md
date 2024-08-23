---
title: ClamAV - Linux上的杀毒软件
date: 2022-01-03T15:33:00.000Z
tags: Linux
---

# ClamAV - Linux上的杀毒软件

## 安装

[安装](https://wiki.archlinux.org/title/Install)[ClamAV](https://archlinux.org/packages/?name=clamav)软件包。

```
sudo pacman -S clamav clamtk
```

## 更新数据库
更新病毒定义库：

<!-- more -->
```
sudo freshclam

```

如果使用代理，请编辑`/etc/clamav/freshclam.conf`，更新 HTTPProxyServer、HTTPProxyPort、HTTPProxyUsername 和 HTTPProxyPassword。

数据库文件保存在：

```
/var/lib/clamav/daily.cvd
/var/lib/clamav/main.cvd
/var/lib/clamav/bytecode.cvd
```

[启动/启用](https://wiki.archlinux.org/title/Start/enable) `clamav-freshclam.service`以使病毒定义保持最新。

```
sudo systemctl start clamav-freshclam.service
sudo systemctl enable clamav-freshclam.service
systemctl status clamav-freshclam.service
```

## 启动守护进程

**注释：**

-   需要`freshclam`在第一次启动服务之前运行，否则会遇到问题/错误，这将阻止 ClamAV 正确启动。
-   如果只想执行独立扫描，则不需要守护程序。请参阅下面的[扫描病毒](https://wiki.archlinux.org/title/ClamAV#Scan_for_viruses)。

该服务叫做`clamav-daemon.service`。[启动](https://wiki.archlinux.org/title/Start)它并[使其](https://wiki.archlinux.org/title/Enable )在系统启动时自动启动。

```
sudo systemctl start clamav-daemon.service
sudo systemctl enable clamav-daemon.service
systemctl status clamav-daemon.service
```

## 测试软件

为了确保 ClamAV 和定义安装正确，请使用 clamscan扫描[EICAR 测试文件](http://2016.eicar.org/86-0-Intended-use.html)（一个不含病毒代码的无害签名）。

```
curl https://secure.eicar.org/eicar.com.txt | clamscan -
```

输出 **必须** 包含：
```
stdin: Win.Test.EICAR_HDB-1 FOUND
```

### Option #1: Set up Fangfrisch
```
yay -S aur/python-fangfrisch
```

```
sudo -u clamav /usr/bin/fangfrisch --conf /etc/fangfrisch/fangfrisch.conf initdb

sudo systemctl enable fangfrisch.timer
sudo systemctl start fangfrisch.timer
systemctl status fangfrisch.timer
```

### Option #2: Set up clamav-unofficial-sigs
```
yay -S aur/clamav-unofficial-sigs
```

```
sudo clamav-unofficial-sigs.sh
sudo less /var/log/clamav-unofficial-sigs/clamav-unofficial-sigs.log
```

```
sudo systemctl enable clamav-unofficial-sigs.timer
sudo systemctl start clamav-unofficial-sigs.timer
systemctl status clamav-unofficial-sigs.timer
```

要更改任何默认设置，请参阅并修改`/etc/clamav-unofficial-sigs/user.conf`。

## 扫描病毒

按需扫描有两种选择：

### 使用独立扫描器

`clamscan` 可用于扫描指定文件、家目录或整个系统：

```
$ clamscan myfile
$ clamscan --recursive --infected $HOME
$ sudo clamscan -r -i / -l /var/log/clamscan.log
# clamscan --recursive --infected --exclude-dir='^/sys|^/dev' /
```

如果想要`clamscan`删除受感染的文件，请在命令中添加该`--remove`选项，或者可以使用它`--move=/dir`来隔离它们。

可能还想要`clamscan`扫描较大的文件。在这种情况下，将选项`--max-filesize=4000M`和`--max-scansize=4000M`附加到命令中。'4000M' 是最大的可能值，可以根据需要降低。

使用该`-l /path/to/file`选项会将`clamscan`日志打印到文本文件中，以定位报告的感染情况。

### 使用守护进程

`clamdscan`与上述用法类似，但要用到守护程序，守护程序必须运行才能使用该命令。多数选项都会被忽略，因为守护进程读取指定在`/etc/clamav/clamd.conf`中的设置。





## 技巧和窍门

### 多线程运行

#### 使用 clamscan

当从命令行使用`clamscan`扫描文件或目录时仅会用到单个 CPU 线程。在时间不关键或不希望计算机变得迟钝的情况下，这可能没问题。如果需要快速扫描大文件夹或 USB 驱动器，可能想要使用所有可用的 CPU 来加速该过程。

`clamscan`被设计为单线程，而`xargs`可用于并行运行扫描：

```
$ find $HOME -type f -print0 | xargs -0 -P $(nproc) clamscan 
```

在这个例子中，`-P`参数 for在与 CPU 一样多的进程中`xargs`同时运行`clamscan`（由`nproc`）报告。`--max-lines`和`--max-args`选项允许更精细地控制跨线程批量处理工作负载。

#### 使用 clamdscan

如果`clamd`守护程序正在运行，则可以使用`clamdscan`来替代 (查阅 [Starting the daemon](https://wiki.archlinux.org/title/ClamAV#Starting_the_daemon)):。

```
$ clamdscan --multiscan --fdpass $HOME
```

这里的`--multiscan`参数允许`clamd`使用可用线程并行扫描目录的内容。当守护进程在`clamav`用户和组下运行时，`--fdpass`参数被用来传递文件描述符权限给 `clamd`。

`clamdscan`可用的线程数在`/etc/clamav/clamd.conf` [clamd.conf(5)](https://man.archlinux.org/man/clamd.conf.5) 通过`MaxThreads`参数定义。即使可能会看到`MaxThreads`指定的数量超过 1（当前默认为 10），但当使用`clamdscan`命令行启动扫描而不指定`--multiscan`选项时，只会有一个有效的 CPU 线程用于进行扫描。


## 参阅

-   [Wikipedia:ClamAV](https://en.wikipedia.org/wiki/ClamAV "wikipedia:ClamAV")
- https://en.wikipedia.org/wiki/ClamAV
- http://www.clamav.net
- file:///usr/share/doc/ClamAV/html/index.html
- https://www.jianshu.com/p/5235b4972442
