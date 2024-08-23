# Git清理删除历史提交文件

##### 1.垃圾回收

先进行垃圾回收，并压缩一些文件

```bash
$ git gc --prune=now
```

Git最初向磁盘中存储对象使用`松散`的格式，后续会将多个对象打包为一个二进制的`包文件`（`packfile`），以`节省磁盘空间`

`.pack`文件存储了`对象的内容`

`.idx`文件存储了`包文件`的`偏移信息`，用于`索引具体的对象

打包对象时，查找命名和大小相近的文件，保留文件`不同版本之间的差异`（`最新一版保存完整内容`，访问频率最高）

##### 2.查找大文件
<!-- more -->

使用`git rev-list --objects —all`显示`所有commit及其所关联的所有对象`：

```bash
$ git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -3 | awk '{print$1}')"

e9461c55c3b8807351909cf7bb46eb22a8df5533 README.md
b866711af76e7d7cc87d9828f8ddde8ea865d053 bigqin
8d675f2ad83219ad4ebe34fe4dcac3a7139002ea bigqin
```

`verify-pack -v *.idx`：查看压缩包内容

##### 3.删除指定的大文件

```bash
$ git filter-branch --force --index-filter "git rm -rf --cached --ignore-unmatch bigqin" --prune-empty --tag-name-filter cat -- --all
Rewrite bf551acd0ca40a5671bcf2d4cad83a999b8baf52 (10/16) (0 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite d1d31551ecb36d362fd1051152f1fc886e4df95c (11/16) (0 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite da902adff9f3f890aa4c3304c5ac6d1e14f589da (12/16) (0 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite c96090316c3600e6e190cb9f99cf14a58f6f09ca (13/16) (0 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite 9d6c9194d76c5e0aa6c9119445681c9fbdf735a3 (14/16) (1 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite b1e2f243a559547e3a0f5eaa18f6a31a35eaa57a (14/16) (1 seconds passed, remaining 0 predicted)    rm 'bigqin'
Rewrite ac49fbb891648b73bbd31b4e82b56bbd71254384 (14/16) (1 seconds passed, remaining 0 predicted)    rm 'bigqin'
.....
```

`filter-branch` 命令通过一个filter来重写历史提交，这个filter针对指定的所有分支(`rev-list`)运行。

`--index-filter`：过滤Git仓库的index，该过滤命令作用于`git rm -rf --cached --ignore-unmatch bigqin`。不`checkout`到`working directory`，只修改`index`的文件，速度快。

`--cached`会删除index中的文件

`--ignore-unmatch`：如果没匹配到文件，不会报错，会继续执行命令

最后一个参数`file/directory`是要被删除的文件的名字

`--prune-empty`：指示`git filter-branch` 完全删除所有的空commit。

`-–tag-name-filter`：将每个tag指向重写后的commit。

`cat`命令会在收到tag时返回tag名称

`–-`选项用来分割 rev-list 和 filter-branch 选项

`--all`参数告诉Git我们需要重写所有分支（或引用）。

> 注意：git rm 这一行命令使用双引号`"git rm -rf --cached --ignore-unmatch bigqin"`

##### 4.删除缓存

移除本地仓库中指向旧提交的剩余refs，`git for-each-ref` 会打印仓库中匹配`refs/original`的所有refs，并使用`delete`作为前缀，此命令通过管道传送到 `git update-ref` 命令，该命令会移除所有指向旧commit的引用。

```bash
$ git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
```

以下命令会使reflog到期，因为它依然包含着对旧commit的引用。使用`--expire=now` 参数，确保它在目前为止到期了。如果没有该参数，只会移除超过90天的reflog。

```bash
$ git reflog expire --expire=now --all
```

现在本地仓库依然包含着所有旧commit的对象，但已经没有引用指向它们了，这些对象需要被删除掉。此时可以使用 `git gc` 命令，Git的垃圾回收器会删除这些没有引用指向的对象。

```bash
$ git gc --prune=now
```

`gc`使用`--prune` 参数来清理特定时期的对象，默认情况下为2周，指定`now`将删除所有这些对象而没有时期限制。

```bash
$ du -sh .git
104K    .git
```

此时，.git文件的大小只有104k了。

#### 7.提交重写的历史到远程

如果确认所做的删除大文件操作没有问题，就可以提交到远程仓库了，一旦提交，再也没有办法恢复到原来的状态，一定要小心谨慎！一定要小心谨慎！一定要小心谨慎！

先进行备份工作，以免出现问题：

```bash
$ cd ~/Desktop/
$ mkdir gitthin_mirror && cd gitthin_mirror
$ git clone --mirror git@gitee.com:coderhony/gitthin.git
```

再回到刚才做的已经瘦身的Git仓库

```bash
$ cd ~/Desktop/gitthin/gitthin
```

把已瘦身的仓库同步到远程仓库，使用`—mirror`参数：

```bash
$ git push --mirror git@gitee.com:coderhony/gitthin.git
```

为了确保都已同步，再执行以下命令：

```bash
$ git push --all --force
Everything up-to-date
$ git push --tags --force
Everything up-to-date
```

#### 8.更新其他的clone

在过滤存储库，并重写提交历史后，将更改强制推送到远程服务器之后。现在要更新该存储库的每一份clone，仅靠常用的`pull`是无法做到这一点的。

第一步是从远程服务器获取存储库，使用`git reset` 将存储库从 `origin/master` 切换到旧存储库状态。

```bash
$ git fetch origin
$ git reset --hard origin/master
```

和上面的一样，需要删除旧提交，清理本地仓库

```bash
$ git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
$ git reflog expire --expire=now --all
$ git gc --prune=now
```


- Article: https://www.jianshu.com/p/7ace3767986a