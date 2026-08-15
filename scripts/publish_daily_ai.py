#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_daily_ai.py — 把自动化产出的「AI 领域每日动态」HTML 报告发布到
Leion'Log 博客的 Daily AI 栏目。

设计要点（与通通 2026-07-29 的约定）：
1. 不做内联嵌入：报告以独立 HTML 页面形式放在 static/daily-ai/，栏目页只放
   「卡片索引」，卡片直接链接到对应 .html 页面。
2. 每张卡片展示该报告「本期主线」段落内容。
3. 剔除页首 branding：masthead 内的 .kicker（观测站夜值 / Daily AI / Nightwatch /
   WAIC 等品牌行）与 .sub/.subtitle（侧重 AI Agent… 焦点行）一律移除；h1 标题与
   本期主线 lead 保留；<title> 里的「观测站夜值」一并清掉。
4. 各报告 masthead 结构不一（header/div 混用、sub 有的嵌在 h1 内），故用标准库
   html.parser 做元素级剔除，零第三方依赖，保证自动化长期稳定。

用法：
  publish_daily_ai.py --all            处理 SRC_DIR 下全部 *_AI领域每日动态.html
  publish_daily_ai.py "<某报告.html>"   处理单个报告（同时仍按 SRC_DIR 全量重建 _index.md）
"""
import os
import re
import sys
import glob
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(HERE)
SRC_DIR = r"C:\Users\Leion\WorkBuddy\automation-2026-05-09-task-1"
STATIC_DAILY = os.path.join(SITE_DIR, "static", "daily-ai")
CONTENT_DAILY = os.path.join(SITE_DIR, "content", "daily-ai")
INDEX_MD = os.path.join(CONTENT_DAILY, "_index.md")

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})_(\d{4})_AI领域每日动态\.html$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# 1) masthead branding 剔除
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
    # 清掉 <title> 里的 观测站夜值（品牌 token）
    cleaned = re.sub(r"\s*·\s*观测站夜值", "", cleaned)
    return cleaned


# ---------------------------------------------------------------------------
# 2) 抽取「本期主线」（通用：覆盖各家报告五花八门的容器与标签写法）
# ---------------------------------------------------------------------------
# 各报告把"主线/摘要"挂在多种容器 class 下：lede / mainline / lead / thesis /
# syn / summary / cross / observe / overview / three ……；标签写法也各异：
# 本期主线 / 今日主线 / 今日三句话 / 横向观察 / 主线判断 / TODAY'S MAIN LINE /
# THESIS / The Through-Line / 今日要览 / Today's Index / 今日摘要 / TL;DR ……
# 故用 HTML 树（有序内容）找到正文里第一个"主线容器"，跳过其内部的标签元素
# （span.tag / div.lbl / h2-h3 / 内联 <b>本期主线</b> 等），只保留正文文本。
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
VOID = {"img", "br", "hr", "meta", "link", "input", "area", "base",
        "col", "embed", "source", "track", "wbr"}
SEP = r"[\s:：·\-—–·、|｜/]+"


class TreeNode:
    __slots__ = ("tag", "classes", "content", "parent")

    def __init__(self, tag, classes):
        self.tag = tag
        self.classes = classes
        self.content = []          # 有序：字符串文本 或 子 TreeNode
        self.parent = None

    def text_strip(self):
        txt = []
        for it in self.content:
            txt.append(it if isinstance(it, str) else it.text_strip())
        return "".join(txt).strip()

    def content_children(self):
        return [c for c in self.content if isinstance(c, TreeNode)]


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = TreeNode("root", set())
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            n = TreeNode(tag, set(dict(attrs).get("class", "").split()))
            n.parent = self.cur
            self.cur.content.append(n)
            return
        n = TreeNode(tag, set(dict(attrs).get("class", "").split()))
        n.parent = self.cur
        self.cur.content.append(n)
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


def _is_label(node: TreeNode) -> bool:
    if node.classes & LABEL_CLASSES:
        return True
    if node.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        t = node.text_strip()
        if LEAD_HEADING_RE.search(t) and len(t) < 60:
            return True
    t = node.text_strip()
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


def _overview_titles(node: TreeNode) -> str:
    out = []
    for item in node.content:
        if not isinstance(item, TreeNode) or "ov-item" not in item.classes:
            continue
        for c in item.content:
            if isinstance(c, TreeNode) and "ov-title" in c.classes:
                t = c.text_strip().strip()
                if t:
                    out.append(t)
    return " ｜ ".join(out)


def _find_first_lead(root: TreeNode):
    stack = [root]
    while stack:
        n = stack.pop()
        if "masthead" in n.classes:
            continue
        if n.classes & LEAD_CONTAINER_CLASSES:
            return n
        stack.extend(reversed(n.content_children()))
    return None


def extract_lead(raw: str) -> str:
    body = re.sub(r"<head[\s\S]*?</head>", "", raw, flags=re.I)
    body = re.sub(r"<style[\s\S]*?</style>", "", body, flags=re.I)
    tb = _TreeBuilder()
    tb.feed(body)
    node = _find_first_lead(tb.root)
    if not node:
        return ""
    txt = _overview_titles(node) if "overview" in node.classes else _node_text(node)
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r"^" + SEP, "", txt)
    txt = re.sub(LEAD_WORD_RE, "", txt)      # 去残留的"本期主线/今日摘要…"等标签词
    txt = re.sub(r"^" + SEP, "", txt)
    txt = re.sub(SEP + r"$", "", txt)
    return txt


# ---------------------------------------------------------------------------
# 3) 文件名 -> (date, time, slug)
# ---------------------------------------------------------------------------
def parse_name(fname: str):
    m = DATE_RE.search(os.path.basename(fname))
    if not m:
        return None
    date, hhmm = m.group(1), m.group(2)
    time = f"{hhmm[:2]}:{hhmm[2:]}"
    slug = f"{date}-{hhmm}"
    return date, time, slug


# ---------------------------------------------------------------------------
# 4) 主流程
# ---------------------------------------------------------------------------
def process_file(path: str) -> dict | None:
    meta = parse_name(path)
    if not meta:
        return None
    date, time, slug = meta
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    cleaned = clean_html(raw)
    os.makedirs(STATIC_DAILY, exist_ok=True)
    out_html = os.path.join(STATIC_DAILY, slug + ".html")
    with open(out_html, "w", encoding="utf-8", newline="\n") as f:
        f.write(cleaned)
    lead = extract_lead(raw)
    return {"date": date, "time": time, "slug": slug, "lead": lead}


SLUG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{4})\.html$")


def collect_published(known_slugs: set) -> list:
    """补齐「已发布但源报告已不在 SRC_DIR」的期次。

    _index.md 每次全量重建，仅靠 SRC_DIR 会在源文件被清理后丢卡片。
    static/daily-ai/ 下的页面是发布后的权威副本，从中回填即可保证
    栏目索引单调不减（幂等，可反复执行）。
    """
    out = []
    if not os.path.isdir(STATIC_DAILY):
        return out
    for name in sorted(os.listdir(STATIC_DAILY)):
        m = SLUG_RE.match(name)
        if not m:
            continue
        slug = name[:-5]
        if slug in known_slugs:
            continue
        date, hhmm = m.group(1), m.group(2)
        try:
            with open(os.path.join(STATIC_DAILY, name), "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError:
            continue
        out.append({"date": date, "time": f"{hhmm[:2]}:{hhmm[2:]}",
                    "slug": slug, "lead": extract_lead(raw)})
    return out


def build_index(records: list):
    records = [r for r in records if r]
    records += collect_published({r["slug"] for r in records})
    records.sort(key=lambda r: (r["date"], r["time"]), reverse=True)
    cards = []
    for r in records:
        lead = r["lead"] or "（本期未标注主线摘要）"
        cards.append(
            f'  <a class="da-card" href="/daily-ai/{r["slug"]}.html">\n'
            f'    <div class="da-card-date">{r["date"]} · {r["time"]}</div>\n'
            f'    <div class="da-card-main">{lead}</div>\n'
            f'    <div class="da-card-go">阅读完整报告 →</div>\n'
            f'  </a>'
        )
    cards_html = "\n".join(cards)
    md = f"""---
