---
title: Nginx 403 forbidden 问题全面解析
date: 2018-08-16 16:22:01
tags:
---

# Nginx 403 forbidden 问题全面解析

```
2020/07/16 15:48:34 [error] 2220#0: *1 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.253.20, server: _, request: "GET / HTTP/1.1", upstream: "http://[::1]:8001/", host: "172.18.253.20"
2020/07/16 15:48:34 [error] 2221#0: *4 "/home/leion/www/nginx_server_8001/index.html" is forbidden (13: Permission denied), client: 127.0.0.1, server: _, request: "GET / HTTP/1.0", host: "172.18.253.20"
```

上面的报错有两个问题，第一个是 nginx 负载均衡连接上游失败`connect() failed (111: Connection refused)`也就是本地 IPv6 地址所在端口访问不通，在 server{} 块下启用`listen [::]:8001;`即可。

第二个问题是本节的重点`403 forbidden (13: Permission denied)`。

## SELinux 状态

安全增强型 Linux（SELinux）是一种采用安全架构的 Linux® 系统，它能够让管理员更好地管控哪些人可以访问系统。它最初是作为 Linux 内核的一系列补丁，由美国国家安全局（NSA）利用 Linux 安全模块（LSM）开发而成。

CentOS 系统默认启用 SELINUX。

查看 SELINUX 的状态

```
sestatus
getenforce
grep '^SELINUX=' /etc/selinux/config
```

<!-- more --> 

关闭 SELINUX（更建议掌握 SELINUX 的工作原理和配置方法）

```
sed -i.bak 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
setenforce 0
```

TODO：后续专门研究 SELINUX 开启状态下如何解决的办法。

## WEB 资源目录下缺少 index 索引文件或 nginx 配置未(正确)指定 index

nginx 默认加载 index.html 文件作为索引，php-fpm 则默认加载 index.php，如果 WEB 资源目录下未提供该文件会报 403，如果使用 index.php，需要在 WEB 服务配置里指明，一般在 nginx.conf 或者 vhost/yourserver.conf (注意这里是你的 nginx 的 WEB 配置文件) 的 server{} 块下配置：`index index.php index.html index.htm`，按需配置。

## 权限

一般会遇到这样的状况：把 WEB 目录放到默认位置（如 /usr/share/nginx/html）访问没问题，或者放到根目录(/)下（如 /www/webserver/）访问也没问题，而放到普通用户家目录下访问则会 403 forbidden Permission denied。

可以查看 nginx worker process 的用户是谁：`ps aux | grep nginx`和`grep user /path/to/nginx.conf`。

一般来说为了安全，执行 nignx 进程的用户不应该通过 login 登录，下面是 CentOS7 中 epel 源里安装 nginx 时的预安装脚本，显示了设置用于执行 nginx 进程的用户和用户组的情况：

```
$ rpm -q --scripts nginx-filesystem
preinstall scriptlet (using /bin/sh):
getent group nginx > /dev/null || groupadd -r nginx
getent passwd nginx > /dev/null || \
    useradd -r -d /var/lib/nginx -g nginx \
    -s /sbin/nologin -c "Nginx web server" nginx
exit 0
```

注意到创建的 nginx 用户属于系统用户（ID 号小于 1000），家目录是/var/lib/nginx，用于存放代理和缓存数据，登录 shell 是/sbin/nologin，登录即退出，也就是不允许像普通用户一样登录。

### 先分析放到家目录以外的路径的情况

一般，系统的 root 的 umask 是 022，非特权用户 umask 是 002。无论如何新建的文件(夹)默认其他用户(o)都有 x 权限，因此无论目录属于任何一个用户，nginx 进程(的执行用户)都对 WEB 资源目录具有执行(x)权限，从而才允许对最终目标文件具有读取(r)权限。

