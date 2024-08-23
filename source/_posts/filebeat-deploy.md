---
title: Filebeat deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---

### 准备好filebeat二进制包文件：
```
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-6.3.0-linux-x86_64.tar.gz
```




### 创建启动APP的用户：

```
id deploy &>/dev/null ; if [[ $? != "0" ]]; then useradd deploy; fi
```
<!-- more -->



### 切换用户：

```
su - deploy
```


### 创建APP目录：

```
cd ~
mkdir -pv filebeat
```



### 安装filebeat APP：

```
tar -xvf filebeat-6.3.0-linux-x86_64.tar.gz -C /home/deploy/filebeat
```



### 修改配置 filebeat.yml：

```
cp /home/deploy/filebeat/filebeat-6.3.0-linux-x86_64/filebeat.yml{,.ori}
vim /home/deploy/filebeat/filebeat-6.3.0-linux-x86_64/filebeat.yml
```



########################################################

### filebeat服务启停操作：

```
ansible filebeat_servers -i filebeat_hosts -m command -a "su - deploy -c /home/deploy/filebeat/filebeat-6.3.0-linux-x86_64/filebeat -e -c /home/deploy/filebeat/filebeat-6.3.0-linux-x86_64/filebeat.yml"
```



### FAQ：


