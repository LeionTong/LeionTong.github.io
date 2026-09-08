# Leion'Log 重装系统 · 本地开发环境备份与恢复清单

> 适用对象：`LeionTong.github.io-hugo`（Hugo + PaperMod，GitHub Pages 自动部署）
> 目标：重装 Windows 后，能在干净机器上**本地构建 + 预览**本站，并恢复每日栏目的发布能力。
> 配套脚本：`scripts/backup-site-env.sh`（可脚本化预检与备份）

---

## 0. 关键结论（先看这三条）

1. **重装前第一要务：把所有未提交改动推上 GitHub。**
   当前仓库有 **68 个已修改文件 + 1 个完全未跟踪文件**（`scripts/reskin_eink.py`）。
   这些是本地产物（含 `static/daily-ai/*.html` 栏目内容），**不入库就会随磁盘清空永久丢失**。
   执行：`git add -A && git commit -m "pre-reinstall" && git push origin master`。
2. **没有 SSH 密钥就 clone/push 不了**（远程是 `git@github.com:...`，SSH 协议）。
   `~/.ssh` 必须在重装前加密备份，并在新机恢复后加入 GitHub 账户。
3. **Hugo 必须装 "extended" 0.164.0 版**，装成 standard 会因 PaperMod 的 SCSS 直接构建失败。
   当前 Hugo 是 WorkBuddy 托管二进制，重装后路径消失——需独立安装（见 §4 / §7）。

---

## 1. 站点现状快照（已实测）

| 项 | 值 |
|---|---|
| 构建工具 | CI/文档钉 **Hugo extended 0.164.0**；**实测本机当前为 v0.165.0 extended**（略新，本地可构建）。恢复建议严格装 0.164.0 以与部署完全一致 |
| 主题 | PaperMod，**已 vendored**（`themes/PaperMod/`，125 个文件入库，**非 submodule**，无嵌套 `.git`） |
| 远程 | `git@github.com:LeionTong/LeionTong.github.io.git`（SSH）；分支 `master`(源) / `gh-pages`(部署) |
| 部署 | 推送 `master` → GitHub Actions 构建 → 强推 `gh-pages` |
| 外部依赖 | **无** `go.mod` / `package.json` / `requirements.txt`；发布脚本纯 Python 标准库 |
| 所需运行时 | Git、Python 3.8+、Hugo extended；**不需要 Node/npm** |
| 脚本 | `scripts/publish_daily_ai.py`、`publish_daily_github.py`、`reskin_eink.py` + `eink-base.css`、`da_cards.css` |
| 密钥情况 | 仓库内**无真实密钥**（GA ID / Search Console 标签均为公开标识）；`GITHUB_TOKEN` 由 Actions 注入 |

---

## 2. 重装前备份清单

| # | 备份内容 | 位置 | 适合方式 | 入库? | 优先级 |
|---|---|---|---|---|---|
| 1 | 项目源码 + 内容 + 脚本 + 主题 | 整个仓库 | **GitHub 远端**（commit + push） | ✅ 是 | P0 |
| 2 | 未提交/未跟踪的本地改动 | 工作区 | 先 commit+push；或单独归档 | 视情况 | P0 |
| 3 | Git 全局配置（user/email 等） | `~/.gitconfig` | 导出文本（脚本 `--backup-config`） | 否(可重设) | P1 |
| 4 | **SSH 私钥 + 配置** | `~/.ssh` | **加密 7z（AES）→ 离线/加密存储** | ❌ **绝不可入库** | P0 |
| 5 | Hugo 版本钉记 + 安装命令 | 文档/脚本 | 写进 `versions.env`（脚本生成） | 否 | P1 |
| 6 | 发布脚本（Python） | `scripts/*.py` | 随仓库（#1 已覆盖） | ✅ 是 | P0 |
| 7 | WorkBuddy 自动化任务（每日栏目生成） | WorkBuddy 配置 | 见 §5.7（需手动/导出） | 否 | P2 |
| 8 | 网络/代理配置（Clash/VPN/Proxifier） | 各 App 配置 | 各 App 自带备份或手动 | 否 | P3 |
| 9 | 编辑器/终端 dotfiles（可选） | `~/.bashrc` 等 | dotfiles 仓库 | 否 | P3 |
| 10 | 构建产物 `public/`、`resources/` | 本地 | **无需备份**（可 `hugo` 重建） | 否(已忽略) | — |

> **本地"数据库/内容数据"说明**：Hugo 是静态站点，**没有数据库**。所有内容即文件——`content/`（Markdown）与 `static/`（含 `daily-ai/*.html` 等）。这些已在 #1 的仓库中；唯一风险是它们有**未提交的本地改动**（见 #2）。