建议这样做：单独在根下创建 WEB 资源目录并把 WEB 资源目录的属主和属组归属给普通用户 leion（`sudo mkdir -p /www/webserver && sudo chown leion.leion -R /www/webserver`），这样可以使用普通用户管理 WEB 资源。

> TIPS：WEB 服务权限的关键点在于对最终目标文件有读取权限，而最容易忽视的地方是从根到最终目标文件途中的所有目录的权限设置。换句话说，ningx 进程(的执行用户)要对 WEB 资源所在目录的所有递归父目录有(x)执行权限，注意是所有递归父目录。根(/)的默认权限是 555(dr-xr-xr-x)，ugo 均有 x 权限，无妨。

### 再来分析 WEB 资源放到家目录的情况

分两种情形：

1. 在普通用户的家目录下存放 WEB 资源，并使用普通用户运行 nginx 进程（不推荐）。
2. 在普通用户的家目录下存放 WEB 资源，并使用系统用户运行 nginx 进程（推荐）。

如果 WEB 目录是 ~/www/webserver/。

第 1 种情形的实现就是将 WEB 资源放到 ~/www/webserver/ 目录下，然后在 nginx.conf 里配置`user leion`，然后`sudo nginx -s reload`。

第 2 种情形的实现就是先将 WEB 资源放到~/www/webserver/目录下

由于 WEB 目录是 ~/www/webserver/，需要 nginx 进程的执行用户对 /home、/home/leion、/home/leion/www、/home/leion/www/webserver 这几个目录全都要有执行权限。而普通用户家目录默认权限 700，其他用户(o)无执行(x)权限。

```
$namei -om ~
f: /home/leion
 drwxr-xr-x root  root  /
 drwxr-xr-x root  root  home
 drwx------ leion leion leion
```

方法 1. 可以这样修正：`chmod o+x /home/leion`，不过这样做法只能先救急，稳态 WEB 服务不建议这么做，因为如此一来所有其他用户都可以至查看家目录下的详细信息了(`ls -l /home/leion`)。

方法 2. 还可以将 nginx_user 加入 普通用户的用户组 leion 里：`sudo usermod -aG leion nginx`，可以用`getent group leion`检查组内成员信息，然后让普通用户属组 leion 对 WEB 资源目录(/home/leion/www/webserver)自顶至下具有 x 权限：1.使用命令检查权限(`namei -om /home/leion/www/webserver`)，2.使用`chmod g+x /home/leion`（一般这一个命令就足够）和`chmod g+x /home/leion/www`和`chmod g+x /home/leion/www/webserver`对 WEB 资源的父目录逐层赋权，这种方法可以作为备选方案推荐。

> 备注：恢复默认的属组：`sudo usermod -G nginx nginx`，检查：`id nginx`。

其他方法. 其他方法无外乎是用户、属主、属组和文件(夹)读取(r)执行(x)权限的各种组合变体的运用，不再深入赘述。

**总结**

执行 nginx 进程的用户需要对 WEB 资源所在的目录树自顶至下所有目录全都有执行(x)权限，因此比较简单也是最建议的解决办法是把 WEB 目录独立出来，让 WEB 资源所在的目录树从除了根(/)以外的最顶端(比如/www)全都隶属于普通用户。

如果无法做到（比如 WEB 目录在别人的家目录下/home/leion/www/webserver），那么注意到如果一开始就是使用 leion 用户创建/home/leion/www/webserver 目录（`mkdir -p /www/webserver`）并上传 WEB 代码的话此时 WEB 资源目录（/home/leion/www/webserver）会很自然的隶属于 leion，此时可行的做法是将 nginx_user 加入 leion 的用户组里，然后让 leion 用户组对 WEB 资源目录(/home/leion/www)自顶至下具有 x 权限。

# 写在最后

可能用得到的网页测试命令：
`for i in {1..20}; do curl 172.18.253.20 ;done`

> 参考：
> <https://stackoverflow.com/questions/6795350/nginx-403-forbidden-for-all-files>
