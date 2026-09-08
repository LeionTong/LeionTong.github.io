#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_daily_github.py — 重建 Daily Github 栏目索引（content/daily-github/_index.md）。

与 publish_daily_ai.py 的分工差异：
  AI 栏目：脚本负责「源报告 HTML -> static/daily-ai/ 落盘 + 索引重建」两步。
  Github 栏目：单期 HTML 由自动化直接生成到 static/daily-github/（历史 NO.01-05
  亦为手工/临时脚本产出），故本脚本**不搬运文件**，只做「扫描 -> 提主线 -> 重建
  索引」。可选地把外部 HTML 复制进 static（传入文件路径时）。

索引单调不减：static/daily-github/ 下的页面是发布后的权威副本，每次全量重建都从
中回填，源文件被清理也不会丢卡片（幂等，可反复执行）。

用法：
  publish_daily_github.py --all            重建索引（扫描 static + 归档目录新文件）
  publish_daily_github.py "<某报告.html>"  复制该报告进 static 后重建索引
"""
import os
import re
import sys
import glob
import html as htmlmod
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(HERE)
STATIC_DAILY = os.path.join(SITE_DIR, "static", "daily-github")
CONTENT_DAILY = os.path.join(SITE_DIR, "content", "daily-github")
INDEX_MD = os.path.join(CONTENT_DAILY, "_index.md")
CARD_CSS = os.path.join(HERE, "da_cards.css")

# 自动化归档目录（若存在其中的 .html 视为待发布新报告）
ARCHIVE_DIR = r"C:\Users\Leion\.workbuddy\automation-data\github-daily\archive"

SLUG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{4})\.html$")
VOID = {"img", "br", "hr", "meta", "link", "input", "area", "base",
        "col", "embed", "source", "track", "wbr"}


# ---------------------------------------------------------------------------
# 1) 轻量 HTML 树（仅用于取 .mh-sub / .lede / h1 的文本）
# ---------------------------------------------------------------------------
class TreeNode:
    __slots__ = ("tag", "classes", "content", "parent")

    def __init__(self, tag, classes):
        self.tag = tag
        self.classes = classes
        self.content = []
        self.parent = None

    def text(self):
        parts = []
        for it in self.content:
            parts.append(it if isinstance(it, str) else it.text())
        return "".join(parts)

    def children(self):
        return [c for c in self.content if isinstance(c, TreeNode)]


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = TreeNode("root", set())
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = TreeNode(tag, set(dict(attrs).get("class", "").split()))
        n.parent = self.cur
        self.cur.content.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        n = TreeNode(tag, set(dict(attrs).get("class", "").split()))
        n.parent = self.cur
        self.cur.content.append(n)

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root and node.tag == tag:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.content.append(data)


def build_tree(raw: str) -> TreeNode:
    body = re.sub(r"<head[\s\S]*?</head>", "", raw, flags=re.I)
    body = re.sub(r"<style[\s\S]*?</style>", "", body, flags=re.I)
    body = re.sub(r"<script[\s\S]*?</script>", "", body, flags=re.I)
    tb = _Builder()
    tb.feed(body)
    return tb.root


def _find(root: TreeNode, cls: str):
    stack = [root]
    while stack:
        n = stack.pop()
        if cls in n.classes:
            return n
        stack.extend(reversed(n.children()))
    return None


def _norm(txt: str) -> str:
    txt = re.sub(r"\s+", " ", txt or "").strip()
    return txt


def extract_title(raw: str) -> str:
    m = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", raw, flags=re.I)
    if not m:
        return ""
    return _norm(re.sub(r"<[^>]+>", "", m.group(1)))


def extract_lead(raw: str) -> str:
    """主线摘要：优先 .mh-sub（报头副标题），回退 .lede，再回退正文首段。"""
    root = build_tree(raw)
    for cls in ("mh-sub", "lede"):
        node = _find(root, cls)
        if node:
            txt = _norm(node.text())
            if len(txt) >= 20:
                return txt
    # 回退：正文里第一个足够长的 <p>
    stack = [root]
    while stack:
        n = stack.pop()
        if n.tag == "p":
            txt = _norm(n.text())
            if len(txt) >= 40:
                return txt
        stack.extend(reversed(n.children()))
    return ""


def meta_from_html(raw: str, fallback_path: str):
    """从 HTML 内容解析 (date, hhmm)；取不到则退回文件 mtime。"""
    import time
    date = hhmm = None
    head = raw[:4000]
    m = re.search(r"(\d{4}-\d{2}-\d{2})", head)
    if m:
        date = m.group(1)
    m = re.search(r"(\d{4}-\d{2}-\d{2})[^\d]{0,6}(\d{2}):(\d{2})", head)
    if m:
        date, hhmm = m.group(1), m.group(2) + m.group(3)
    if not hhmm:
        m = re.search(r"\b(\d{2}):(\d{2})\b", head)
        if m:
            hhmm = m.group(1) + m.group(2)
    if not date or not hhmm:
        st = os.stat(fallback_path)
        lt = time.localtime(st.st_mtime)
        date = date or time.strftime("%Y-%m-%d", lt)
        hhmm = hhmm or time.strftime("%H%M", lt)
    return date, hhmm


# ---------------------------------------------------------------------------
# 2) 收集记录
# ---------------------------------------------------------------------------
def record_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    date, hhmm = meta_from_html(raw, path)
    return {
        "slug": f"{date}-{hhmm}",
        "date": date,
        "time": f"{hhmm[:2]}:{hhmm[2:]}",
        "title": extract_title(raw),
        "lead": extract_lead(raw),
    }


def collect_static() -> list:
    """从 static/daily-github 回填（权威副本，保证索引单调不减）。"""
    out = []
    if not os.path.isdir(STATIC_DAILY):
        return out
    for name in sorted(os.listdir(STATIC_DAILY)):
        m = SLUG_RE.match(name)
        if not m:
            continue
        path = os.path.join(STATIC_DAILY, name)
        r = record_from_file(path)
        r["slug"] = name[:-5]
        r["date"], hhmm = m.group(1), m.group(2)
        r["time"] = f"{hhmm[:2]}:{hhmm[2:]}"
        out.append(r)
    return out


def ingest(path: str) -> dict:
    """把外部 HTML 复制进 static（若尚未存在），返回记录。"""
    r = record_from_file(path)
    os.makedirs(STATIC_DAILY, exist_ok=True)
    dst = os.path.join(STATIC_DAILY, r["slug"] + ".html")
    if os.path.abspath(path) != os.path.abspath(dst):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return r


# ---------------------------------------------------------------------------
# 3) 重建索引
# ---------------------------------------------------------------------------
def build_index(records: list) -> int:
    seen, uniq = set(), []
    for r in records:
        if r["slug"] in seen:
            continue
        seen.add(r["slug"])
        uniq.append(r)
    uniq.sort(key=lambda r: (r["date"], r["time"]), reverse=True)

    cards = []
    for r in uniq:
        lead = r["lead"] or "（本期未标注主线摘要）"
        title = r["title"] or f'Daily Github · {r["date"]}'
        cards.append(
            f'  <a class="da-card" href="/daily-github/{r["slug"]}.html">\n'
            f'    <div class="da-card-date">{r["date"]} · {r["time"]}</div>\n'
            f'    <div class="da-card-title">{htmlmod.escape(title)}</div>\n'
            f'    <div class="da-card-main">{htmlmod.escape(lead)}</div>\n'
            f'    <div class="da-card-go">阅读完整报告 →</div>\n'
            f'  </a>'
        )
    cards_html = "\n".join(cards)

    with open(CARD_CSS, "r", encoding="utf-8") as f:
        css = f.read().strip()

    md = f"""---