### 快速执行（脚本化）
```bash
cd LeionTong.github.io-hugo
bash scripts/backup-site-env.sh --check          # 只读预检，列出所有风险点
bash scripts/backup-site-env.sh --commit-push    # 交互确认后提交+推送（P0）
bash scripts/backup-site-env.sh --backup-config  # 导出 git 配置 + versions.env
bash scripts/backup-site-env.sh --backup-ssh /e/site-ssh-backup.7z  # 加密 SSH
```

---

## 3. 纳入版本控制 vs 必须排除

### ✅ 应纳入版本控制（repo 即备份）
- `hugo.toml` —— 站点与主题配置
- `content/`、`static/`（头像、栏目 HTML）、`data/`、`i18n/`、`archetypes/`
- `layouts/`（**含 `layouts/partials/google_analytics.html`**——自定义覆盖，缺它会丢 GA/og 标签，**必须入库**）
- `themes/PaperMod/`（vendored，随仓库）
- `assets/`（若有）
- `scripts/*.py` + `scripts/*.css`（发布/样式基线）
- `.github/workflows/hugo-deploy.yml`
- `README.md`、`.gitignore`、本清单 `BACKUP-RECOVERY.md`

### ❌ 必须排除（已在 `.gitignore`，保持即可）
```
/public/          # 构建产物，Actions 生成
/resources/       # Hugo 资源缓存（_gen）
/hugo_stats.json
.hugo_build.lock
.netlify/
.DS_Store  Thumbs.db  desktop.ini
.idea/  .vscode/  *.swp
__pycache__/
```
> 建议补一条：`.hugo_cache/`（非 module 站点一般不生成，留作安全网）。

### 🚫 绝对禁止提交
- 任何 SSH 私钥（`id_rsa`/`id_ed25519` 等）、`.env` 含密钥、API token、密码。
- 当前仓库已扫描确认**无真实密钥**；保持这条铁律即可。

---

## 4. 重装后恢复顺序（及每步验证）

> 顺序即依赖：先基础工具 → 再凭证 → 再源码 → 最后构建验证。

### 步骤 1 · 安装基础工具
- 安装 **Git for Windows**（带 Git Bash）。验证：`git --version`。
- 安装 **Python 3.8+**（发布脚本用）。验证：`python --version`。
- 安装 **Hugo extended 0.164.0**（任选其一）：
  ```bash
  winget install Hugo.Hugo.Extended --version 0.164.0
  # 或便携版（离线优先）：下 hugo_extended_0.164.0_windows-amd64.zip 解压到 PATH
  ```
  验证：`hugo version` 必须含 `extended`。
  > 注：实测本机当前为 **0.165.0 extended**（比 CI 钉的 0.164.0 略新）。恢复时建议严格装 **0.164.0** 以与 GitHub Actions / 生产构建完全一致；若临时用 0.165.0 也能构建，但部署以 CI 的 0.164.0 为准。

### 步骤 2 · 恢复 SSH 凭证（关键）
- 把 §2.#4 的加密 7z 拷回新机，解压到 `~/.ssh`，`chmod 600` 私钥。
- （或重新生成密钥并加入 GitHub 账户。）
- 验证：`ssh -T git@github.com` 返回欢迎语、无权限错误。

### 步骤 3 · 恢复 Git 全局配置
- `git config --global user.name "..."` / `user.email "..."`
- （或把 `versions.env` 旁的 `git-config.txt` 逐项设回。）

### 步骤 4 · 拉取源码
```bash
git clone git@github.com:LeionTong/LeionTong.github.io.git
# 注意：clone 默认目录为 LeionTong.github.io；若沿用旧名：
#   git clone git@github.com:LeionTong/LeionTong.github.io.git LeionTong.github.io-hugo
cd LeionTong.github.io-hugo
```
- 验证：`git status` 干净；`git log --oneline -3` 可见最近提交。

### 步骤 5 · 本地构建 + 预览验证（核心验收）
```bash
hugo server --bind 127.0.0.1 -p 1313     # 本地预览
# 另开终端：
hugo --gc --minify                        # 生产构建
```
- 验证清单：
  - [ ] `hugo version` = v0.164.0 **extended**
  - [ ] `hugo server` 启动无报错，访问 `http://localhost:1313`
  - [ ] 首页 profile 正常；顶部菜单含 **Posts / Daily AI / Daily Github / Archive / Search / Tags**
  - [ ] `/daily-ai/` 与 `/daily-github/` 索引页**有卡片**（非空白）
  - [ ] 搜索页可打开
  - [ ] `hugo --gc --minify` 退出码 0，`public/index.html`、`public/daily-ai/index.html` 存在
  - [ ] 生产构建产物含 GA 标签：爬 `public/index.html` 见 `G-43PK5HWLDX`
