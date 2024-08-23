---
title: How to use Hexo and deploy to GitHub Pages
date: 2017-05-17T19:39:26.000Z
tags: hexo
---
# How to use Hexo and deploy to GitHub Pages

- <https://github.com/hexojs/hexo>
- <https://hexo.io/docs/>

## 1. Install Hexo

<!-- more -->
```
$ sudo npm install -g hexo-cli

$ hexo -v
hexo-cli: 1.0.2
os: Linux 4.9.15-x86_64-linode81 linux x64
http_parser: 2.7.0
node: 6.10.2
v8: 5.1.281.98
uv: 1.10.2
zlib: 1.2.7
ares: 1.10.1-DEV
icu: 50.1.2
modules: 48
openssl: 1.0.1e-fips
```

<!-- more --> 

## 2. Create a project for your GitHub Pages

```
$ hexo init LeionTong.github.io

$ cd LeionTong.github.io

$ npm install
```

## 3. Run a test server locally

```
$ hexo server
INFO  Hexo is running at http://localhost:4000 . Press Ctrl+C to stop.
```

## 4. Set information for your new blog

<https://hexo.io/docs/configuration.html>

```sh
$ vi _config.yml

~~~~~~~~~~~~~~~~~~ _config.yml ~~~~~~~~~~~~~~~~~~
# Site
title: Leion-Sky
subtitle:
description: LeionTong's personal blog!
keywords:
author: LeionTong
language: zh-CN
timezone: Asia/Shanghai

...
url: https://LeionTong.github.io/
...
```

## 5. Set information to use Git

https://hexo.io/docs/one-command-deployment

Install [hexo-deployer-git](https://github.com/hexojs/hexo-deployer-git).
```sh
$ npm install hexo-deployer-git --save  
```

Edit **_config.yml** (with example values shown below as comments):
```sh
$ vi _config.yml

~~~~~~~~~~~~~~~~~~ _config.yml ~~~~~~~~~~~~~~~~~~
deploy:
  type: git
  repo: git@github.com:LeionTong/LeionTong.github.io.git
  branch: gh-pages
  message: [message]
```

## 6. Set "watch" before starting your work

"watch" command can monitor your files.<br>
<https://hexo.io/docs/generating.html>

```sh
$ hexo generate --watch
```

## 7. Create a new post file

```sh
$ hexo new first-post
INFO  Created: ~/***/LeionTong.github.io/source/_posts/first-post.md
```

## 8. Edit the above file with Markdown or Hexo's Helper

Hexo's Helper<br>
<https://hexo.io/docs/helpers.html><br>
I use Atom with "shift + control + m" when I use Markdown :-)<br>
<https://atom.io/>

## 9. Delete "source/_posts/hello-world.md"

It's not necessary to deploy.

## 10. Deploy your new blog!!

<https://hexo.io/docs/deployment.html>

```sh
$ hexo clean && hexo deploy
```

After writting the above command, you can see your new blog on GitHub Pages.<br>
<http://******.github.io/>

## 11. Change your blog theme

<https://github.com/hexojs/hexo/wiki/Themes>

For instance, How to use the following theme.
https://hexo.io/hexo-theme-light/ or maybe https://github.com/theme-next/hexo-theme-next ?

```sh
## If you're using Hexo 5.0 or later, the simplest way to install is through npm:
$ cd LeionTong.github.io
$ npm install hexo-theme-next

## Or you can clone the entire repository:
$ cd LeionTong.github.io
$ git clone https://github.com/next-theme/hexo-theme-next themes/next

## Set information to use the theme
$ cd LeionTong.github.io
$ vi _config.yml

~~~~~~~~~~~~~~~~~~ _config.yml ~~~~~~~~~~~~~~~~~~
theme: next
```

## 12. Create a new page file

<https://hexo.io/docs/writing.html>

```
$ hexo new page aboutme
INFO  Created: ~/***/LeionTong.github.io/source/aboutme/index.md
```

## Q&A

Q：运行 hexo 提示 "/usr/bin/env: node: 没有那个文件或目录"

A：由于 Ubuntu 下已经有一个名叫 node 的库，因此 Node.js 在 ubuntu 下默认叫 nodejs ，创建软链接：

```
sudo ln -s`which nodejs` /usr/bin/node
```

Q: 如果要将源码上传至Github，或者GitLab等云平台，.gitignore怎么写？

A: .gitignore代码：

```
# .DS_Store
# Thumbs.db
# db.json
# *.log
# node_modules/
# public/
# .deploy*/
## 上面是Hexo自带的gitignore内容，我注释掉了，换成了我自己的。
## 我这里只需要备份source文件夹下的Markdown笔记和配置信息。
## 另外，我自定义的NexT主题配置项也在NexT官方指导下合并到了Hexo的_config.yml文件里。
## 所以也不需要备份themes文件夹，如果主题改动较大建议将themes那两行取消注释。
## 注意：这里采用排除法，先忽略所有文件，然后再排除，这样就只留下了自己需要git版本控制的文件(夹)。
*
!/source/
!/source/**/*
#!/themes/
#!/themes/**/*
!/_config.yml
!/.gitignore
!/README.md
```

Q：Github Pages要想自定义域名怎么办？

在 source 目录下新建 CNAME 文本文件，写入购买的域名，然后在域名供应商管理后台配置好域名解析记录。

Q：怎么创建软链接？
使用 WSL，MobaXterm，GitforWindows 等 terminal 工具。
```sh
ln -sv "/mnt/c/Users/leion/OneDrive/Obsidian Vault/H.exo/source" "/mnt/c/Users/leion/Documents/Tong-Workspaces/Git/Hexo-Blog/source"
```

Q：WSL-Ubuntu安装 npm 和 hexo 后启动 `hexo s` 报错：vbnet
`TypeError: Object.fromEntries is not a function`
`
> https://hexo.io/zh-cn/docs/#Node-js-版本限制
> https://blog.csdn.net/LizequaNNN/article/details/122369122

nodejs版本太低。升级node：
```sh
leion@DELL-XPS-WIN:/drives/c/Users/leion/Downloads/he$ node --version
v10.19.0
leion@DELL-XPS-WIN:/drives/c/Users/leion/Downloads/he$ sudo npm install -g n
/usr/local/bin/n -> /usr/local/lib/node_modules/n/bin/n
+ n@9.0.0
added 1 package from 2 contributors in 0.18s
leion@DELL-XPS-WIN:/drives/c/Users/leion/Downloads/he$ sudo n stable
  installing : node-v16.17.1
       mkdir : /usr/local/n/versions/node/16.17.1
       fetch : https://nodejs.org/dist/v16.17.1/node-v16.17.1-linux-x64.tar.xz
     copying : node/16.17.1
   installed : v16.17.1 (with npm 8.15.0)

Note: the node command changed location and the old location may be remembered in your current shell.
         old : /usr/bin/node
         new : /usr/local/bin/node
If "node --version" shows the old version then start a new shell, or reset the location hash with:
hash -r  (for bash, zsh, ash, dash, and ksh)
rehash   (for csh and tcsh)
leion@DELL-XPS-WIN:/drives/c/Users/leion/Downloads/he$ hash -r
leion@DELL-XPS-WIN:/drives/c/Users/leion/Downloads/he$ node -v
v16.17.1
```