title: "Daily Github"
---

> 自动化「GitHub 优质项目」栏目，每日筛选 5 个**主流与小众兼具、易商业化、可规模化、低边际成本、可快速验证**的开源项目。
> 点击任意卡片，直达当期的完整图文报告（含五维评分与 30 分钟验证路径）。

<div class="da-cards">
{cards_html}
</div>

<style>
{css}
</style>
"""
    os.makedirs(CONTENT_DAILY, exist_ok=True)
    with open(INDEX_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    return len(uniq)


def main():
    args = sys.argv[1:]
    records = []

    # 归档目录里的新报告（自动化产物）
    if os.path.isdir(ARCHIVE_DIR):
        for p in sorted(glob.glob(os.path.join(ARCHIVE_DIR, "*.html"))):
            try:
                records.append(ingest(p))
            except OSError as e:
                print(f"跳过 {p}: {e}", file=sys.stderr)

    # 命令行显式传入的报告
    if args and args[0] != "--all":
        for a in args:
            if os.path.isfile(a):
                try:
                    records.append(ingest(a))
                except OSError as e:
                    print(f"跳过 {a}: {e}", file=sys.stderr)

    # 静态目录回填（保证历史卡片不丢）
    records += collect_static()

    if not records:
        print("没有找到任何报告 HTML。", file=sys.stderr)
        sys.exit(1)

    n = build_index(records)
    print(f"Daily Github 索引已重建：{n} 张卡片 -> {INDEX_MD}")


if __name__ == "__main__":
    main()
