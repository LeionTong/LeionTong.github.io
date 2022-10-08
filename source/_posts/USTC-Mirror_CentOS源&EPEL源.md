---
title: USTC-Mirror_CentOS源&EPEL源
date: 2018-08-16 16:22:01
tags:
---

USTC-Mirror_CentOS源&EPEL源

CentOS 源
https://mirrors.ustc.edu.cn/centos/

警告
操作前请做好相应备份。

对于 CentOS 8，使用以下命令替换默认的配置

```
sudo sed -e 's|^mirrorlist=|#mirrorlist=|g' \
         -e 's|^#baseurl=http://mirror.centos.org/$contentdir|baseurl=https://mirrors.ustc.edu.cn/centos|g' \
         -i.bak \
         /etc/yum.repos.d/CentOS-Base.repo \
         /etc/yum.repos.d/CentOS-Extras.repo \
         /etc/yum.repos.d/CentOS-AppStream.repo
```
对于 CentOS 6、7，使用以下命令替换默认配置

```
sudo sed -e 's|^mirrorlist=|#mirrorlist=|g' \
         -e 's|^#baseurl=http://mirror.centos.org/centos|baseurl=https://mirrors.ustc.edu.cn/centos|g' \
         -i.bak \
         /etc/yum.repos.d/CentOS-Base.repo
```
以上命令只替换了默认启用的仓库。替换之后请运行 yum makecache 更新缓存。

***

<!-- more --> 

EPEL 源
https://mirrors.ustc.edu.cn/epel/

说明
EPEL (Extra Packages for Enterprise Linux) 是由 Fedora Special Interest Group 为企业 Linux 创建、维护和管理的一个高质量附加包集合，适用于但不仅限于 Red Hat Enterprise Linux (RHEL), CentOS, Scientific Linux (SL), Oracle Linux (OL)。

```
sudo yum install -y epel-release
sudo sed -e 's|^metalink=|#metalink=|g' \
         -e 's|^#baseurl=https\?://download.fedoraproject.org/pub/epel/|baseurl=https://mirrors.ustc.edu.cn/epel/|g' \
         -i.bak \
         /etc/yum.repos.d/epel.repo
```

