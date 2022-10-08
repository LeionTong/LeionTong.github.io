---
title: shadowsocks-Manual-for-Server-&-Client-Usage
date: 2017-10-16T09:00:00.000Z
tags: null
---

# shadowsocks的CLI客户端(sslocal)使用指南

## Step1（非必需）：

### 服务端ssserver

安装：

`sudo apt install shadowsocks`

配置：



启动：
`sudo systemctl start shadowsocks.service`

## Step2：

### 客户端sslocal

安装：

`sudo apt install shadowsocks`

<!-- more --> 

备份原配置文件：

`cp /etc/shadowsocks/config.json{,.original}`

配置：

`vim /etc/shadowsocks/config.json`

示例：

```
leion@leion-sky:~$ cat /etc/shadowsocks/config.json.ori
{
    "server":"my_server_ip",
    "server_port":8388,
    "local_address": "127.0.0.1",
    "local_port":1080,
    "password":"mypassword",
    "timeout":300,
    "method":"aes-256-cfb",
    "fast_open": false,
    "workers": 1
}
```

启动 sslocal 进程：

`sslocal -c /etc/shadowsocks/config.json &>>/tmp/sslocal.log &`

杀掉正在运行的 sslocal 进程：

`ps -ef | awk '$9~/sslocal/{print $2}' | xargs kill -9`

将该命令放到 ~/.bashrc 以实现用户登录shell后自动启动：

`echo 'sslocal -c /etc/shadowsocks/config.json &>>/tmp/sslocal.log &' >> ~/.bashrc`

编写 systemd 服务单元脚本：

```
[Unit]
Description=Daemon to start Shadowsocks Client. Put this file as sslocal.service into '/lib/systemd/system/' directory.
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/sslocal -c /etc/shadowsocks/client.json

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl start sslocal.service
sudo systemctl enable sslocal.service
```



## Step3：

### 验证

`curl -x socks5://127.0.0.1:1080 google.com/ncr`

返回结果：
````
leion@leion-sky:~$ curl -x socks5://127.0.0.1:1080 google.com/ncr
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>301 Moved</title>
# 301 Moved
 The document has moved
[here](https://www.google.com/ncr). ```

````

