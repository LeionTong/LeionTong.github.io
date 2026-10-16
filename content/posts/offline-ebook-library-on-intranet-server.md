---
title: "无公网内网服务器上离线部署个人电子书库（Calibre-Web / Kavita / Samba / Nextcloud）"
date: 2026-10-16 02:00:00
slug: "offline-ebook-library-on-intranet-server"
draft: false
---

# 无公网内网服务器上离线部署个人电子书库

场景：一台 **Linux 服务器，无桌面、无公网**，手头有一千本电子书，想把它存下来、能在浏览器里在线读、内网里多台设备（Windows / macOS / 手机）都能取用。

下面把几条可行路线、选型取舍和可直接复制的命令一次写清。核心前提只有一条：**服务器拉不到镜像、也下不了插件，所以要"在有网机器上准备好一切，再搬进内网"**。

## 一、选型对比

优先选 **Docker 离线部署**（无公网也能跑，全程命令行操作，Web 界面访问）；最省事的是 **Samba 纯文件共享**（零 Web，拖放就行）。

| 方案 | 部署难度 | 核心优势 | 无公网适配 | 适合场景 |
| --------------- | ------------ | -------------------------- | ----- | ------------- |
| **Calibre-Web** | ⭐⭐（Docker 离线） | 全功能：在线读 + 分类 + 标签 + 元数据，1000 本无压力 | ✅ 完美 | 存 + 读 + 管理一站式（首选） |
| **Kavita** | ⭐⭐（Docker 离线） | 轻量、界面现代，阅读体验优于 Calibre-Web | ✅ 完美 | 纯阅读 + 轻管理，更流畅 |
| **Samba（SMB）** | ⭐（纯命令行） | 像本地文件夹，拖放即存，无 Web 界面 | ✅ 完美 | 只存不在线读，极简 |
| **Komga** | ⭐⭐（Docker 离线） | 漫画 + 书籍双支持，手动补元数据 | ✅ 完美 | 漫画 + 书籍混合存 |
| NextCloud | ⭐⭐（Docker 离线） | 网盘 + 在线读 + 多用户权限，功能最全 | ✅ 完美 | 要"网盘 + 电子书"一体化 |

> 通用思路：无公网环境走 **有网机器拉镜像 → `docker save` 导出 tar → 传到内网 → `docker load` 导入 → 启动**。书籍同理，用 scp / U 盘 / 内网 Samba 拷贝过去。

## 二、方案 1：Calibre-Web（首选，离线 Docker 部署）

### 核心逻辑

- 无公网：**提前在有网机器拉 Docker 镜像 → 导出 tar 包 → 传到内网服务器 → 导入 → 启动**
- 无桌面：全程命令行操作，Web 界面（内网浏览器）访问 / 管理
- 书籍：通过 Samba / scp 传到服务器目录，容器挂载后自动识别

### 步骤一：有网机器（准备镜像 + 书籍）

```bash
# 拉取 Calibre-Web 镜像（仅需一次）
docker pull linuxserver/calibre-web:latest

# 导出镜像为 tar 包（方便传到内网）
docker save -o calibre-web.tar linuxserver/calibre-web:latest
```

可选：提前把 1000 本书统一放一个文件夹（优先 EPUB / PDF），后续一起传到内网服务器。

### 步骤二：内网服务器（无公网 + 无桌面，命令行操作）

1. 传输文件：把 `calibre-web.tar` 和书籍文件夹，通过 **scp / U 盘 / 内网 Samba** 传到服务器（比如 `/root/` 目录）。

2. 导入 Docker 镜像（无公网核心步骤）：

```bash
docker load -i /root/calibre-web.tar
```

3. 创建书籍 / 配置目录（命令行）：

```bash
# 配置目录（存账号 / 设置）
mkdir -p /data/calibre-web/config
# 书籍目录（存 1000 本书）
mkdir -p /data/calibre-web/books
# 权限（避免容器读写报错；先用 id 命令查看自己的 UID/GID 再替换 1000:1000）
chown -R 1000:1000 /data/calibre-web
```

> 查 UID/GID：执行 `id`，输出 `uid=1000(xxx) gid=1000(xxx)`，把命令里的 `1000:1000` 换掉。

4. 启动 Calibre-Web 容器（`PUID` / `PGID` 替换成上一步查到的值）：

```bash
docker run -d \
  --name=calibre-web \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Asia/Shanghai \
  -p 8083:8083 \
  -v /data/calibre-web/config:/config \
  -v /data/calibre-web/books:/books \
  --restart unless-stopped \
  linuxserver/calibre-web
```

