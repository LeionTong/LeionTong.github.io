---
title: Run OP-TEE from scratch
date: 2021-08-24T15:33:00.000Z
tags: TEE
---

# Run OP-TEE from scratch
OP-TEE的编译及运行 

Reference_&_Useful_URL: 
https://www.op-tee.org/
https://github.com/OP-TEE
https://optee.readthedocs.io
https://blog.csdn.net/thanksgining/article/details/108848825
https://blog.csdn.net/zhuyong006/article/details/85282624

## 宿主环境
- OS: Ubuntu 20.04 LTS Desktop
- Disk_Size: 50GB

## Get and build the solution
> Refer：https://optee.readthedocs.io/en/latest/building/gits/build.html#get-and-build-the-solution

 ### 前置条件(Prerequisites)
 
 > Refer：https://optee.readthedocs.io/en/latest/building/prerequisites.html#prerequisites
 
 Ubuntu-based distributions
 
First enable installation of i386 architecture packages and update the package managers database.
```
$ sudo dpkg --add-architecture i386
$ sudo apt-get update
```

Install the following packages regardless of what target you will use in the end.
```
$ sudo apt-get install android-tools-adb android-tools-fastboot autoconf \
        automake bc bison build-essential ccache cscope curl device-tree-compiler \
        expect flex ftp-upload gdisk iasl libattr1-dev libcap-dev \
        libfdt-dev libftdi-dev libglib2.0-dev libgmp-dev libhidapi-dev \
        libmpc-dev libncurses5-dev libpixman-1-dev libssl-dev libtool make \
        mtools netcat ninja-build python-crypto python3-crypto python-pyelftools \
        python3-pycryptodome python3-pyelftools python-serial python3-serial \
        rsync unzip uuid-dev xdg-utils xterm xz-utils zlib1g-dev
```

### Git 配置
```
sudo apt install git -y
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### 安装repo
> Refer：https://mirrors.tuna.tsinghua.edu.cn/help/git-repo/

```
curl https://mirrors.tuna.tsinghua.edu.cn/git/git-repo -o repo
chmod +x repo

sudo mv repo /usr/local/bin/

cat >> ~/.bashrc << "EOF"
export REPO_URL='https://mirrors.tuna.tsinghua.edu.cn/git/git-repo'
EOF

> 并重启终端模拟器。
```

### 获取OP-TEE源代码
> Refer：https://optee.readthedocs.io/en/latest/building/gits/build.html#get-and-build-the-solution

```
mkdir -p optee-project
cd optee-project
repo init -u git://github.com/OP-TEE/manifest.git -m qemu_v8.xml --repo-url=https://mirrors.tuna.tsinghua.edu.cn/git/git-repo -b 3.8.0
repo sync -j4
```

由于github仓库网络问题，中间多次重新同步，还辅助以`proxychains`工具代理外网。
最终，同步了20+GB的数据回来。
![](Spectacle_20210820_171532.png)
![](Spectacle_20210820_172232.png)
![](Spectacle_20210820_172453.png)

### 获取工具链(toolchain)
```
cd optee-project/build
make -j2 toolchains
```

查看 toolchain.mk 文件可知，执行 make 指令之后，系统会去下载 toolchains 的tar包，包括32位和64位的编译链接工具，下载完成后会进行解压操作。

如果执行 make 指令后，一直卡在“Downloading xxx ...”那。

手动到[https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads)下载指定toolchain（toolchain.mk指定了AARCH32_GCC_VERSION和AARCH64_GCC_VERSION）。

这里下载的是[gcc-arm-8.3-2019.03-x86_64-arm-linux-gnueabihf.tar.xz](https://developer.arm.com/-/media/Files/downloads/gnu-a/8.3-2019.03/binrel/gcc-arm-8.3-2019.03-x86_64-arm-linux-gnueabihf.tar.xz?revision=e09a1c45-0ed3-4a8e-b06b-db3978fd8d56&la=en&hash=93ED4444B8B3A812B893373B490B90BBB28FD2E3)和[gcc-arm-8.3-2019.03-x86_64-aarch64-linux-gnu.tar.xz](https://developer.arm.com/-/media/Files/downloads/gnu-a/8.3-2019.03/binrel/gcc-arm-8.3-2019.03-x86_64-aarch64-linux-gnu.tar.xz?revision=2e88a73f-d233-4f96-b1f4-d8b36e9bb0b9&la=en&hash=167687FADA00B73D20EED2A67D0939A197504ACD)

将下载的toolchain的tar包放到op-tee源代码的根目录下的toolchains目录，并进行解压：
```
tar xf gcc-arm-8.3-2019.03-x86_64-arm-linux-gnueabihf.tar.xz -C aarch32 --strip-components=1
tar xf gcc-arm-8.3-2019.03-x86_64-aarch64-linux-gnu.tar.xz -C aarch64 --strip-components=1
```

### 编译(Build the solution)

```
cd optee-project/build
make -j `nproc`
#或者将上述命令写完整些:
make -j `nproc` -f qemu_v8.mk all
```
编译完成：
![](Spectacle_20210824_111244.png)

如果编译有问题，可以通过管道将日志导入文件，方便排查（查找 `ERROR` 字符串）：
```
make -j `nproc` 2>&1 | tee build.log
```

> 注：
> 1. 如果 Make 命令运行时没有指定目标，默认会执行 Makefile 文件的第一个目标。
> 2. Makefile 文件在 repo 初始化时自动生成，且指向 qemu_v8.mk，因此本例中可只需执行 make 命令：
![](Spectacle_20210824_100156.png)

### 启动设备
> Refer：https://optee.readthedocs.io/en/latest/building/devices/qemu.html#qemu-v8

```
cd optee-project/build
make run-only
```
查看 qemu_v8.mk 文件如下代码块可知，由于运行 `make run` 会强制执行 `make all` ，如果没有更新过仓库且只需要单纯启动设备而不需要更新文件系统可以通过执行 `make run-only` 略过从头再编译一遍的过程。
```
.PHONY: run
# This target enforces updating root fs etc
run: all
	$(MAKE) run-only
