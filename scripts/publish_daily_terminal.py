#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_daily_terminal.py — 重建 Daily Terminal 栏目索引（content/daily-terminal/_index.md）。

三栏目脚本同构（ai / github / terminal）：单期 HTML 由自动化直接生成到
static/daily-terminal/，本脚本**不搬运文件**，只做「扫描 -> 提主线 -> 重建
索引」。从 static 回填，保证索引单调不减（幂等，可反复执行）。

用法：
  publish_daily_terminal.py --all            重建索引（扫描 static）
  publish_daily_terminal.py "<某报告.html>"  复制该报告进 static 后重建索引
"""
import os
import re
import sys
import html as htmlmod
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(HERE)
STATIC_DAILY = os.path.join(SITE_DIR, "static", "daily-terminal")
CONTENT_DAILY = os.path.join(SITE_DIR, "content", "daily-terminal")
INDEX_MD = os.path.join(CONTENT_DAILY, "_index.md")
CARD_CSS = os.path.join(HERE, "da_cards.css")

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
    return re.sub(r"\s+", " ", txt or "").strip()


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
    """从 static/daily-terminal 回填（权威副本，保证索引单调不减）。"""
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
        title = r["title"] or f'Daily Terminal · {r["date"]}'
        cards.append(
            f'  <a class="da-card" href="/daily-terminal/{r["slug"]}.html">\n'
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
title: "Daily Terminal"
---

> 自动化「终端智能优选项目」栏目，每日发现并评估优质**终端硬件开源项目**
> （语音终端 / 穿戴 / 桌面机器人 / 智能屏显示 / e-paper / 具身小硬件），兼顾可玩性与商业化潜力。
> 点击任意卡片，直达当期的完整图文报告。

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
        # 尚无报告时，仍生成一个只有说明的空索引，保证栏目可访问
        print("没有找到任何报告 HTML，生成空索引。", file=sys.stderr)
        write_empty_index()
        return

    n = build_index(records)
    print(f"Daily Terminal 索引已重建：{n} 张卡片 -> {INDEX_MD}")


def write_empty_index():
    with open(CARD_CSS, "r", encoding="utf-8") as f:
        css = f.read().strip()
    md = f"""---
title: "Daily Terminal"
---

> 自动化「终端智能优选项目」栏目，每日发现并评估优质**终端硬件开源项目**
> （语音终端 / 穿戴 / 桌面机器人 / 智能屏显示 / e-paper / 具身小硬件），兼顾可玩性与商业化潜力。

_本期尚无内容，首期报告将于首次运行后自动生成。_

<style>
{css}
</style>
"""
    os.makedirs(CONTENT_DAILY, exist_ok=True)
    with open(INDEX_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print(f"Daily Terminal 空索引已生成 -> {INDEX_MD}")


if __name__ == "__main__":
    main()
