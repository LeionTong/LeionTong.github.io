#!/usr/bin/env bash
# =============================================================================
# backup-site-env.sh — Leion'Log 站点「重装系统前」环境备份脚本
# 用途：把"项目源码 + Git 全局配置 + Hugo 版本钉记 + SSH 密钥(加密)"一次性打包，
#       使重装系统后能在干净机器上重建本地开发环境。
# 运行环境：Windows + Git Bash（MSYS2）。也可在 WSL/bash 下运行。
#
# 设计原则（安全）：
#   - 默认只做【只读预检】，不改动任何东西。
#   - 仓库自身的源码/内容靠 `git commit && git push` 上远端，脚本仅协助提交。
#   - SSH 私钥【绝不以明文落盘、绝不进仓库】；只在用户提供密码与目标路径时，
#     生成 AES 加密的 7z 归档，由用户自行转移到离线/加密存储。
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# 注：本环境 git -C <绝对路径> 解析异常，故统一 cd 进仓库后用普通 git 命令
cd "$REPO_ROOT" || { echo "无法进入仓库目录: $REPO_ROOT" >&2; exit 1; }
OUT_DIR="${BACKUP_OUT:-$REPO_ROOT/../site-env-backup}"   # 默认落在仓库同级目录，不在仓库内
HUGO_VER="0.164.0"                                       # 与 hugo.toml / workflow 钉死

log()  { printf '\033[1;36m[backup]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[✓]\033[0m %s\n' "$*"; }

usage() {
  cat <<EOF
用法:
  $0 --check                  只读预检：列出未提交改动 / 版本 / SSH 状态（默认）
  $0 --backup-config          导出 Git 全局配置 + 写 versions.env（非机密，可入库）
  $0 --backup-ssh <dest.7z>   交互式密码，把 ~/.ssh 打成 AES 加密 7z（机密，手动转移）
  $0 --commit-push            交互确认后 git add -A && commit && push origin master
  $0 --all                    依次执行 backup-config + backup-ssh（SSH 需手动给目标路径）

示例:
  $0 --check
  $0 --backup-config
  $0 --backup-ssh /e/site-ssh-backup.7z
  $0 --all /e/site-ssh-backup.7z
EOF
}

# ---- 只读预检 ---------------------------------------------------------------
preflight() {
  log "预检仓库: $REPO_ROOT"
  echo "--- Git 远程 / 分支 ---"
  git remote -v
  git branch --show-current
  echo
  echo "--- 未提交改动（重装前必须处理！）---"
  local m u
  m=$(git status -s | grep -c '^ M') || true
  u=$(git status -s | grep -c '^??') || true
  warn "已修改(未提交): $m 个文件"
  warn "未跟踪(完全不在仓库): $u 个文件"
  git status -s | head -40
  echo
  echo "--- 版本钉记 ---"
  if command -v hugo >/dev/null 2>&1; then
    hugo version || true
  else
    warn "未检测到 hugo（重装后需安装 extended $HUGO_VER）"
  fi
  echo "Git : $(git --version 2>/dev/null || echo '缺失')"
  echo "Py  : $(python3 --version 2>/dev/null || python --version 2>/dev/null || echo '缺失(发布脚本需要)')"
  echo
  echo "--- SSH 状态（clone/push 依赖）---"
  if [ -d "$HOME/.ssh" ]; then
    ls -1 "$HOME/.ssh" 2>/dev/null | sed 's/^/    /'
    ok "存在 ~/.ssh"
  else
    warn "无 ~/.ssh —— 重装后无法 SSH 方式 clone！需先有密钥并加入 GitHub"
  fi
  echo
  echo "--- 主题 vendored 校验（无 submodule 才安全）---"
  if [ -d "$REPO_ROOT/themes/PaperMod/.git" ]; then
    warn "themes/PaperMod 内含 .git —— submodule 异常，需另行备份主题"
  else
    ok "themes/PaperMod 已 vendored（随仓库入库，自动备份）"
  fi
}

