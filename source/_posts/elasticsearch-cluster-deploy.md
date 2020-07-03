---
title: Elasticsearch cluster deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---
### 准备好deploy APP二进制包文件：

```
curl -L -O https//artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.3.0.tar.gz
curl -L -O https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.tar.gz
curl -L -O https://artifacts.elastic.co/downloads/kibana/kibana-6.3.0-linux-x86_64.tar.gz
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-6.3.0-linux-x86_64.tar.gz
```



### 创建普通用户：

```
id deploy &>/dev/null; if [[ $? != "0" ]]; then useradd deploy; fi
```



### 切换用户：

```
su - deploy
```

<!-- more --> 

### 创建 APP目录和数据目录：
```
cd ~
mkdir -pv ./{elasticsearch,logstash,kibana}
mkdir -pv ./{elasticsearch,logstash,kibana}/{data,logs} # （建议）可以放到单独分区的目录里：/data/{elasticsearch,logstash}/{data,logs}
```



### 更改deploy目录和数据目录权限：

```
chown -R deploy:deploy /home/deploy/{elasticsearch,logstash,kibana}   #如果是放到单独分区的目录里注意赋权： chown -R deploy:deploy /deploy
```

### 安装：

```
tar xvf elasticsearch-6.3.0.tar.gz -C /home/deploy/elasticsearch
tar xvf logstash-6.3.0.tar.gz -C /home/deploy/logstash/
tar xvf kibana-6.3.0.tar.gz -C /home/deploy/kibana/
```



### 修改配置文件：

```
cp /home/deploy/elasticsearch/elasticsearch-6.3.0/config/elasticsearch.yml{,.ori}
vim /home/deploy/elasticsearch/elasticsearch-6.3.0/config/elasticsearch.yml
```



```
cluster.name: es-cluster    #自定义，集群内统一
node.name: es-node-1    #自定义，集群内唯一
node.master: true   # 可选值：true|false
node.data: true
path.data: /home/deploy/elasticsearch/data/
path.logs: /home/deploy/elasticsearch/logs
#bootstrap.memory_lock: true
network.host: 10.0.0.11
http.port: 9200
discovery.zen.ping.unicast.hosts: ["10.0.0.11", "10.0.0.12"]
discovery.zen.minimum_master_nodes: 1
#gateway.recover_after_nodes: 3
```



#### 后台启动elasticsearch集群

```
su - deploy -c '/home/deploy/elasticsearch/elasticsearch-6.3.0/bin/elasticsearch -d'
```



### 使用 ansible 将配置好的配置文件分发到各节点主机上

```
ansible elasticsearch_servers -i elasticsearch_hosts -m file -a "path=/home/deploy/elasticsearch state=directory" ansible elasticsearch_servers -i elasticsearch_hosts -m copy -a "src=/home/deploy/elasticsearch-6.3.0.tar.gz dest=/home/deploy/ owner=root group=root mode=0644"

ansible elasticsearch_servers -i elasticsearch_hosts -m user -a "name=deploy password=deploy"

ansible elasticsearch_servers -i elasticsearch_hosts -m file -a "path=/home/deploy/elasticsearch state=directory owner=deploy group=deploy mode=0755"
ansible elasticsearch_servers -i elasticsearch_hosts -m file -a "path=/home/deploy/elasticsearch/data state=directory owner=deploy group=deploy mode=0755"
ansible elasticsearch_servers -i elasticsearch_hosts -m file -a "path=/home/deploy/elasticsearch/logs state=directory owner=deploy group=deploy mode=0755"

ansible elasticsearch_servers -i elasticsearch_hosts -m unarhchive -a "src=/home/deploy/elasticsearch-6.3.0.tar.gz dest=/home/deploy/elasticsearch"

ansible elasticsearch_servers -i elasticsearch_hosts -m copy -a "src=/home/deploy/elasticsearch/elasticsearch-6.3.0/config/elasticsearch.yml dest=/home/deploy/elasticsearch/elasticsearch-6.3.0/config owner=deploy group=deploy mode=0644"
```



