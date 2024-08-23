---
title: Kibana deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---

### 准备好APP二进制包文件：

`curl -L -O <https://artifacts.elastic.co/downloads/kibana/kibana-6.3.0-linux-x86_64.tar.gz>`

### 创建启动APP的用户：

`id deploy &>/dev/null ; if [[ $? != "0" ]]; then useradd deploy; fi`

### 切换用户：

`su - deploy`

### 创建APP目录：
<!-- more -->

```
cd ~
mkdir -pv ./kibana
```



### 安装kibana APP：

`tar -xvf kibana-6.3.0-linux-x86_64.tar.gz -C /home/deploy/kibana`


### 修改配置 kibana.yml：

`cp /home/deploy/kibana/kibana-6.3.0-linux-x86_6/config/kibana.yml{,.ori}`

```
vim /home/deploy/kibana/kibana-6.3.0-linux-x86_64/config/kibana.yml
...
server.port: 5601
server.host: 10.0.0.13
server.name: "leion's kibana"
elasticsearch.url: "<http://10.0.0.11:9200>"
...
```



#### 启动kibana：

`su - deploy -c '/home/deploy/kibana/kibana-6.3.0-linux-x86_64/bin/kibana &>/dev/null &'`

### 查看健康状态：

`curl http://10.0.0.13:5601/status`

如果返回 `Status: Green` 表示正常：。

\################################################################################

### 使用 ansible 将配置好的配置文件分发到各节点主机上：

```
ansible kibana_servers -i kibana_hosts -m copy -a "src=/home/deploy/kibana/kibana-6.3.0-linux-x86_64.tar.gz dest=/home/deploy owner=root group=root mode=0644"

ansible kibana_servers -i kibana_hosts -m user -a "name=deploy password=deploy"

ansible kibana_servers -i kibana_hosts -m file -a "path=/home/deploy/kibana state=directory owner=deploy group=deploy mode=0755"

ansible kibana_servers -i kibana_hosts -m unarhchive -a "src=/home/deploy/kibana-6.3.0-linux-x86_64.tar.gz dest=/home/deploy/kibana"

ansible kibana_servers -i kibana_hosts -m copy -a "src=/home/deploy/kibana/kibana-6.3.0-linux-x86_64/config/kibana.yml dest=/home/deploy/kibana/kibana-6.3.0-linux-x86_64/config owner=deploy group=deploy mode=0644"
```



### 最后再赋权一遍，以防万一：

`ansible kibana_servers -i kibana_hosts -m command -a "chown -R deploy:deploy /home/deploy/deploy"`

### kibana服务启停操作：

`ansible kibana_servers -i kibana_hosts -m command -a "su - deploy -c /home/deploy/kibana/kibana-6.3.0-linux-x86_64/bin/kibana &>/dev/null &"`

=====================================================

### FAQ：


