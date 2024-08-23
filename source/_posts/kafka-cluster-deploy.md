---
title: Kafka cluster deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---
```
cd ~

mkdir -pv ~/kafka/kafka-logs

curl -o kafka_2.12-1.1.0.tgz <https://mirrors.ustc.edu.cn/apache/kafka/1.1.0/kafka_2.12-1.1.0.tgz>

tar xvf kafka_2.12-1.1.0.tgz -C ~/kafka
```



#### 修改配置文件：

<!-- more -->
    cp ~/kafka/kafka_2.12-1.1.0/config/server.properties{,.ori}
    vim ~/kafka/kafka_2.12-1.1.0/config/server.properties
    ...
    broker.id=0  每台服务器的broker.id不能相同
    log.dirs=~/kafka/kafka-logs
    zookeeper.connect=10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181
    delete.topic.enable=true    #删除topic(需要server.properties中设置delete.topic.enable=true否则只是标记删除)
    auto.create.topics.enable=false # 关闭自动创建topic
    ...


## 后台启动Kafka集群（3台都需要启动）

cd ~/kafka/kafka_2.12-1.1.0/bin
./kafka-server-start.sh -daemon ../config/server.properties

#### 查看kafka服务日志：

tail -f ~/kafka/kafka_2.12-1.1.0/logs/server.log

\################################################################################

#### 创建topic：

cd ~/kafka/kafka_2.12-1.1.0/bin
./kafka-topics.sh --create --zookeeper 10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181 --replication-factor 2 --partitions 1 --topic test  #  --replication-factor 2：复制两份，--partitions 1：创建1个分区，--topic：主题为test

#### 列出全部topic：

./kafka-topics.sh --list --zookeeper 10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181

#### 查看topic状态：

./kafka-topics.sh --describe --zookeeper 10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181 --topic test

#### 模拟客户端发送消息

./kafka-console-producer.sh --broker-list 10.0.0.11:9092,10.0.0.12:9092,10.0.0.13:9092 --topic test

> 回车后 输入一些内容，然后回车

#### 模拟客户端接收信息（如果能正常接收到信息说明kafka部署正常）

./kafka-console-consumer.sh --bootstrap-server 10.0.0.11:9092,10.0.0.12:9092,10.0.0.13:9092 --topic test --from-beginning

#### 删除topic：

./kafka-topics.sh --delete --zookeeper 10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181 --topic test

\################################################################################

## 监控： Kafka Offset Monitor

<https://github.com/quantifind/KafkaOffsetMonitor>

    java -cp KafkaOffsetMonitor-assembly-0.2.1.jar \
         com.quantifind.kafka.offsetapp.OffsetGetterWeb \
         --zk 10.0.0.11:12181,10.0.0.12:12181,10.0.0.13:12181 \
         --port 8080 \
         --refresh 10.seconds \
         --retain 1.days \
         &

\################################################################################

### 使用 ansible 将配置好的配置文件分发到三台主机上；

    ansibleansible remote_servers -i \_etc_ansible_hosts -m file -a "path=~/kafka state=directory" kafka_servers -m copy -a "src=~/kafka_2.12-1.1.0.tar.gz dest=~/ owner=root group=root mode=0644"
    
    ansible remote_servers -i \_etc_ansible_hosts -m file -a "path=~/kafka state=directory"
    ansible remote_servers -i \_etc_ansible_hosts -m file -a "path=~/kafka/kafka-logs/ state=directory"
    
    ansible remote_servers -i \_etc_ansible_hosts -m command -a "tar xf ~/kafka_2.12-1.1.0.tar.gz -C ~/kafka/"
    
    ansible remote_servers -i \_etc_ansible_hosts -m copy -a "src=~/kafka/kafka_2.12-1.1.0/config/server.properties dest=~/kafka/kafka_2.12-1.1.0/config/ owner=root group=root mode=0644"

### kafka服务启停操作：

        ansible remote_servers -i \_etc_ansible_hosts -m command -a "~/kafka/kafka_2.12-1.1.0/bin/kafka-server-start.sh -daemon ~/kafka/kafka_2.12-1.1.0/config/server.properties"
        ansible remote_servers -i \_etc_ansible_hosts -m command -a "~/kafka/kafka_2.12-1.1.0/bin/kafka-server-stop.sh"

\################################################################################

### 先停止kafka服务，后删除kafka安装目录：

        ansible deploy_servers -i \_deploy_hosts -m shell -a "kafka/kafka_2.12-1.1.0/bin/kafka-server-stop.sh"
        ansible deploy_servers -i \_deploy_hosts -m file -a "path=kafka state=absent"

\################################################################################

### FAQ：

Q：

A：
