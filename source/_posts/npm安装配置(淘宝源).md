---
title: npm安装配置(淘宝源)
date: 2020-05-17T19:39:26.000Z
tags: Coding
---

# npm安装：
官网下载nodejs安装包并安装：https://nodejs.org。nodejs自带npm，实际上npm是nodejs的包管理器。

# npm配置：
> https://npmmirror.com/

## 使用说明

你可以使用我们定制的 [cnpm](https://github.com/cnpm/cnpm) (gzip 压缩支持) 命令行工具代替默认的 `npm`:

```bash
$ npm install -g cnpm --registry=https://registry.npmmirror.com
```

或者你直接通过添加 `npm` 参数 `alias` 一个新命令:

<!-- more -->
```bash
alias cnpm="npm --registry=https://registry.npmmirror.com \
--cache=$HOME/.npm/.cache/cnpm \
--disturl=https://npmmirror.com/mirrors/node \
--userconfig=$HOME/.cnpmrc"

# Or alias it in .bashrc or .zshrc
$ echo '\n#alias for cnpm\nalias cnpm="npm --registry=https://registry.npmmirror.com \
  --cache=$HOME/.npm/.cache/cnpm \
  --disturl=https://npmmirror.com/mirrors/node \
  --userconfig=$HOME/.cnpmrc"' >> ~/.zshrc && source ~/.zshrc
```

### 安装模块

```bash
$ cnpm install [name]
```

### 同步模块

直接通过 `sync` 命令马上同步一个模块, 只有 `cnpm` 命令行才有此功能:

```bash
$ cnpm sync express
```

当然, 你可以直接通过 web 方式来同步: [/sync/express](https://npmmirror.com/sync/express)

```bash
$ open https://npmmirror.com/sync/express
```

### 其它命令

支持 `npm` 除了 `publish` 之外的所有命令, 如:

```bash
$ cnpm info express
```