```

#### Terminal: qemu
![](Screenshot-2021-08-24-11-22-12.png)
#### Terminal: Normal World
![](Screenshot-2021-08-24-11-22-24.png)
#### Terminal: Secure World
![](Screenshot-2021-08-24-11-22-28.png)

## 继续运行
在 qemu 的终端 Terminal 里输入 `c`（小写）然后按 `<Enter>` 键，让系统继续运行。

#### Terminal: qemu
![](Screenshot-2021-08-24-11-37-48.png)
#### Terminal: Normal World
![](Screenshot-2021-08-24-11-37-56.png)
#### Terminal: Secure World
![](Screenshot-2021-08-24-11-38-03.png)

### 执行测试(Run xtest)
> https://optee.readthedocs.io/en/latest/building/gits/build.html#step-9-run-xtest

```
xtest
```

If there are no regressions / issues found, xtest should end with something like this:
```
...
+-----------------------------------------------------
24537 subtests of which 0 failed
96 test cases of which 0 failed
0 test case was skipped
TEE test application done!
```
![](Screenshot-2021-08-24-14-41-11.png)

至此，完成。

## TODO
### Tips and Tricks - Reference existing project to speed up repo sync
> https://optee.readthedocs.io/en/latest/building/gits/build.html#reference-existing-project-to-speed-up-repo-sync

## Q&A：
### `repo sync` 获取源代码时遇到网络问题
```
error: Cannot fetch linaro-swg/linux.git from https://github.com/linaro-swg/linux.git  
Fetching:   7% (1/13), done in 4m19.092s  
Garbage collecting: 100% (13/13), done in 0.089s  
Fetching: 100% (13/13), done in 2h21m29.800s  
Garbage collecting: 100% (13/13), done in 0.221s  
  
error: Exited sync due to fetch errors.  
Local checkouts *not* updated. Resolve network issues & retry.  
`repo sync -l` will update some local checkouts.
```

解决方法：
- 使用代理
或者：
- 使用[从 URL 导入 - Gitee.com](https://gitee.com/projects/import/url)
问题是仓库 https://github.com/linaro-swg/linux.git 太大无法导入。
- 部分仓库已有前人在2021年1月份时同步过了，可以借用（未验证，也不清楚是否过时）：https://gitee.com/fastsource/projects

### `make` 编译过程的 buildroot 阶段由于网络问题下载 patchelf 失败
![](Spectacle_20210823_162552.png)
在别处下载好后放到 `optee-project/buildroot/dl/patchelf` 目录下。因为可能遇到多个包下载失败的问题这里可以单独执行 `make buildroot` 编译此部分以节省时间，等此部分编译通过后再执行一遍 `make` 命令。
该阶段其他包如果下载失败也可同理解决。

### `make run` 启动两个终端报错，找不到可执行文件 `soc_term`
报错信息如下：
```
Error: Failed to execute child process “optee-project/build/../soc_term/soc_term” (No such file or directory)
```

原因是 `make all` 过程出现问题，没有编译出来 soc_term ，重新执行编译操作：
```
cd optee-project/build
make soc-term
```
或者手动进入`soc_term`文件夹进行编译：
```
cd optee-project/build/soc_term/
make
```
然而，一般情况下肯定是编译到 soc_term 之前就出错了，所以才没有继续编译 soc_term，此时最好根据终端输出往上查错。