5. 书籍批量导入（两种方式）：

```bash
# 方式 1（命令行）：把整理好的 1000 本书直接复制过去
cp -r /root/你的书籍文件夹/* /data/calibre-web/books/
```

方式 2（Web 端）：内网浏览器打开 `http://服务器IP:8083`，登录后点「上传书籍」批量导入。

6. 初始配置：

- 初始账号 `admin`、密码 `admin123`（登录后立即修改）
- 首次登录：选择「使用现有书库」，路径填 `/books`，自动扫描所有书籍

## 三、方案 2：Kavita（轻量阅读，离线 Docker 部署）

步骤与 Calibre-Web 逻辑一致，仅镜像与端口不同。

### 有网机器

```bash
docker pull kizaing/kavita:latest
docker save -o kavita.tar kizaing/kavita:latest
```

### 内网服务器

```bash
# 导入镜像
docker load -i /root/kavita.tar

# 创建目录（先用 id 查看 UID/GID 再替换 1000:1000）
mkdir -p /data/kavita/config
mkdir -p /data/kavita/books
chown -R 1000:1000 /data/kavita

# 启动容器（Kavita 默认书籍目录为 /manga）
docker run -d \
  --name=kavita \
  -p 5000:5000 \
  -v /data/kavita/config:/kavita/config \
  -v /data/kavita/books:/manga \
  --restart unless-stopped \
  kizaing/kavita
```

访问 `http://服务器IP:5000`，注册账号后扫描 `/manga` 目录即可。

## 四、方案 3：Samba（极简，纯文件共享，无 Web）

适合：只存不在线读，内网多设备（Windows / macOS / 手机）直接拖放。

```bash
# 安装 Samba（内网若有本地源，用本地源；无则提前下载 deb 包离线 dpkg -i 安装）
sudo apt update && sudo apt install samba -y

# 创建书籍共享目录
sudo mkdir -p /data/books
sudo chmod 777 /data/books
sudo chown -R $USER:$USER /data/books

# 编辑配置（命令行用 vim / nano）
sudo nano /etc/samba/smb.conf
```

在文件末尾追加：

```ini
[Books]
   path = /data/books
   browseable = yes
   read only = no
   guest ok = yes  # 允许匿名访问（内网安全，无需密码）
   create mask = 0666
   directory mask = 0777
```

```bash
# 重启并设置开机自启
sudo systemctl restart smbd nmbd
sudo systemctl enable smbd nmbd
```

内网访问：

- Windows：打开「此电脑」，地址栏输入 `\\服务器IP`，直接拖放书籍到 `Books` 文件夹
- Linux / macOS：`smb://服务器IP/Books`
- 手机：用 ES 文件浏览器 / Documents，选 SMB 连接，输入服务器 IP 即可

## 五、方案 4：Nextcloud（网盘 + 电子书一体，离线 Docker 部署）

核心思路：**Docker 离线部署 Nextcloud（用 SQLite 轻量数据库，无需单独搭 MySQL）+ 离线安装 Reader 插件（在线读 EPUB / PDF）+ 内网传书（Samba / scp / U 盘）**，满足「存书 + 在线读 + 内网多设备共享 + 多用户权限」。

### 一、核心准备（有网机器，仅需一次）

```bash
# 拉取官方 Nextcloud 镜像（SQLite 版，无公网首选，无需数据库容器）
docker pull nextcloud:latest

# 导出为 tar 包（传到内网服务器）
docker save -o nextcloud.tar nextcloud:latest
```

下载「Reader」插件（应用商店需公网，提前在有网机器下好）：

- 插件地址：`https://apps.nextcloud.com/apps/reader`
- 下载对应 Nextcloud 版本的 `reader.tar.gz`（比如 Nextcloud 28/29，选最新稳定版）
- 备用：也可下载 `files_reader`（旧版 Reader，兼容性更好）

再把 1000 本书统一放一个文件夹（优先 EPUB / PDF），准备一起传进内网。

### 二、内网服务器部署（无公网 + 无桌面，纯命令行）

```bash
# 传输文件：通过 scp / U 盘 / 内网 Samba，把 nextcloud.tar、reader.tar.gz 和书籍文件夹传到 /root/

# 导入 Docker 镜像
docker load -i /root/nextcloud.tar

# 创建数据目录（书籍、配置、用户数据都在这；先用 id 查 UID/GID 再替换 1000:1000）
mkdir -p /data/nextcloud
chown -R 1000:1000 /data/nextcloud
```