title: "Daily AI"
---

> 自动化「AI 领域每日动态」栏目，不定期更新，聚焦 **AI Agent / 终端与端侧 / 具身智能**。
> 点击任意卡片，直达当期的完整图文报告（含信号星图与逐条解读）。

<div class="da-cards">
{cards_html}
</div>

<style>
.da-cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;margin:26px 0 8px}}
.da-card{{display:block;border:1px solid var(--card-edge,rgba(111,214,224,.18));border-radius:14px;
  padding:18px 18px 14px;background:var(--card,rgba(20,28,48,.55));text-decoration:none;color:inherit;
  transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}}
.da-card:hover{{transform:translateY(-3px);border-color:var(--cyan,#6fd6e0);
  box-shadow:0 10px 30px rgba(0,0,0,.28)}}
.da-card-date{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;letter-spacing:.12em;
  color:var(--cyan,#6fd6e0);margin-bottom:8px}}
.da-card-main{{font-size:14.5px;line-height:1.7;color:var(--ink-soft,#a9b4cc)}}
.da-card-go{{margin-top:12px;font-size:13px;color:var(--gold,#e9c46a)}}
</style>
"""
    os.makedirs(CONTENT_DAILY, exist_ok=True)
    with open(INDEX_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    return len(records)


def main():
    args = sys.argv[1:]
    # _index.md 始终按 SRC_DIR 全量重建：即使只传入单个报告，也不丢失历史卡片。
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*_AI领域每日动态.html")))
    if args and args[0] != "--all":
        known = {os.path.abspath(f) for f in files}
        extras = [a for a in args if os.path.isfile(a) and os.path.abspath(a) not in known]
        files += extras
    if not files:
        print("没有找到待处理的报告 HTML。", file=sys.stderr)
        sys.exit(1)
    records = [process_file(p) for p in files]
    n = build_index(records)
    print(f"已处理 {len([r for r in records if r])} 篇报告，生成 {n} 张卡片到 {INDEX_MD}")


if __name__ == "__main__":
    main()