### 使用 unarchlive 模块解压 zip 文件前需要先在目标主机上安装 unzip 包

```
ansible elasticsearch_servers -i elasticsearch_hosts -m yum -a "name=unzip state=present"
ansible elasticsearch_servers -i elasticsearch_hosts -m yum -a "list=unzip"  #等同于命令yum list unzip
```



### 安装 elasticsearch-analysis-ik 插件

```
ansible elasticsearch_servers -i elasticsearch_hosts -m unarchive -a "src=elasticsearch-analysis-ik-6.3.0.zip dest=/home/deploy/elasticsearch/elasticsearch-6.3.0/plugins/ik"
```



### 最后再赋权一遍，以防万一：

```
ansible elasticsearch_servers -i elasticsearch_hosts -m command -a "chown -R deploy:deploy /home/deploy/deploy"
```



### elasticsearch服务启停操作：

```
ansible elasticsearch_servers -i elasticsearch_hosts -m command -a "su - deploy -c /home/deploy/elasticsearch/elasticsearch-6.3.0/bin/elasticsearch -d"
```



### 查看集群健康状态：

`curl http:/10.0.0.11:9200/_cluster/health`

如果返回status=green表示正常，返回结果类似如下：

```
{"cluster_name":"es-cluster","status":"green","timed_out":false,"number_of_nodes":2,"number_of_data_nodes":2,"active_primary_shards":0,"active_shards":0,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":100.0}
```



### 查看集群状态：

`http://10.0.0.11:9200/_cluster/state`

`http://10.0.0.11:9200/_cluster/state?pretty`

### FAQ：

Q: 

报错：`org.elasticsearch.bootstrap.StartupException: java.lang.RuntimeException: can not run elasticsearch as root`

A:
不能以root账号执行，要以普通用户执行：
`su - deploy -c '/home/deploy/elasticsearch/elasticsearch-6.3.0/bin/elasticsearch -d'`

Q：
`elasticsearch java.nio.file.AccessDeniedException`
A：
出现这个异常的原因是当前用户没权限，解决办法，为普通用户deploy授权：

`chown -R deploy:deploy /usr/local/elasticsearch`

=======================================================

Q:

```
ERROR: [3] bootstrap checks failed
[1]&#x3A; max file descriptors [4096] for elasticsearch process is too low, increase to at least [65536][2]: max number of threads [3892] for user [deploy] is too low, increase to at least [4096][3]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```

A:



# deploy环境准备

由于Elasticsearch、Logstash、Kibana均不能以root账号运行。
但是Linux对非root账号可并发操作的文件、线程都有限制。
所以，部署deploy相关的机器都要调整：

## 修改文件限制

#### 修改系统文件

`vi /etc/security/limits.conf`

#### 增加的内容

```
soft nofile 65536
hard nofile 65536
soft nproc 2048
hard nproc 4096
deploy soft memlock unlimited
deploy hard memlock unlimited
```



### 调整进程数：

#### 修改系统文件

`vi /etc/security/limits.d/20-nproc.conf`

#### 调整成以下配置

```
soft    nproc     4096
root       soft    nproc     unlimited
```



### 调整虚拟内存&最大并发连接：

#### 修改系统文件

`vi /etc/sysctl.conf`

#### 增加的内容，执行 "sudo sysctl -p" 生效：

```
vm.max_map_count=655360
fs.file-max=655360
vm.swappiness=0
```

以上操作重启系统后生效: reboot

=======================================================

Q:

```
fatal: [10.0.0.12]&#x3A; FAILED! => {"changed": false, "msg": "Failed to find handler for "/root/.ansible/tmp/ansible-tmp-1530157101.0-36263796351235/source". Make sure the required command to extract the file is installed. Command "unzip" not found. Command "/usr/bin/gtar" could not handle archive."}
```

A: 目标主机缺少unzip命令。
Solution：在远程目标主机上执行安装命令：

`sudo yum install unzip`

`ansible remote_servers -i \_etc_ansible_hosts -m yum -a "list=unzip"`