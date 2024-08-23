---
title: common Hexo post Steps
date: 1970-01-01T00:00:00.000Z
tags: hexo
---

# common Hexo post Steps:

## Server preview:
hexo clean && hexo g && hexo server

## Deploy to Gh-pages:
hexo clean && hexo g -d && hexo clean


# Hexo insert images into Mardown
Hexo 向 Mardown 中插入图片

> Refer: https://zhuanlan.zhihu.com/p/265077468
<!-- more -->
## 安装插件

```shell
npm install hexo-renderer-marked
```

## 修改配置：
```shell
vim _config.yaml
```

```yaml
...
post_asset_folder: true
marked:
  prependRoot: true
  postAsset: true
...
```

## 编辑 Mardown 

1. 图片文件名不能存在特殊字符，文件名中的空格最好用下划线或横杠代替。
2. 所有图片需放到与 Mardown 同名的文件夹下，然后引用。
3. 使用 `hexo deploy` 发布之前需要确保引用时不加路径，因为发布后由该 Mardown 生成的 `index.html`和图片位于同一目录下。

两种最佳实践：

1. 使用 typora 编辑 Mardown：
偏好设置 -> 图像 -> 插入图片时：

	"复制到指定路径" 选择 "./$(filename)"
	勾选：对本地位置的图片应用上述规则
	勾选：对网络位置的图片应用上述规则
	勾选：优先使用相对路径
这样，在插入图片时 typora 会在 Mardown 文件当前目录下自动新建同名的文件夹。
编辑完成后，再将引用的相对路径全部替换为空。
然后再发布。

2. 使用 obsidian 编辑 Mardown：
设置 -> 文件与链接：

	内部链接类型："以尽可能简短的形式插入"
	新附件的默认位置：当前文件夹下指定的子文件夹中
	子文件夹名称：assets
这样，在插入图片时 obsidian 会在 Mardown 文件当前目录下自动新建名为 `assets` 的文件夹。
编辑完成后，再将之前定义的 `assets` 的文件夹改名为 Mardown 文件同名的文件夹。
然后再发布。

