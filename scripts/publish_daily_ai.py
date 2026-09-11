#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_daily_ai.py — 重建 Daily AI 栏目索引（content/daily-ai/_index.md）。

三栏目脚本同构（ai / github / terminal）：单期 HTML 由自动化直接生成到
static/daily-<栏目>/，本脚本**不搬运文件**，只做「扫描 -> 提主线 -> 重建
索引」。从 static 回填，保证索引单调不减（幂等，可反复执行）。

栏目差异：摄入外部单文件时先做 masthead 品牌行剔除（历史报告结构不一，
标准库 html.parser 元素级剔除 .kicker/.sub/.subtitle，零第三方依赖）。

用法：
  publish_daily_ai.py --all            重建索引（扫描 static）
  publish_daily_ai.py "<某报告.html>"  清洗后复制进 static 并重建索引
"""
import os
import re
import sys
import time
import html as htmlmod
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(HERE)
STATIC_DAILY = os.path.join(SITE_DIR, "static", "daily-ai")
CONTENT_DAILY = os.path.join(SITE_DIR, "content", "daily-ai")
INDEX_MD = os.path.join(CONTENT_DAILY, "_index.md")
CARD_CSS = os.path.join(HERE, "da_cards.css")

SLUG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{4})\.html$")
VOID = {"img", "br", "hr", "meta", "link", "input", "area", "base",
        "col", "embed", "source", "track", "wbr"}


# ---------------------------------------------------------------------------
# 0) masthead 品牌行剔除（仅摄入外部单文件时使用）
# ---------------------------------------------------------------------------
class MastheadCleaner(HTMLParser):
    """元素级剔除 masthead 内的 .kicker / .sub / .subtitle，保留其余。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []            # [{tag, classes}]
        self.drop_depth = None     # 进入 drop 子树时的 stack 深度

    def _ancestor_masthead(self):
        return any("masthead" in s["classes"] for s in self.stack)

    def _render_start(self, tag, attrs, self_closing=False):
        s = "<" + tag
        for k, v in attrs:
            s += f' {k}' if v is None else f' {k}="{v}"'
        return s + ("/>" if self_closing else ">")

    def handle_starttag(self, tag, attrs):
        classes = set(dict(attrs).get("class", "").split())
        depth = len(self.stack)
        if (self.drop_depth is None and self._ancestor_masthead()
                and ("kicker" in classes or "sub" in classes or "subtitle" in classes)):
            self.drop_depth = depth
            self.stack.append({"tag": tag, "classes": classes})
            return
        if self.drop_depth is None:
            self.out.append(self._render_start(tag, attrs))
        self.stack.append({"tag": tag, "classes": classes})

    def handle_startendtag(self, tag, attrs):
        if self.drop_depth is None:
            self.out.append(self._render_start(tag, attrs, self_closing=True))

    def handle_endtag(self, tag):
        if not self.stack:
            if self.drop_depth is None:
                self.out.append(f"</{tag}>")
            return
        top = self.stack[-1]
        if (self.drop_depth is not None
                and len(self.stack) - 1 == self.drop_depth
                and top["tag"] == tag):
            self.drop_depth = None
            self.stack.pop()
            return
        if self.drop_depth is None:
            self.out.append(f"</{tag}>")
        self.stack.pop()

    def handle_data(self, data):
        if self.drop_depth is None:
            self.out.append(data)

    def handle_entityref(self, name):
        if self.drop_depth is None:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if self.drop_depth is None:
            self.out.append(f"&#{name};")

    def handle_comment(self, data):
        if self.drop_depth is None:
            self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        if self.drop_depth is None:
            self.out.append(f"<!{decl}>")


