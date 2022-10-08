---
title: Logstash deploy
date: 2018-08-16T09:00:00.000Z
tags: null
---
### 准备好ELK APP二进制包文件：
```
curl -L -O <https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.tar.gz>
wget <https://download.elastic.co/demos/logstash/gettingstarted/logstash-tutorial.log.gz>
```
### 创建普通用户：
```
id deploy &>/dev/null ; if \[[ $? != "0" ]]; then useradd deploy; fi
```
### 切换用户elk：
```
su - deploy
```
### 创建APP目录和数据目录：
```
cd ~
mkdir -pv ./logstash
mkdir -pv ./logstash/{data,logs} # （建议）可以放到单独分区的目录里：/data/logstash/{data,logs}
```
### 更改ELK目录和数据目录权限：
```
chown -R deploy:deploy /home/deploy/logstash   #如果是放到单独分区的目录里注意赋权： chown -R deploy:deploy /logstash
```

### 安装APP：

<!-- more --> 

tar xvf logstash-6.3.0.tar.gz -C /home/deploy/logstash

### 修改配置 logstash.yml：
```
cp /home/deploy/logstash/logstash-6.3.0/config/logstash.yml{,.ori}
vim /home/deploy/logstash/logstash-6.3.0/config/logstash.yml
    ...
    path.data: /home/deploy/logstash/data
    path.logs: /home/deploy/logstash/logs
    ...
```
## logstash输入源使用log文件，输出到console： file => logstash => stdout

#### 新增配置 logstash-input-file-output-stdout.conf：
```
vim /home/deploy/logstash/logstash-6.3.0/config/logstash-input-file-output-stdout.conf
    ...
    input {
      file {
        path => "/opt/logstash-tutorial.log"
        start_position => "beginning"
      }
    }
    output {
      stdout { codec => rubydebug }
    }
    ...
```
#### 检查配置文件：
```
/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-file-output-stdout.conf --config.test_and_exit
```
#### 启动logstash：
```
su - deploy -c '/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-file-output-stdout.conf --config.reload.automatic'
```
################################################################################

## filebeat => logstash => stdout：logstash-input-beats-output-stdout

#### 新增配置 logstash-input-beats-output-stdout.conf：
```
vim /home/deploy/logstash/logstash-6.3.0/config/logstash-input-beats-output-stdout.conf
    ...
    input {
        beats {
            port => "5044"
        }
    }
    output {
        stdout { codec => rubydebug }
    }
    ...
```
#### 启动logstash：
```
su - deploy -c '/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-beats-output-stdout.conf --config.reload.automatic'
```
#### 在filebeat主机上模拟生成数据：
```
cp /opt/logstash-tutorial.log{,.ori}    #备份原始文件
cat /opt/logstash-tutorial.log.ori >> /opt/logstash-tutorial.log    #追加数据至log文件
```
#### 观察到logstash所在主机console有输出：
```sh
    {
           "message" => "86.1.76.62 - - [04/Jan/2015:05:30:37 +0000] \"GET /style2.css HTTP/1.1\" 200 4877 \"http://www.semicomplete.com/projects/xdotool/\" \"Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140205 Firefox/24.0 Iceweasel/24.3.0\"",
        "prospector" => {
            "type" => "log"
        },
              "beat" => {
                "name" => "localhost",
            "hostname" => "localhost",
             "version" => "6.3.0"
        },
          "@version" => "1",
        "@timestamp" => 2018-08-04T13:47:14.926Z,
              "host" => {
            "name" => "localhost"
        },
            "source" => "/opt/logstash-tutorial.log",
            "offset" => 146784,
             "input" => {
            "type" => "log"
        },
              "tags" => [
            [0] "beats_input_codec_plain_applied"
        ]
    }
```
################################################################################

## filebeat => logstash => elasticsearch：logstash-input-beats-output-es

#### 新增配置 logstash-input-beats-output-es.conf：
```
vim /home/deploy/logstash/logstash-6.3.0/config/logstash-input-beats-output-es.conf
    ...
    input {
        beats {
            port => "5044"
        }
    }
    # filter {}
    output {
      elasticsearch {
        hosts => [ "10.0.0.11:9200","10.0.0.12:9200" ]
        manage_template => false
        index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"
      }
    }
    ...
```
#### 启动logstash：
```
su - deploy -c '/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-beats-output-es.conf --config.reload.automatic'
```
################################################################################

## filebeat => kafka => logstash => stdout： logstash-input-kafka-output-stdout

#### 新增配置 logstash-input-kafka-output-stdout.conf：
```
vim /home/deploy/logstash/logstash-6.3.0/config/logstash-input-kafka-output-stdout.conf
    ...
    input {
      kafka {
        bootstrap_servers => "10.0.0.11:9092,10.0.0.12:9092,10.0.0.13:9092"
       }
    }
    # filter {}
    output {
        stdout { codec => rubydebug }
    }
    ...
```

#### 启动logstash：
```
su - deploy -c '/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-kafka-output-stdout.conf --config.reload.automatic'
```
################################################################################

## filebeat => kafka => logstash => elasticsearch： logstash-input-kafka-output-es

#### 新增配置 logstash-input-kafka-output-es.conf：
```
vim /home/deploy/logstash/logstash-6.3.0/config/logstash-input-kafka-output-es.conf
    ...
    input {
      kafka {
        bootstrap_servers => "10.0.0.11:9092,10.0.0.12:9092,10.0.0.13:9092"
        ## Here, "topics" of kafka in logstash input section equals to "topic" of output.kafka in filebeat.yml,
        ## as is "log_topics" of fileds of filebeat.inputs in filebeat.yml
        topics => "leion"
        consumer_threads => 1
        decorate_events => true
    #    codec => "json"
        auto_offset_reset => "latest"
      }
    }
    # filter {}
    output {
      elasticsearch {
        hosts => [ "10.0.0.11:9200","10.0.0.12:9200" ]
        manage_template => false
    #    index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"
        index => "leion-%{+YYYY.MM.dd}"
      }
      stdout { codec => rubydebug }
    }
    ...
```
#### 启动logstash：
```
su - deploy -c '/home/deploy/logstash/logstash-6.3.0/bin/logstash -f /home/deploy/logstash/logstash-6.3.0/config/logstash-input-kafka-output-es.conf --config.reload.automatic'
```
################################################################################

### FAQ：

Q:
A:
