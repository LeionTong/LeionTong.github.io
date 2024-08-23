---
title: Nginx的mod_zip模块安装和使用
date: 2018-03-03T09:00:00.000Z
tags: null
---
# Nginx的mod_zip模块安装和使用

## Step 1： 安装Nginx
预配置必要的环境

```
yum install gcc gcc-c++ automake pcre pcre-devel zlib zlib-devel openssl openssl-devel gd gd-devel
```



```
groupadd www
useradd -g www www
```
<!-- more -->


## Step 2： 编译安装nginx

```
cd /opt
curl -O https://nginx.org/download/nginx-1.12.2.tar.gz
tar xvf ./nginx-1.12.2.tar.gz
```

```
./configure \
--prefix=/opt/nginx \
--user=www \
--group=www \
--with-pcre \
--with-http_ssl_module \
--with-http_v2_module \
--with-http_realip_module \
--with-http_addition_module \
--with-http_sub_module \
--with-http_dav_module \
--with-http_flv_module \
--with-http_mp4_module \
--with-http_gunzip_module \
--with-http_gzip_static_module \
--with-http_random_index_module \
--with-http_secure_link_module \
--with-http_stub_status_module \
--with-http_auth_request_module \
--with-http_image_filter_module \
--with-http_slice_module \
--with-mail \
--with-threads \
--with-file-aio \
--with-stream \
--with-mail_ssl_module \
--with-stream_ssl_module \
--add-module=/opt/mod_zip \
```

```
make -j 2 && make install
```




## Step 3： 安装php-fpm
安装php-fpm，为节省时间使用yum安装

```
yum install php-fpm -y
vim /etc/php-fpm.d/php-fpm.conf
```



编写php脚本，测试PHP服务器功能

```
cat << EOF >> /opt/nginx/html/index.php
<?php
    phpinfo()
?>
EOF
```



## Step 4： 验证
编写php脚本，测试mod_zip功能

```
cat << EOF >> /opt/nginx/html/testzip.php
<?php
header('X-Accel-Chareset: utf-8');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename=test.zip');
header('X-Archive-Files: zip');
$crc32 = "-";
printf("%s %d %s %s\n", $crc32, 346506, '/1.png', 'a.png');
printf("%s %d %s %s\n", $crc32, 155834, '/2.png', 'b.png');
?>
EOF
```