def clean_html(raw: str) -> str:
    c = MastheadCleaner()
    c.feed(raw)
    cleaned = "".join(c.out)
    # 清掉 <title> 里的历史品牌 token
    cleaned = re.sub(r"\s*·\s*观测站夜值", "", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# 1) 轻量 HTML 树（仅用于取 .mh-sub / .lede / h1 / 主线容器的文本）
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


# ---------------------------------------------------------------------------
# 2) 主线摘要抽取（容器启发式，兼容历史各版式 + 现行 DAILY-COMMON 模板）
# ---------------------------------------------------------------------------
LEAD_CONTAINER_CLASSES = {
    "lede", "mainline", "lead", "thesis", "syn", "summary",
    "cross", "observe", "overview", "three", "lede-box", "main",
}
LABEL_CLASSES = {"tag", "lbl", "label", "sec-label", "h", "kicker", "sub", "subtitle"}
LEAD_HEADING_RE = re.compile(
    r"(本期主线|本期侧重|今日主线|今日摘要|今日三句话|今日一句话|横向观察|主线判断"
    r"|TODAY'?S\s*MAIN\s*LINE|TL;?DR|THESIS|Through[\s-]?Line"
    r"|今日要览|Today'?s\s*Index|MAIN\s*LINE)",
    re.I)
LEAD_WORD_RE = re.compile(
    r"^(本期主线|本期侧重|今日主线|今日摘要|横向观察|今日三句话|今日一句话|主线判断"
    r"|今日要览|TODAY'?S\s*MAIN\s*LINE|THESIS|Through[\s-]?Line)\b",
    re.I)


def _is_label(node: TreeNode) -> bool:
    if node.classes & LABEL_CLASSES:
        return True
    if node.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        t = node.text()
        if LEAD_HEADING_RE.search(t) and len(t) < 60:
            return True
    t = node.text()
    if LEAD_HEADING_RE.search(t) and len(t) < 60:
        return True
    return False


def _node_text(node: TreeNode) -> str:
    if _is_label(node):
        return ""
    parts = []
    for item in node.content:
        if isinstance(item, str):
            parts.append(item)
        elif not _is_label(item):
            parts.append(_node_text(item))
    return "".join(parts)


def _find_first_lead(root: TreeNode):
    stack = [root]
    while stack:
        n = stack.pop()
        if "masthead" in n.classes:
            continue
        if n.classes & LEAD_CONTAINER_CLASSES:
            return n
        stack.extend(reversed(n.children()))
    return None


def extract_lead(raw: str) -> str:
    """主线摘要：优先主线容器（.lede 等），回退 .mh-sub，再回退正文首段。"""
    root = build_tree(raw)
    node = _find_first_lead(root)
    if node is not None:
        txt = _norm(_node_text(node))
        txt = re.sub(LEAD_WORD_RE, "", txt).strip()
        if len(txt) >= 20:
            return txt
    for cls in ("mh-sub", "lede"):
        n = _find(root, cls)
        if n:
            txt = _norm(n.text())
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
# 3) 收集记录
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
    """从 static/daily-ai 回填（权威副本，保证索引单调不减）。"""
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
    """把外部 HTML 清洗后复制进 static（若尚未存在），返回记录。"""
    r = record_from_file(path)
    os.makedirs(STATIC_DAILY, exist_ok=True)
    dst = os.path.join(STATIC_DAILY, r["slug"] + ".html")
    if os.path.abspath(path) != os.path.abspath(dst):
        with open(path, "r", encoding="utf-8") as f:
            content = clean_html(f.read())
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return r


# ---------------------------------------------------------------------------
# 4) 重建索引
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
        title = r["title"] or f'Daily AI · {r["date"]}'
        cards.append(
            f'  <a class="da-card" href="/daily-ai/{r["slug"]}.html">\n'
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
title: "Daily AI"
---

> 自动化「AI 领域每日动态」栏目，不定期更新，聚焦 **AI Agent / 终端与端侧 / 具身智能**。
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

    # 命令行显式传入的报告（清洗后摄入）
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
    print(f"Daily AI 索引已重建：{n} 张卡片 -> {INDEX_MD}")


def write_empty_index():
    with open(CARD_CSS, "r", encoding="utf-8") as f:
        css = f.read().strip()
    md = f"""---
title: "Daily AI"
---

> 自动化「AI 领域每日动态」栏目，不定期更新，聚焦 **AI Agent / 终端与端侧 / 具身智能**。

_本期尚无内容，首期报告将于首次运行后自动生成。_

<style>
{css}
</style>
"""
    os.makedirs(CONTENT_DAILY, exist_ok=True)
    with open(INDEX_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print(f"Daily AI 空索引已生成 -> {INDEX_MD}")


if __name__ == "__main__":
    main()