# ---- 导出非机密配置 ---------------------------------------------------------
backup_config() {
  mkdir -p "$OUT_DIR"
  log "导出 Git 全局配置 -> $OUT_DIR/git-config.txt"
  git config --global --list > "$OUT_DIR/git-config.txt" 2>/dev/null || warn "无 Git 全局配置"
  log "写版本钉记 -> $OUT_DIR/versions.env"
  {
    echo "# Leion'Log 重建所需版本与安装命令（重装后照此执行）"
    echo "HUGO_VERSION=0.164.0            # 必须 extended 版"
    echo "HUGO_EXTENDED=1"
    echo "GIT_REPO=git@github.com:LeionTong/LeionTong.github.io.git"
    echo "GIT_BRANCH=master"
    echo "DEPLOY_BRANCH=gh-pages          # 由 Actions 自动部署，无需本地恢复"
    echo "PYTHON_MIN=3.8                  # 发布脚本仅用标准库，无需 pip 依赖"
    echo "NODE_REQUIRED=0                 # 本站无 package.json，不需要 Node"
    echo
    echo "# Hugo 安装（任选其一，离线优先生 portable zip）:"
    echo "#   1) winget install Hugo.Hugo.Extended --version 0.164.0"
    echo "#   2) scoop install hugo-extended   # 注意：会装 latest，需再 pin"
    echo "#   3) 便携版: 下 hugo_extended_0.164.0_windows-amd64.zip 解压到 PATH"
  } > "$OUT_DIR/versions.env"
  ok "非机密配置已导出到 $OUT_DIR"
}

# ---- 加密备份 SSH（机密）---------------------------------------------------
backup_ssh() {
  local dest="${1:-}"
  [ -z "$dest" ] && { warn "用法: $0 --backup-ssh <目标.7z 路径>"; exit 1; }
  [ ! -d "$HOME/.ssh" ] && { warn "无 ~/.ssh 可备份"; exit 1; }
  if ! command -v 7z >/dev/null 2>&1; then
    warn "未找到 7z。请手动加密备份:"
    warn "  7z a -p<你的密码> -mhe=on \"$dest\" \"$HOME/.ssh\""
    warn "  或把 ~/.ssh 拷到加密 U 盘 / 密码管理器后离线存放。"
    exit 1
  fi
  log "将把 ~/.ssh 加密归档到: $dest"
  warn "该文件含私钥，生成后【立即转移到离线/加密存储，切勿提交进仓库】"
  read -r -s -p "请输入 7z 加密密码: " PW; echo
  [ -z "$PW" ] && { warn "密码为空，中止"; exit 1; }
  7z a -p"$PW" -mhe=on "$dest" "$HOME/.ssh" >/dev/null
  ok "已生成加密归档: $dest"
  warn "请确认已转移到安全位置后再重装系统。"
}

# ---- 提交并推送未提交工作（关键）-------------------------------------------
commit_push() {
  log "准备提交未提交改动（共 $(git status -s | wc -l) 项）"
  warn "提交前请先 review: git status -s"
  read -r -p "确认提交并推送到 origin/master? [y/N] " ANS
  [[ "$ANS" =~ ^[Yy]$ ]] || { warn "已取消"; exit 0; }
  git add -A
  read -r -p "提交说明: " MSG
  git commit -m "${MSG:-chore: pre-reinstall backup}" 
  git push origin "$(git branch --show-current)"
  ok "已提交并推送。仓库源码/内容/脚本/主题现已安全（远端冗余）。"
}

# ---- 入口 ------------------------------------------------------------------
case "${1:---check}" in
  --check)        preflight ;;
  --backup-config) backup_config ;;
  --backup-ssh)   backup_ssh "${2:-}" ;;
  --commit-push)  commit_push ;;
  --all)
    backup_config
    backup_ssh "${2:-}" ;;
  -h|--help)      usage ;;
  *) warn "未知参数: $1"; usage; exit 1 ;;
esac
