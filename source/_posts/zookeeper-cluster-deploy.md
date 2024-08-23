---
title: Zookeeper cluster deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---
```
mkdir -pv /opt/zookeeper/{zkdata,zkdatalog}
curl -o /opt/zookeeper-3.4.12.tar.gz http://mirrors.ustc.edu.cn/apache/zookeeper/stable/zookeeper-3.4.12.tar.gz
tar xvf /opt/zookeeper-3.4.12.tar.gz -C /opt/zookeeper/
```

`cp /opt/zookeeper/zookeeper-3.4.12/conf/{zoo-example.cfg,zoo.cfg}`
<!-- more -->

```
vim /opt/zookeeper/zookeeper-3.4.12/conf/zoo.cfg
...
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/opt/zookeeper/zkdata
clientPort=12181
dataLogDir=/opt/zookeeper/zkdatalog
server.1=10.0.0.11:12888:13888
server.2=10.0.0.12:12888:13888
server.3=10.0.0.13:12888:13888
...
```


### 使用 ansible 将配置好的配置文件分发到三台主机上；
```
ansible all -i _etc_ansible_hosts -m file -a "path=/opt/zookeeper state=directory" zookeeper_servers -m copy -a "src=/opt/zookeeper-3.4.12.tar.gz dest=/opt/ owner=root group=root mode=0644"

ansible all -i _etc_ansible_hosts -m file -a "path=/opt/zookeeper state=directory"
ansible all -i _etc_ansible_hosts -m file -a "path=/opt/zookeeper/zkdata/ state=directory"
ansible all -i _etc_ansible_hosts -m file -a "path=/opt/zookeeper/zkdatalog/ state=directory"

ansible all -i _etc_ansible_hosts -m command -a "tar xf /opt/zookeeper-3.4.12.tar.gz -C /opt/zookeeper/"

ansible all -i _etc_ansible_hosts -m copy -a "src=/opt/zookeeper/zookeeper-3.4.12/conf/zoo.cfg dest=/opt/zookeeper/zookeeper-3.4.12/conf/ owner=root group=root mode=0644"
```

### 在zookeeper-server1上：
echo "1" > /opt/zookeeper/zkdata/myid
### 在zookeeper-server2上：
echo "2" > /opt/zookeeper/zkdata/myid
### 在zookeeper-server3上：
echo "3" > /opt/zookeeper/zkdata/myid

### zookeeper服务启停操作：
```
ansible all -i _etc_ansible_hosts -m command -a "/opt/zookeeper/zookeeper-3.4.12/bin/zkServer.sh start"
ansible all -i _etc_ansible_hosts -m command -a "/opt/zookeeper/zookeeper-3.4.12/bin/zkServer.sh status"
ansible all -i _etc_ansible_hosts -m command -a "/opt/zookeeper/zookeeper-3.4.12/bin/zkServer.sh stop"
```


### FAQ：

Q：
Error contacting service. It is probably not running.
A：
```
systemctl stop firewalld.service
ansible zookeeper_servers -m command -a "systemctl disable firewalld.service"
```
