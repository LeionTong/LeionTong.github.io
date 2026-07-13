# Leion'Log

个人博客，基于 **Hugo + PaperMod** 主题构建，通过 **GitHub Actions** 自动部署到 GitHub Pages（`gh-pages` 分支）。

## 本地开发与预览

```bash
# 安装 Hugo extended（v0.164.0）后
hugo server --bind 127.0.0.1 -p 1313   # 本地预览 http://localhost:1313
hugo --gc --minify                      # 生产构建到 ./public
```

## 目录结构

- `hugo.toml` —— 站点与 PaperMod 主题配置
- `content/posts/` —— 文章（front matter 含 `slug`，URL 全英文）
- `static/` —— 静态资源（头像 `avatar.gif` 等）
- `themes/PaperMod/` —— 主题（已随仓库 vendored，无需 submodule）
- `.github/workflows/hugo-deploy.yml` —— 推送 `master` 即自动构建并部署

## 部署

推送 `master` 分支即触发 Actions：构建 Hugo → 强推 `gh-pages` → GitHub Pages 发布。
线上地址：https://leiontong.github.io/