启动 Nextcloud 容器：

```bash
docker run -d \
  --name=nextcloud \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Asia/Shanghai \
  -p 8080:80 \
  -v /data/nextcloud:/var/www/html \
  --restart unless-stopped \
  nextcloud:latest
```

初始化 Nextcloud（内网浏览器操作）：

1. 内网任意设备浏览器打开 `http://服务器IP:8080`
2. 创建**管理员账号**（用户名 / 密码，记好）
3. 数据库选择 **SQLite**（无公网首选，无需配置数据库地址 / 账号）
4. 点击「安装」，等待 1–2 分钟完成初始化（无公网不影响，纯本地安装）

离线安装「Reader」插件（在线读电子书）：

```bash
# 复制插件包到 Nextcloud 的 apps 目录（容器内路径映射到宿主机 /data/nextcloud/apps）
cp /root/reader.tar.gz /data/nextcloud/apps/

# 解压插件包
cd /data/nextcloud/apps/
tar -zxvf reader.tar.gz

# 授权（关键：避免插件无法启用）
chown -R 1000:1000 /data/nextcloud/apps/reader
```

再到 Web 端启用：登录管理员 → 右上角「用户头像」→「应用」→ 找到 Reader（或 Files Reader）→ 点击「启用」。启用后，上传的 EPUB / PDF 可直接在线打开阅读。

批量传书（三种内网方式，任选）：

```bash
# 方式 1（最快）：命令行直接复制到用户目录（admin 替换为你的管理员用户名）
cp -r /root/你的书籍文件夹/* /data/nextcloud/data/admin/files/
```

> 传完后在 Nextcloud Web 端「文件」→ 右上角「⋮」→「重新扫描文件」，书籍立即显示。

方式 2：参照上面的 Samba 配置，把 `/data/nextcloud/data/admin/files/` 设为共享目录，Windows / macOS 直接拖放。

方式 3：Web 端「文件」→「上传」，少量书籍可用（1000 本建议用方式 1 / 2）。

### 三、Nextcloud 存书用法

- **分类管理**：Web 端建文件夹（「小说」「技术」「历史」），拖入对应目录，支持标签、收藏、搜索
- **在线阅读**：点击 EPUB / PDF，自动用 Reader 插件打开，支持翻页、书签、夜间模式
- **多设备访问**：电脑浏览器访问；手机装 Nextcloud App（离线装 APK / IPA）；其他设备可用 SMB / WebDAV 映射为网络驱动器
- **多用户共享**：管理员创建子账号，给不同用户分配目录权限（家人 / 同事分权限访问）

## 六、无公网 + 无桌面避坑

1. **离线元数据**：无公网抓不到封面 / 作者信息，可在 Web 端手动上传封面、编辑元数据；批量编辑用「批量操作」功能。
2. **书籍格式**：优先存 **EPUB**（体积小、在线读体验好），PDF 次之；MOBI / AZW3 在有网机器用 Calibre 转成 EPUB 再传。
3. **存储成本**：1000 本平均 5 MB/本，仅需约 **5 GB** 空间，普通硬盘完全够用；`/data` 目录别放系统盘。
4. **权限避坑**：Docker 容器的 `PUID` / `PGID` 必须和服务器目录所有者一致，否则会出现「无法读取书籍」「无法上传」。
5. **备份**：定期备份 `/data` 下的数据目录（书籍 + 配置 + 用户信息都在里面）。
6. **内网安全**：无需公网映射，仅内网 IP 访问；Samba 可关掉 `guest ok` 并设账号密码（`sudo smbpasswd -a 用户名`）；Nextcloud 管理员密码设复杂。
7. **性能**：1000 本 + SQLite，普通 2 核 4 G 服务器完全流畅，无需额外优化。

## 七、取舍建议

- 要**存 + 在线读 + 管理**：直接选 **Calibre-Web（离线 Docker）**，功能最全，适配 1000 本规模。
- 要**轻量、阅读体验好**：选 **Kavita（离线 Docker）**。
- 完全**不想折腾 Web 界面**：选 **Samba**，拖放即存，零学习成本。
- 需要**网盘 + 电子书 + 多用户权限**一体：选 **Nextcloud**，比 Calibre-Web / Kavita 更全能，适合长期内网使用。

**一句话**：纯存书 + 简单在线读，Calibre-Web 更轻更快；要把「网盘 + 电子书」揉在一起，Nextcloud 才是那口锅。
