---
title: vscode offline setup remote development environment
date: 2024-08-23T10:22:00.000Z
tags: IDE
References:
  - https://blog.csdn.net/qq_43623902/article/details/136258880
  - https://git-scm.com/download/win
---
# VSCode完全离线搭建远程开发环境，离线安装Git、SSH、vscode-server
## 环境背景

- 时间：2024年8月。
- 客户端：Windows_Server_2016（经试验Windows_Server_2012无法启动pycharm2024.1.6和VSCode1.92.2，这是本文完成时的最新版）。
- 服务端：Linux，X86_64、ARM64 均可。
- 完全离线环境：Windows客户端和Linux服务端均在内网，Windows客户端可以直接访问Linux服务端，两者均无法访问互联网。笔者另有一台电脑可以通过零信任访问这两台内网机器，但对两者均无法直连。
- 用户受限：Windows客户端无 Administrator 管理员权限，即无法执行任何需要管理员权限的动作，比如无法安装全局软件、只能使用便携版软件；无法往Windows文件夹放dll；无法执行需要管理员权限的powershell或bat脚本、当然无法启动具有管理员权限的powershell或cmd。

## 安装 PortableGit

<!-- more -->
https://github.com/git-for-windows/git/releases/download/v2.46.0.windows.1/PortableGit-2.46.0-64-bit.7z.exe

这是一个7z自动解压包，安装至 `C:\PortableGit\`。
SSH 客户端的路径就在 `C:\PortableGit\usr\bin\ssh.exe`。

## 安装 VSCode 及扩展插件

### 安装 VSCodeUserSetup 版本
下载 `VSCodeUserSetup-x64-1.92.2.exe` 并传输到Windows客户端安装。

### 安装扩展插件 Remote - SSH

在 VSCode [marketplace](https://marketplace.visualstudio.com/) 中搜索`Remote - SSH` [Remote - SSH - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)，在 `Version History` 标签页中下载`0.113.2024072315` 版本，也就是`2024/7/23`发布的版本，得到文件 `ms-vscode-remote.remote-ssh-0.113.2024072315.vsix` 保存以备后续在客户端上离线安装。

打开 VSCode 侧边栏“扩展”页面，从VSIX安装，选中插件。
### 配置 Remote - SSH 插件的 SSH 自定义路径

在`VSCode` 中使用快捷键 `Ctl+Shift+P` 打开命令栏，输入 `Preference: Open User Settings (JSON)` ，编辑文本加入以下内容：

> 注意json格式，即注意逗号，注意最外层的花括号只有一个。

```json
{
    // VSCode 自定义 Remote - ssh 插件使用的 SSH 路径
    "remote.SSH.path": "C:\\PortableGit\\usr\\bin\\ssh.exe"
}
```

### VSCode 远程连接 Linux 服务端

#### 方法1：通过 ssh 连接命令连接

在`VSCode` 中使用快捷键 `Ctl+Shift+P` 打开命令栏，输入 `ssh` ，点击 `Remote-SSH: 连接到主机` -> `+ 添加新的ssh主机`，在打开的连接命令窗口中输入命令

```shell
ssh <user>@<hostname>:[port]
```

- user: 是在远程服务器上的用户名
- hostname: 远程服务器的主机名或 IP 地址
- port: SSH 连接的端口号(默认为 22)

输入后按`Enter`键选择要更新的配置文件，一般选择第一个也就是`C:\Users\${你的用户名}\.ssh\config` 。

#### 方法2：通过更新 ssh 配置文件连接

在`VSCode` 中使用快捷键 `Ctl+Shift+P` 打开命令栏，输入 `ssh` ，点击 `Remote-SSH: 打开SSH配置文件`选择要更新的 SSH 配置文件，一般选择第一个也就是`C:\Users\${username}\.ssh\config`，打开后编辑并保存:

```
Host xxx
  HostName xxx.xxx.xxx.xxx
  Port xx
  User xxx
  IdentityFile "xxx"
