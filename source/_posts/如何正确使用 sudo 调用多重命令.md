---
title: 如何正确使用 sudo 调用多重命令
date: 2021-08-20T16:30:00.000Z
tags: linux
---

# 如何正确使用 sudo 调用多重命令

## 问题现状(Problem)
执行命令 ~~`sudo echo xxx > txt`~~ 时 `Permission denied`

```
sudo echo 'some_strings' > test.txt
-bash: test.txt: Permission denied
```
bash 拒绝这么做，说是权限不够.
这是因为重定向符号 `>` 也是 bash 的命令。sudo 只是让 echo 命令具有了 root 权限，
但是没有让 `>` 命令也具有 root 权限，所以 bash 会认为这个命令没有写入信息的权限。

## 解决办法(Solution)
1. 利用 `sh -c` 命令，它可以让 bash 将一个字串作为完整的命令来执行，这样就可以将 sudo 的影响范围扩展到整条命令。
具体用法如下：

```
sudo sh -c "echo 'some_strings' > test.txt"
```

2. 利用管道和 `tee` 命令，该命令可以从标准输入中读取信息并将其同时写入标准输出和文件中，
具体用法如下：

```
echo 'some_strings' | sudo tee test.txt
echo 'some_strings' | sudo tee -a test.txt   // -a 是追加的意思，等同于 >>
```

`tee` 命令很好用，它从管道接收信息，一边向屏幕输出，一边向文件写入。

3. 提升 shell 权限。
`sudo -s  //提到root 权限。提示符为#`
当你觉得该退回到普通权限时：
`sudo su <username>  //退回到 username 权限，提示符为$`
exit 退出当前用户，回到上一层目录.

centos 提升权限: `su -`
ubuntu 提升权限: `sudo -s`，`sudo su`
