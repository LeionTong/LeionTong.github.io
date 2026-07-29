#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把「每日 AI 新闻推送」自动化产出的 HTML 报告转换为 Hugo 文章，发布到 Daily AI 栏目。

用法:
  python publish_daily_ai.py <report.html>        # 转换单个报告
  python publish_daily_ai.py --all                # 转换 automation 目录下全部 *_AI领域每日动态.html
  python publish_daily_ai.py --all --since <日期> # 仅转换该日期(含)之后的报告

产出:
  content/daily-ai/<YYYY-MM-DD>-<HHMM>.md         # 内嵌完整样式 + 正文的 Hugo 文章
  static/daily-ai/<YYYY-MM-DD>-<HHMM>.html        # 原始 HTML(供"查看原始版本"链接)

设计: 报告是自带深色主题/星图/SVG 动画的完整 HTML 文档。本脚本仅提取 <style> 与 <body> 正文，
把 `body` 选择器改写为 `.dailyai-report` 包裹容器类,从而在不覆盖任何主题模板的前提下,
完整保留星图背景、卡片配色与 SVG 星座图。Hugo 侧需开启 Goldmark unsafe=true 才能放行内联 HTML。
"""
import sys
import re
import shutil
import pathlib
import datetime

# ---- 路径常量(本机) ----
HUGO_ROOT = pathlib.Path(r"C:\Users\Leion\T\LeionTong.github.io-hugo")
CONTENT_DIR = HUGO_ROOT / "content" / "daily-ai"
STATIC_DIR = HUGO_ROOT / "static" / "daily-ai"
AUTOMATION_DIR = pathlib.Path(r"C:\Users\Leion\WorkBuddy\automation-2026-05-09-task-1")

REPORT_GLOB = "*_AI领域每日动态.html"


def parse_filename(path: pathlib.Path):
    """从文件名提取 YYYY-MM-DD 与 HHMM,如 2026-07-29_1812_AI领域每日动态.html"""
    m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{4})", path.name)
    if not m:
        raise SystemExit(f"[✗] 无法从文件名解析日期/时间: {path.name}")
    return m.group(1), m.group(2)


def extract(html_text: str):
    """提取 <style>...</style> 与 <body>...</body> 内部内容"""
    style_m = re.search(r"<style>(.*?)</style>", html_text, re.S)
    style = style_m.group(1) if style_m else ""
    body_m = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.S)
    body = body_m.group(1) if body_m else ""
    # 提取在线字体 <link>(preconnect + stylesheet),保持观感
    fonts = re.findall(r"<link[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com)[^>]*>", html_text)
    return style, body, "\n".join(fonts)


def adapt_style(style: str) -> str:
    """把 body 选择器改写为 .dailyai-report,使星图/渐变在包裹容器内生效"""
    style = re.sub(r"body\s*::before", ".dailyai-report::before", style)
    style = re.sub(r"body\s*::after", ".dailyai-report::after", style)
    style = re.sub(r"body\s*\{", ".dailyai-report{", style)
    # 确保包裹容器自身定位/溢出正确,以便星图伪元素正确铺底
    if ".dailyai-report{" in style:
        style = style.replace(
            ".dailyai-report{",
            ".dailyai-report{position:relative;overflow:hidden;",
            1,
        )
    return style


def build_markdown(date: str, time: str, style: str, body: str, fonts: str, slug: str) -> str:
    iso = f"{date}T{time[:2]}:{time[2:]}:00+08:00"
    hhmm = f"{time[:2]}:{time[2:]}"
    title = f"AI 领域每日动态 · {date} {hhmm}"
    summary = f"每日 AI 观测站夜值 · {date} {hhmm} · 侧重 AI Agent / 终端与端侧 / 具身智能"
    font_block = fonts if fonts else ""
    return f"""---
title: "{title}"
date: {iso}
slug: {slug}
description: "{summary}"
summary: "{summary}"
tags: ["ai", "daily-ai"]
draft: false
---

{font_block}
<style>{style}</style>

<div class="dailyai-report">
{body}
</div>

---

[查看原始 HTML 版本](/daily-ai/{slug}.html) · 由「每日 AI 新闻推送」自动化生成
"""


def process_file(src: pathlib.Path):
    text = src.read_text(encoding="utf-8")
    style, body, fonts = extract(text)
    if not body:
        print(f"[!] 跳过(无 <body> 正文): {src.name}")
        return None
    style = adapt_style(style)
    date, time = parse_filename(src)
    slug = f"{date}-{time}"
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    md_path = CONTENT_DIR / f"{slug}.md"
    md_path.write_text(build_markdown(date, time, style, body, fonts, slug), encoding="utf-8")
    raw_path = STATIC_DIR / f"{slug}.html"
    shutil.copy(src, raw_path)
    print(f"[✓] {src.name}  ->  {md_path.relative_to(HUGO_ROOT)}  +  {raw_path.relative_to(HUGO_ROOT)}")
    return md_path


def main():
    args = sys.argv[1:]
    if args and args[0] != "--all":
        # 单文件模式
        src = pathlib.Path(args[0])
        if not src.exists():
            raise SystemExit(f"[✗] 源文件不存在: {src}")
        process_file(src)
        return

    # --all 模式
    since = None
    if "--since" in args:
        idx = args.index("--since")
        if idx + 1 < len(args):
            since = args[idx + 1]
    files = sorted(AUTOMATION_DIR.glob(REPORT_GLOB), key=lambda p: p.name)
    if since:
        files = [f for f in files if f.name >= f"{since}_"]
    if not files:
        print("[!] 未找到可转换的报告文件。")
        return
    print(f"[*] 待转换 {len(files)} 篇报告")
    for f in files:
        process_file(f)


if __name__ == "__main__":
    main()