```

- Host: 这是一个主机别名，你可以使用这个别名来代替实际的主机名进行连接.
- HostName: 这是指定远程主机的 IP 地址或主机名.
- Port: 这是指定 SSH 连接的端口号.
- User: 这是指定用于连接远程主机的用户名.
- IdentityFile: 这是免密登录时指定用于身份验证的私钥文件的路径.

> 如果要配置多个远程连接主机，继续在此文件追加配置即可。

完成后点击 `Remote-SSH: 连接到主机`，此时会出现新配置的远程连接，根据需要选择`在当前窗口连接`或`在新窗口中连接`，此时会让你输入密码，然后会在远程端下载所需文件(需要联网)，如果无法联网，就需要离线下载 vscode-server 并安装。

### 离线下载 vscode-server 并安装至服务端

如果远程端不能联网可以下载包离线安装，下载 vscode-server 的 url 需要和 vscode 客户端版本的 `commit-id` 对应。通过 vscode 面板的`帮助->关于`可以获取该信息，复制信息，我当前版本如下(`Commit` 后面对应的就是 `commit_id`):

```
Version: 1.92.2 (user setup)
Commit: fee1edb8d6d72a0ddff41e5f71a671c23ed924b9
Date: 2024-08-14T17:29:30.058Z
Electron: 30.1.2
ElectronBuildId: 9870757
Chromium: 124.0.6367.243
Node.js: 20.14.0
V8: 12.4.254.20-electron.0
OS: Windows_NT x64 10.0.14393
```

#### 旧版离线包下载【已过时】

vscode-server 下载地址如下，其中 commit_id 是上面复制的提交 id:

```
x86:
https://update.code.visualstudio.com/commit:${commit_id}/server-linux-x64/stable
arm:
https://update.code.visualstudio.com/commit:${commit_id}/server-linux-arm64/stable
```

将下载的文件 `vscode-server-linux-x64.tar.gz` 解压解包后名为 `vscode-server-linux-x64` 文件夹改名为 `${commit_id}` 放在 `/home/${user}/.vscode-server/bin/` 目录下.

#### 新版离线包下载【用这个】

在某次更新后远程端的 .vscode-server 目录结构发生变化:

```
📦.vscode-server
 ┣━ 📁bin  # 存放旧方法下的vscode commit相关文件
 ┃   ┗━ 📁${commit_id1}
 ┃   ┗━ 📁${commit_id2}
 ┃   ┗━ ···
 ┣━ 📁cli  # 存放新方法下的vscode commit相关文件
 ┃   ┗━ 📁servers
 ┃   ┃   ┗━ 📁Stable-${commit_id}
 ┃   ┃   ┃   ┗━ 📁server
 ┃   ┃   ┃   ┗━ ···
 ┃   ┃   ┗━ ···
 ┃   ┗━ 📜lru.json  # 存放最近的vscode commit_id
 ┣━ 📜code-${commit_id}  # 存放vscode_cli_alpine_x64_cli.tar.gz解压后名为code的文件，并将其改名为code-${commit_id}
 ┣━ 📁data
 ┗━ 📁extensions
```

现在需要安装两个文件，两个文件的下载地址如下:

```
x86:
https://vscode.download.prss.microsoft.com/dbazure/download/stable/${commit_id}/vscode-server-linux-x64.tar.gz
https://vscode.download.prss.microsoft.com/dbazure/download/stable/${commit_id}/vscode_cli_alpine_x64_cli.tar.gz

arm:
https://vscode.download.prss.microsoft.com/dbazure/download/stable/${commit_id}/vscode-server-linux-arm64.tar.gz
https://vscode.download.prss.microsoft.com/dbazure/download/stable/${commit_id}/vscode_cli_alpine_arm64_cli.tar.gz
```

第一个文件 `vscode-server-linux-x64.tar.gz` 解压解包后名为 `vscode-server-linux-x64` 文件夹改名为 `server` 放在 `/home/${user}/.vscode-server/cli/servers/Stable-${commit_id}/` 目录。

第二个文件 `vscode_cli_alpine_x64_cli.tar.gz` 解压解包后名为 `code` 的文件改名为 `code-${commit_id}`放在 `/home/${user}/.vscode-server/` 目录。

## Q&A

如果仍然连接不上，则有一些可能原因，修复后再尝试连接。
1. 赋予二进制文件可执行权限：
```bash
chmod +x ~/.vscode-server/code-*
```
2. 需要修改`.vscode-server`文件夹及其子目录的权限，例如权限改为`755`:
```bash
chmod -R 755 ~/.vscode-server/
```

## 参阅

- [Visual Studio Code - Code Editing. Redefined](https://code.visualstudio.com/)
- [Remote - SSH - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)
- [Git - Downloading Package](https://git-scm.com/download/win)
- [vscode 远程 linux(包括离线vscode-server安装，免密登录方法)\_vscode-server-linux-CSDN博客](https://blog.csdn.net/qq_43623902/article/details/136258880)