- 发布脚本验证（可选）：`python scripts/publish_daily_ai.py --help` 能跑、无 import 报错。

### 步骤 6 · gh-pages（无需本地恢复）
部署分支由 Actions 自动生成，**不要**手动 `git push --force` 到 `gh-pages`，以免覆盖线上。

### 步骤 7 · 恢复每日栏目自动化（见 §5.7）
WorkBuddy 自动化任务需重建/重导入，否则栏目停止更新。

---

## 5. 最容易遗漏 / 出错的环节

1. **未提交改动丢失**（最高频）：68 modified + 1 untracked。重装前务必 `--commit-push`。
2. **SSH 密钥遗忘**：远程是 SSH，无密钥无法 clone/push。且 `known_hosts`/ssh-agent 也需就位。
3. **Hugo 装成 standard 而非 extended**：PaperMod 用 SCSS，standard 版直接报 "extended version required"。
4. **Hugo 版本漂移**：未钉 0.164.0 可能触发模板/函数不兼容；以 `versions.env` 为准。
5. **`reskin_eink.py` 未跟踪**：它完全不在仓库，漏备份即永久丢失（已随本次交付纳入建议提交）。
6. **自定义 `layouts/` 覆盖缺失**：若哪天把主题当 submodule 或误删 `layouts/partials/google_analytics.html`，GA/og 标签丢失（站点仍能构建，但 SEO/统计失效）。
7. **Python 未装**：仅影响重跑发布脚本，不影响 `hugo` 构建；但栏目更新会失败。
8. **WorkBuddy 自动化未恢复**：栏目生成任务在 WorkBuddy 配置里，不在仓库——重装后栏目停更。
9. **目录名错位**：clone 默认 `LeionTong.github.io`，旧工作目录是 `LeionTong.github.io-hugo`；自动化/肌肉记忆若写死旧名会找不到路径（脚本均用相对路径，影响较小）。
10. **误提交 `public/`/密钥**：若把旧 `public/` 拷进仓库或误加私钥，会污染历史。保持 `.gitignore` 与"禁提交密钥"铁律。
11. **Git user 未设**：导致 commit 失败或作者错误，提前设好全局配置。

---

## 6. 自动化脚本说明（`scripts/backup-site-env.sh`）

| 子命令 | 作用 | 是否改动 |
|---|---|---|
| `--check` | 预检：未提交数、版本、SSH、主题 vendored | 只读 |
| `--backup-config` | 导出 `~/.gitconfig` + 生成 `versions.env` | 写到仓库同级 `site-env-backup/` |
| `--backup-ssh <dest.7z>` | 交互密码，把 `~/.ssh` 打 AES 加密 7z | 新建加密归档（机密） |
| `--commit-push` | 交互确认后 `add -A && commit && push` | 改仓库+远端 |
| `--all <dest.7z>` | config + ssh 一起 | 同上组合 |

- 默认输出目录：`仓库/../site-env-backup/`（在仓库外，避免误提交）。
- 加密依赖 `7z`；缺失时脚本会打印手动命令。
- **脚本不替你执行任何不可逆/外部动作**，敏感步骤均交互确认。

---

## 7. 仍需手动处理的步骤（脚本无法代劳）

- [ ] **转移加密 SSH 归档到离线/加密存储**（U 盘 / 密码管理器），重装后再拷回。脚本只生成归档。
- [ ] **将 SSH 公钥加入 GitHub 账户**（若不用旧密钥而重新生成）。
- [ ] **重装后重新登录**各类账号、重装 Clash/VPN/Proxifier 并导入各自配置（属通用环境，非站点专属）。
- [ ] **重建/重导入 WorkBuddy 自动化任务**（每日 AI / 每日 Github 栏目生成器）。这是"内容持续更新"的关键，且**不在仓库内**。
- [ ] **确认 Hugo 安装方式**：建议独立于 WorkBuddy 装便携版/winget，使站点不绑定 WorkBuddy 内部路径。
- [ ] 若改用新机目录名，统一为 `LeionTong.github.io-hugo` 或更新任何写死路径的引用。

---

## 附：版本钉记速查（抄自 `versions.env`）
```
Hugo        0.164.0  (extended, windows/amd64)
Git         近期 2.4x
Python      3.8+（脚本仅标准库，无 pip 依赖）
Node        不需要
远程        git@github.com:LeionTong/LeionTong.github.io.git  (master)
部署        Actions → gh-pages（自动，勿手动强推）
```
