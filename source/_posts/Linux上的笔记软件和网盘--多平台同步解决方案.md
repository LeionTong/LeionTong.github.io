---
title: Linux上的笔记软件和网盘--多平台同步解决方案
date: 2018-08-16 16:22:01
tags: Linux
---

# Linux上的笔记软件和网盘--多平台同步解决方案

## 支持云同步的笔记客户端

### nixnote2

Nixnote2是evernote的第三方客户端通过API接口实现同步，不会占用免费用户的同步设备数量。

### wiznote

为知笔记，优良的跨平台笔记软件，支持多级目录和多标签，以及markdown，试用100天。

### 有道云笔记 YNote
<!-- more -->

官方不支持Linux操作系统，Linux上只能使用第三方通过Electron封装版或者网页版。

### Simplenote

很有前途的一个软件，支持多平台同步，问题是国内同步速度太慢，导致容易弄乱笔记。

### Joplin

Joplin - 跨平台开源免费 Markdown 笔记应用，配合NextCloud、WebDAV食用效果更佳。

Joplin 的特色：  
全(跨)平台支持，提供了桌面版、手机移动版以及命令行版客户端  
网页剪藏插件 (支持 Chrome 和 FireFox)  
支持端到端加密 (End To End Encryption / E2EE)  
可完全离线使用，不上传任何数据  


也可搭配各种主流网盘同步，比如 OneDrive、NextCloud、Dropbox,、WebDAV 等  
支持导入印象笔记的 .enex 备份文件，支持导入 Markdown 文档  
可以导出：JEX （Joplin 导出格式）备份，或 MD、TXT、PDF、JASON 等格式  
支持记录笔记、待办事项，支持使用标签和笔记本进行整理  
支持中文全文搜索  
支持 Markdown 语法，可以显示出图片和排版  
支持插入附件  
支持使用外置编辑器打开和修改笔记

### GitNote

国人开发，基于Git，支持同步至Github。

## 本地编辑器

- atom typora neovim oni

[https://atom.io/](https://atom.io/)

[https://typora.io/](https://typora.io/)

[https://neovim.io/](https://neovim.io/)

[https://github.com/onivim/oni](https://github.com/onivim/oni)

### Qownnotes:

[https://www.qownnotes.org/](https://www.qownnotes.org/)

支持API同步至OwnCloud、NextCloud。

- [x] 启用深色系统图标与托盘图标
- [x] 显示系统托盘图标
- [x] 强制系统图标主题

### VNote:

[https://tamlok.github.io/vnote/zh_cn/](https://tamlok.github.io/vnote/zh_cn/)

[https://github.com/tamlok/vnote/blob/master/README_zh.md](https://github.com/tamlok/vnote/blob/master/README_zh.md)

## 网盘：

- NutStore  
    坚果云，全平台同步，速度快，按流量限制，支持WebDAV。

- MEGAsync  
    [mega.nz](http://mega.nz)，国外的网盘，免费容量50g，速度还可以。

- OneDrive  
    微软Win10自带，免费用户默认5G空间，同步速度很快，网页版打开速度有点儿慢，Windows、安卓、iOS有客户端。

- Nextcloud  
    [Providers – Nextcloud](https://nextcloud.com/providers/)


## More ...

https://wiki.archlinux.org/index.php/List\_of\_applications_(简体中文)#笔记

## 基于云的解决方案，本地编辑，云端存储

atom + 各种markdown插件 + hexo + github pages

vimwiki + Github/Gitee 私有仓库

typora + Gitbook

boostnote

turtl
