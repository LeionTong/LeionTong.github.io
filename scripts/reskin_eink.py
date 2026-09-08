#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reskin_eink.py — 把历史单期 HTML 批量转换为墨水屏友好版本。

策略（重要）：不替换各页自有 CSS。
历史页面共 48 套互不相同的手写样式、类名词汇各异，直接换 <style> 会导致
正文大面积丢失样式。因此采用「保留 + 净化 + 叠加」三段式：

  1. 保留：各页自有 CSS 全部保留，版面结构不受影响。
  2. 净化：剔除渐变 / 阴影 / 动画 / 过渡 / 变换 / 半透明 / 固定定位 / 外部字体，
          深色背景翻转为浅色，文字颜色按对比度下限收紧，字号与行高兜底抬升。
  3. 叠加：在最前面并入 eink-base.css 作为统一基线，末尾追加保证性规则。

幂等：可反复执行，同一份文件二次处理结果稳定。
回滚：仓库已版本化，`git checkout -- static/` 即可还原。

用法：
  python reskin_eink.py --dry-run            # 只报告不落盘
  python reskin_eink.py                      # 处理全部
  python reskin_eink.py --only '2026-08-*'   # 只处理匹配的文件名
  python reskin_eink.py --verify             # 校验已处理文件是否仍违反约束
"""

import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
BASE_CSS = os.path.join(HERE, "eink-base.css")
TARGET_DIRS = [
    os.path.join(SITE, "static", "daily-ai"),
    os.path.join(SITE, "static", "daily-github"),
]

SYS_FONT = (
    "-apple-system,BlinkMacSystemFont,\"PingFang SC\",\"Hiragino Sans GB\","
    "\"Microsoft YaHei\",\"Source Han Sans SC\",\"Noto Sans CJK SC\","
    "\"Helvetica Neue\",Arial,sans-serif"
)
MONO_FONT = (
    "ui-monospace,SFMono-Regular,Menlo,Consolas,\"Liberation Mono\","
    "\"Courier New\",monospace"
)
SERIF_FONT = (
    "Georgia,\"Songti SC\",\"Noto Serif CJK SC\",\"Source Han Serif SC\","
    "\"Times New Roman\",serif"
)

# 已知的网络字体名（Google Fonts 等），命中即整体替换为系统字体栈
MONO_HINTS = [
    "jetbrains mono", "jetbrainsmono", "fira code", "firacode", "space mono",
    "spacemono", "source code", "ibm plex mono", "roboto mono",
    "courier prime", "courierprime", "courier", "menlo", "consolas", "monaco",
]
SERIF_HINTS = [
    "cormorant", "playfair", "lora", "merriweather", "spectral",
    "eb garamond", "libre baskerville", "crimson", "pt serif", "vollkorn",
    "young serif", "fraunces", "newsreader", "literata", "noto serif",
    "source serif", "times new roman",
]
SANS_HINTS = [
    "inter", "roboto", "karla", "manrope", "lato", "open sans", "mukta",
    "work sans", "zilla", "poppins", "nunito", "figtree", "dm sans",
]
WEB_FONT_HINTS = MONO_HINTS + SERIF_HINTS + SANS_HINTS

# 直接丢弃的属性（墨水屏会产生残影 / 脏块 / 无效）
DROP_PROPS = {
    "animation", "animation-name", "animation-duration", "animation-delay",
    "animation-timing-function", "animation-iteration-count",
    "animation-direction", "animation-fill-mode", "animation-play-state",
    "transition", "transition-property", "transition-duration",
    "transition-delay", "transition-timing-function",
    "box-shadow", "text-shadow", "filter", "-webkit-filter", "backdrop-filter",
    "-webkit-backdrop-filter", "transform", "-webkit-transform",
    "-ms-transform", "transform-origin", "transform-style", "perspective",
    "perspective-origin", "will-change", "mix-blend-mode", "isolation",
    "backface-visibility", "contain", "content-visibility",
}

BG_PROPS = {"background", "background-color"}
OPACITY_PROPS = {"opacity", "fill-opacity", "stroke-opacity", "stop-opacity"}
BGIMG_PROPS = {"background-image"}
FG_PROPS = {"color", "-webkit-text-fill-color", "caret-color"}

MIN_FONT_PX = 13.0
BODY_MIN_FONT_PX = 17.0
MIN_LINE_HEIGHT = 1.7
FALLBACK_LINE_HEIGHT = 1.85
CONTRAST_NORMAL = 4.5
CONTRAST_LARGE = 3.0

NAMED_COLORS = {
    "transparent": None, "white": (255, 255, 255), "black": (0, 0, 0),
    "red": (255, 0, 0), "gray": (128, 128, 128), "grey": (128, 128, 128),
    "silver": (192, 192, 192), "paper": (255, 255, 255),
}

STATS = {}


def stat(key, n=1):
    STATS[key] = STATS.get(key, 0) + n


# ------------------------------------------------- CSS 自定义属性（变量）

# 历史页面大量使用 background:var(--bg) / color:var(--muted)，
# 不解析变量就无法判断真实的明暗与对比度。
VAR_MAP = {}

VAR_REF_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)")


def collect_vars(css):
    """收集整份 CSS 里的自定义属性定义。:root 优先，其次其它选择器。"""
    root_attrs, other_attrs = {}, {}
    for prelude, body in iter_blocks(css):
        if body is None:
            continue
        target = root_attrs if prelude.strip().lower().startswith(":root") else other_attrs
        for prop, val in split_decls(body):
            if prop and prop.startswith("--") and prop not in target:
                target[prop] = val.strip()
        if prelude.startswith("@"):
            for k, v in collect_vars(body).items():
                other_attrs.setdefault(k, v)
    merged = {}
    merged.update(other_attrs)
    merged.update(root_attrs)
    return merged


def resolve_vars(val, depth=0):
    """把值里的 var(--x[, fallback]) 展开为字面量。

    用手工扫描而非正则：fallback 本身可以是 var(...)，正则无法匹配嵌套括号，
    会导致外层的 var() 残留到下一次执行才被展开（破坏幂等性）。
    解析不出结果时原样保留 token，绝不返回空串吞掉颜色。
    """
    if depth > 5 or "var(" not in val:
        return val

    out, i = [], 0
    while i < len(val):
        j = val.find("var(", i)
        if j < 0:
            out.append(val[i:])
            break
        out.append(val[i:j])
        k = j + 4
        m = re.match(r"\s*(--[\w-]+)\s*", val[k:])
        if not m:
            out.append("var(")
            i = j + 4
            continue
        name = m.group(1)
        k += m.end()

        fallback = None
        if k < len(val) and val[k] == ",":
            k += 1
            s, d = k, 0
            while k < len(val):
                c = val[k]
                if c == "(":
                    d += 1
                elif c == ")":
                    if d == 0:
                        break
                    d -= 1
                k += 1
            fallback = val[s:k].strip()
        if k < len(val) and val[k] == ")":
            k += 1

        if name in VAR_MAP:
            inner = resolve_vars(VAR_MAP[name], depth + 1)
            if inner.strip():
                out.append(inner)
            elif fallback:
                out.append(resolve_vars(fallback, depth + 1))
            else:
                out.append(val[j:k])
        elif fallback:
            out.append(resolve_vars(fallback, depth + 1))
        else:
            out.append(val[j:k])
        i = k
    return "".join(out)


# ---------------------------------------------------------------- 颜色工具

def _lin(v):
    v = v / 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


_COLOR_RE = re.compile(
    r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
    r"|rgba?\(\s*[^()]*?\)"
    r"|hsla?\(\s*[^()]*?\)"
    r"|\b(?:transparent|white|black|gray|grey|silver|paper)\b"
)


def parse_color(tok):
    """把颜色字面量解析为 (r,g,b,a)；透明返回 None。"""
    if tok is None:
        return None
    t = tok.strip().lower()
    if t.startswith("#"):
        h = t[1:]
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h[:3])
        else:
            h = h[:6]
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except ValueError:
            return None
        return (r, g, b, 1.0)
    m = re.match(r"rgba?\(([^)]*)\)", t)
    if m:
        nums = re.findall(r"[\d.]+", m.group(1))
        if len(nums) >= 3:
            r, g, b = (clamp255(float(x)) for x in nums[:3])
            a = float(nums[3]) if len(nums) > 3 else 1.0
            return (r, g, b, max(0.0, min(1.0, a)))
        return None
    if t in NAMED_COLORS:
        c = NAMED_COLORS[t]
        return None if c is None else (c[0], c[1], c[2], 1.0)
    return None


def clamp255(v):
    return int(max(0, min(255, round(v))))


def to_hex(rgb, alpha=None):
    if rgb is None:
        return None
    if len(rgb) == 4:
        a_new = rgb[3]
        rgb = rgb[:3]
        alpha = a_new if alpha is None else min(alpha, a_new)
    if alpha is not None and alpha < 0.999:
        a = max(0.0, min(1.0, alpha))
        r = clamp255(rgb[0] * a + 255 * (1 - a))
        g = clamp255(rgb[1] * a + 255 * (1 - a))
        b = clamp255(rgb[2] * a + 255 * (1 - a))
        rgb = (r, g, b)
    return "#%02x%02x%02x" % tuple(clamp255(c) for c in rgb)


def first_color(text):
    for tok in _COLOR_RE.findall(text):
        c = parse_color(tok)
        if c is not None:
            return c
    return None


# ------------------------------------------------------------ CSS 结构化

def iter_blocks(css):
    """产出顶层块：(prelude, body)。body 为 None 表示这是一条孤立语句或注释。"""
    i, n = 0, len(css)
    buf = []
    while i < n:
        ch = css[i]
        if css.startswith("/*", i):
            k = css.find("*/", i + 2)
            k = n if k < 0 else k + 2
            yield css[i:k], None
            i = k
            continue
        if ch == "{":
            depth, j = 1, i + 1
            while j < n:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            yield "".join(buf).strip(), css[i + 1:j]
            buf = []
            i = j + 1
            continue
        if ch == ";":
            piece = "".join(buf).strip()
            buf = []
            if piece:
                yield piece, None
            i += 1
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        yield tail, None


def split_decls(body):
    """按顶层分号切分声明，忽略括号内的分号。"""
    parts, cur, depth = [], [], 0
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth <= 0:
            parts.append("".join(cur))
            cur = []
            continue
        cur.append(ch)
    tail = "".join(cur)
    if tail.strip():
        parts.append(tail)
    out = []
    for p in parts:
        # 先剥离注释再判断：行尾注释会与下一条声明粘连成同一片段，
        # 若直接按 "以 /* 开头" 丢弃，会连带丢掉注释后面的真实声明。
        p = re.sub(r"/\*[\s\S]*?\*/", "", p).strip()
        if not p:
            continue
        if ":" in p:
            k, v = p.split(":", 1)
            out.append((k.strip(), v.strip()))
        else:
            out.append((None, p))
    return out


GRADIENT_RE = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", re.I)


def strip_gradients_from_value(val):
    """从值中移除所有 gradient() 调用，返回剩余文本。"""
    out, i = [], 0
    while i < len(val):
        m = GRADIENT_RE.search(val, i)
        if not m:
            out.append(val[i:])
            break
        out.append(val[i:m.start()])
        depth, j = 1, m.end()
        while j < len(val) and depth:
            if val[j] == "(":
                depth += 1
            elif val[j] == ")":
                depth -= 1
            j += 1
        out.append(" ")
        i = j
    return "".join(out)


def first_gradient(val):
    m = GRADIENT_RE.search(val)
    if not m:
        return None
    depth, j = 1, m.end()
    while j < len(val) and depth:
        if val[j] == "(":
            depth += 1
        elif val[j] == ")":
            depth -= 1
        j += 1
    return val[m.start():j]


def base_color_from_background(val):
    """从含渐变（或含 SVG data URI）的背景值中取出可用的纯色。"""
    if "svg+xml" in val.lower() and "gradient" in val.lower():
        # SVG 图案里带渐变，整块丢弃不安全，退化为纯白
        return (255, 255, 255, 1.0)
    rest = strip_gradients_from_value(val)
    c = first_color(rest)
    if c is not None:
        return c
    g = first_gradient(val)
    if g:
        c = first_color(g)
        if c is not None:
            return c
    return (255, 255, 255, 1.0)


def lighten_background(rgb):
    """深色背景映射到浅色带，保留原有明度次序。"""
    L = luminance(rgb)
    DARK = 0.45
    if L >= DARK:
        return rgb
    g = 238 + (max(0.0, L) / DARK) * 17.0
    g = clamp255(g)
    return (g, g, g)


def darken_text(rgb, bg, need):
    """按比例压暗文字颜色，直到满足对比度下限（保留色相，改动最小）。

    判定一律基于 to_hex 取整后的实际输出值：若按浮点判定，取整回落会让下一次
    执行判定为不达标并再压一档，产生逐次漂移。
    """
    if contrast(tuple(clamp255(c) for c in rgb), bg) >= need:
        return rgb
    for step in range(1, 101):
        t = step / 100.0
        cand = tuple(clamp255(c * (1 - t)) for c in rgb)
        if contrast(cand, bg) >= need:
            return cand
    return (0, 0, 0)


def pick_font_stack(resolved_lower):
    """按字体类型返回对应的系统字体栈，保留等宽 / 衬线的语义差异。"""
    if any(h in resolved_lower for h in MONO_HINTS):
        return MONO_FONT
    if any(h in resolved_lower for h in SERIF_HINTS):
        return SERIF_FONT
    return SYS_FONT


def normalize_px(val):
    """返回 val 对应的 px 数值；无法判定返回 None。"""
    m = re.match(r"^(-?\d*\.?\d+)\s*(px|pt|rem|em)?$", val.strip())
    if not m:
        return None
    v, unit = float(m.group(1)), (m.group(2) or "px")
    if unit == "pt":
        v *= 4.0 / 3.0
    elif unit == "rem":
        v *= 16.0
    return v


def sanitize_decls(body, is_body_rule=False):
    """净化一个规则体。返回新的声明文本。"""
    decls = split_decls(body)
    kept = []  # [(prop, val)]

    for prop, val in decls:
        if prop is None:
            continue

        # 统一前置：先展开 CSS 变量、再把半透明合成为不透明等效色。
        # 必须在做任何判断之前完成，否则「决策时看到的颜色」与「输出的颜色」
        # 不一致，第二次执行会产生漂移（幂等性破坏）。
        val = resolve_vars(val)
        val = compose_alpha(val)
        low = prop.lower()

        if low.startswith("--"):
            kept.append((prop, val))
            continue
        if low in DROP_PROPS:
            stat("drop_" + low.replace("-webkit-", ""))
            continue
        if low in ("@import", "import"):
            continue

        # 外部字体 -> 系统字体栈（先展开 CSS 变量再判定）
        if low == "font-family":
            resolved = resolve_vars(val).lower()
            if any(h in resolved for h in WEB_FONT_HINTS):
                val = pick_font_stack(resolved)
                stat("font_stack")
            kept.append((prop, val))
            continue

        # 渐变
        if GRADIENT_RE.search(val):
            if low in BGIMG_PROPS:
                kept.append((low, "none"))
                stat("gradient_removed")
                continue
            if low in BG_PROPS:
                c = base_color_from_background(val)
                kept.append((low, to_hex(c)))
                stat("gradient_removed")
                continue
            if low in ("background", "background-image", "-webkit-mask-image",
                       "mask-image", "list-style-image"):
                kept.append((low, "none"))
                stat("gradient_removed")
                continue

        # SVG data URI 里带渐变
        if low in BG_PROPS or low in BGIMG_PROPS:
            if "svg+xml" in val.lower() and "gradient" in val.lower():
                c = base_color_from_background(val)
                kept.append(("background-image" if low in BGIMG_PROPS else low,
                             to_hex(c) if low in BG_PROPS else "none"))
                stat("svg_pattern_removed")
                continue

        # 固定定位
        if low == "position" and val.strip().lower() in ("fixed", "sticky"):
            kept.append((low, "static"))
            stat("fixed_removed")
            continue

    # 半透明
        # 注意：必须「丢弃」而非钳到 1。
        # 这些页面大量用 opacity:0 + animation 做入场动画，动画已被移除，
        # 若保留 opacity:0 元素将永久不可见。
        if low in OPACITY_PROPS:
            try:
                if float(val.strip()) < 0.999:
                    stat("opacity_removed")
                    continue
            except ValueError:
                pass

        # 过细字重
        if low == "font-weight":
            try:
                w = int(float(val.strip()))
                if w < 400:
                    val = "400"
                    stat("thin_weight")
            except ValueError:
                pass
            kept.append((prop, val))
            continue

        kept.append((prop, val))

    # ---- 第二轮：颜色对比度与字号 ----
    ft_px = None
    bold = False
    for prop, val in kept:
        low = prop.lower()
        if low == "font-size":
            ft_px = normalize_px(val)
        elif low == "font-weight":
            lv = val.strip().lower()
            try:
                bold = lv == "bold" or int(float(lv)) >= 700
            except ValueError:
                bold = lv in ("bold", "bolder")

    # 规则自身的最终背景色。必须先经过「深色翻浅」变换再用于文字对比度判定，
    # 否则浅色文字会因「当时的深色背景」被判为合格，背景翻浅后落得浅字压浅底。
    # 同一块内多条背景声明按 CSS 层叠取最后一条。
    own_bg = None
    for prop, val in kept:
        if prop.lower() in BG_PROPS:
            c = parse_color(val) or first_color(val)
            if c is not None:
                own_bg = lighten_background(c[:3])
    bg = own_bg if own_bg is not None else (255, 255, 255)

    out = []
    for prop, val in kept:
        low = prop.lower()
        rval = resolve_vars(val)

        # 背景：过深翻浅
        if low in BG_PROPS:
            c = parse_color(rval)
            if c is None:
                c = first_color(rval)
            if c is not None:
                # bg 已在块级统一按「翻浅后」的值算好，此处保持一致即可
                new_rgb = lighten_background(c[:3])
                if new_rgb != c[:3]:
                    stat("bg_lightened")
                    val = to_hex(new_rgb)
                bg = new_rgb
            out.append((prop, val))
            continue

        # 前景色：对比度兜底
        if low in FG_PROPS:
            c = parse_color(rval)
            if c is None:
                c = first_color(rval)
            if c is not None:
                rgb = c[:3]
                need = CONTRAST_NORMAL
                if ft_px is not None and (ft_px >= 24 or (bold and ft_px >= 18.66)):
                    need = CONTRAST_LARGE
                if contrast(rgb, bg) < need:
                    new_rgb = darken_text(rgb, bg, need)
                    val = to_hex(new_rgb)
                    stat("text_darkened")
                elif c[3] < 0.999:
                    val = to_hex(c)
            out.append((prop, val))
            continue

        # 边框色：过浅则加深，保证分栏线可见
        if low.startswith("border") and low.endswith("color"):
            c = parse_color(rval) or first_color(rval)
            if c is not None and luminance(c[:3]) > 0.75:
                val = "#b8b8b8"
                stat("border_enforced")
            out.append((prop, val))
            continue

        # 字号兜底
        if low == "font-size":
            px = normalize_px(val)
            if px is not None:
                floor = BODY_MIN_FONT_PX if is_body_rule else MIN_FONT_PX
                if px < floor:
                    val = "%.0fpx" % floor
                    stat("font_bumped")
            out.append((prop, val))
            continue

        # 行高兜底（仅无单位写法）
        if low == "line-height":
            v = val.strip()
            try:
                f = float(v)
                if f < MIN_LINE_HEIGHT:
                    v = str(FALLBACK_LINE_HEIGHT)
                    stat("line_bumped")
            except ValueError:
                pass
            out.append((prop, v))
            continue

        out.append((prop, val))

    body_text = ";\n  ".join("%s:%s" % (p, v) for p, v in out)
    return ("\n  " + body_text + ";\n") if body_text else "\n"


def compose_alpha(val):
    """把值里的 rgba(...a<1) 合成为不透明白底等效色。"""
    def repl(m):
        tok = m.group(0)
        c = parse_color(tok)
        if c is None:
            return tok
        if c[3] >= 0.999:
            return to_hex(c[:3])
        r = clamp255(c[0] * c[3] + 255 * (1 - c[3]))
        g = clamp255(c[1] * c[3] + 255 * (1 - c[3]))
        b = clamp255(c[2] * c[3] + 255 * (1 - c[3]))
        stat("alpha_composited")
        return "#%02x%02x%02x" % (r, g, b)
    return re.sub(r"rgba?\([^()]*\)", repl, val)


def process_css(css):
    out = []
    for prelude, body in iter_blocks(css):
        if body is None:
            if prelude.startswith("/*") or not prelude:
                continue
            if prelude.lower().startswith("@import"):
                stat("import_removed")
                continue
            if prelude.lower().startswith("@charset"):
                continue
            continue
        p = prelude.strip()
        plow = p.lower().replace(" ", "")
        if "@keyframes" in plow or "@-webkit-keyframes" in plow:
            stat("keyframes_removed")
            continue
        if "@font-face" in plow:
            stat("fontface_removed")
            continue
        if "prefers-color-scheme:dark" in plow:
            stat("darkmq_removed")
            continue
        if p.startswith("@"):
            inner = process_css(body)
            if inner.strip():
                out.append(p + " {" + inner + "}")
            continue

        is_body = re.search(r"(^|,)\s*(html|body)\s*(,|$)", p) is not None
        new_body = sanitize_decls(body, is_body_rule=is_body)
        if new_body.strip():
            out.append(p + " {" + new_body + "}")
    return "\n".join(out)


# ------------------------------------------------------------ HTML 处理

STYLE_RE = re.compile(r"<style[^>]*>([\s\S]*?)</style>", re.I)
GFONT_LINK_RE = re.compile(
    r"\s*<link[^>]+href=[\"'][^\"']*fonts\.(?:googleapis|gstatic)\.com[^\"']*[\"'][^>]*>",
    re.I)
COLOR_SCHEME_META_RE = re.compile(
    r"\s*<meta[^>]+name=[\"']color-scheme[\"'][^>]*>", re.I)
BG_ATTR_RE = re.compile(r"\s+(?:bgcolor|background|text|link|vlink|alink)\s*=\s*\"[^\"]*\"", re.I)
# 内联 SVG 的呈现属性（不在 CSS 里，需单独处理）
SVG_COLOR_ATTR_RE = re.compile(
    r"""\b(fill|stroke|stop-color|flood-color|lighting-color)=(["'])(rgba?\([^"']*\))\2""")
SVG_OPACITY_ATTR_RE = re.compile(
    r"""\s+(?:opacity|fill-opacity|stroke-opacity)=(["'])(?:0?\.\d+)\1""")
INLINE_STYLE_DQ_RE = re.compile(r'style\s*=\s*"([^"]*)"')
INLINE_STYLE_SQ_RE = re.compile(r"style\s*=\s*'([^']*)'")

# ---- 区块标记 ----
# 用于识别「已处理」的文件：二次运行时只取 LEGACY 段，避免把 base 与保证规则
# 反复叠加导致 "</style>" 无限膨胀。
M_BASE = ("/* <<EINK:BASE>> */", "/* <</EINK:BASE>> */")
M_LEGACY = ("/* <<EINK:LEGACY>> */", "/* <</EINK:LEGACY>> */")
M_GUARANTEE = ("/* <<EINK:GUARANTEE>> */", "/* <</EINK:GUARANTEE>> */")
REPROCESSED_RE = re.compile(
    re.escape(M_LEGACY[0]) + r"([\s\S]*?)" + re.escape(M_LEGACY[1]))

GUARANTEE_CSS = """
/* ---- E-Ink 保证性规则（置于末尾，同优先级下生效） ---- */
html{-webkit-text-size-adjust:100%;color-scheme:light}
body{background:#ffffff!important;color:#000000!important;
  font-size:17px!important;line-height:1.85!important;
  font-family:__SYSFONT__}
*{box-sizing:border-box}
@media print{
  body{background:#fff!important;color:#000!important}
  [class]{break-inside:avoid;page-break-inside:avoid}
}
""".replace("__SYSFONT__", SYS_FONT)


def sanitize_inline_style(val):
    if not val.strip():
        return val
    if GRADIENT_RE.search(val) or any(c in val for c in ("#", "rgb")):
        pass
    new = sanitize_decls(val)
    new = re.sub(r"\s*\n\s*", " ", new).strip()
    new = new.rstrip(";").strip()
    return new


def process_html(html, base_css):
    stats_budget = dict(STATS)
    # 外部资源与遗留属性
    html = GFONT_LINK_RE.sub("", html)
    if GFONT_LINK_RE is None:
        pass
    html = COLOR_SCHEME_META_RE.sub("", html)
    html = BG_ATTR_RE.sub("", html)

    # 内联 SVG：半透明填充合成为不透明等效色；去掉透明度属性
    html = SVG_COLOR_ATTR_RE.sub(
        lambda m: '%s="%s"' % (m.group(1), compose_alpha(m.group(2))), html)
    html = SVG_OPACITY_ATTR_RE.sub("", html)

    # 行内样式净化（双引号与单引号两种写法）
    def _inline(m):
        new = sanitize_inline_style(m.group(1))
        if not new:
            return ""
        return 'style="%s"' % new

    html = INLINE_STYLE_DQ_RE.sub(_inline, html)
    html = INLINE_STYLE_SQ_RE.sub(_inline, html)

    # 抽取并净化所有 <style>
    styles = STYLE_RE.findall(html)
    joined = "\n".join(styles)
    already = REPROCESSED_RE.search(joined)
    legacy = already.group(1) if already else joined
    VAR_MAP.clear()
    VAR_MAP.update(collect_vars(legacy))
    new_style = "<style>\n" + "\n".join([
        M_BASE[0], base_css.strip(), M_BASE[1],
        M_LEGACY[0], process_css(legacy).strip(), M_LEGACY[1],
        M_GUARANTEE[0], GUARANTEE_CSS.strip(), M_GUARANTEE[1],
    ]) + "\n</style>"

    first = STYLE_RE.search(html)
    html = html[:first.start()] + new_style + html[first.end():]
    html = STYLE_RE.sub(lambda m: "", html, count=0) if False else html
    # 移除其余 style 块
    rest = list(STYLE_RE.finditer(html))
    for m in reversed(rest[1:]):
        html = html[:m.start()] + html[m.end():]

    return html


# ------------------------------------------------------------ 校验

BANNED_PATTERNS = [
    ("gradient", re.compile(r"(linear|radial|conic|repeating-linear|repeating-radial)-gradient\s*\(", re.I)),
    ("box-shadow", re.compile(r"box-shadow\s*:", re.I)),
    ("text-shadow", re.compile(r"text-shadow\s*:", re.I)),
    ("filter", re.compile(r"(backdrop-)?filter\s*:\s*(?!none)", re.I)),
    ("animation", re.compile(r"animation\s*:|\sanimation-", re.I)),
    ("transition", re.compile(r"transition\s*:|\stransition-", re.I)),
    ("transform", re.compile(r"(?<![-\w])transform\s*:\s*(?!none)", re.I)),
    ("position:fixed", re.compile(r"position\s*:\s*fixed", re.I)),
    ("rgba alpha", re.compile(r"rgba?\([^()]*,\s*0?\.\d", re.I)),
    ("opacity<1", re.compile(r"opacity\s*:\s*0?\.\d", re.I)),
    ("external font", re.compile(r"fonts\.(googleapis|gstatic)\.com", re.I)),
    ("prefers-color-scheme dark", re.compile(r"prefers-color-scheme\s*:\s*dark", re.I)),
    ("keyframes", re.compile(r"@keyframes", re.I)),
    ("@font-face", re.compile(r"@font-face", re.I)),
]


def verify_html(html, path):
    problems = []
    for name, rx in BANNED_PATTERNS:
        if rx.search(html):
            problems.append(name)
    # 字号
    sizes = [float(x) for x in re.findall(r"font-size\s*:\s*([0-9.]+)px", html)]
    if sizes and min(sizes) < MIN_FONT_PX - 0.01:
        problems.append("font<%.0fpx(%.1f)" % (MIN_FONT_PX, min(sizes)))
    # 深色背景
    for c in re.findall(r"background(?:-color)?\s*:\s*(#[0-9a-fA-F]{6})", html):
        h = c[1:]
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        if luminance(rgb) < 0.45:
            problems.append("dark-bg %s" % c)
            break
    return problems


# ------------------------------------------------------------ 主流程

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="*")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    base_css = open(BASE_CSS, encoding="utf-8").read()

    files = []
    for d in TARGET_DIRS:
        files.extend(sorted(glob.glob(os.path.join(d, args.only + ".html"))))
    files.sort()
    if not files:
        print("no files matched")
        return 1

    print("targets: %d" % len(files))
    bad = []
    for p in files:
        html = open(p, encoding="utf-8").read()
        if args.verify:
            probs = verify_html(html, os.path.basename(p))
            if probs:
                bad.append((os.path.basename(p), probs))
            continue
        new = process_html(html, base_css)
        if not args.dry_run and new != html:
            open(p, "w", encoding="utf-8", newline="\n").write(new)
        probs = verify_html(new, p)
        if probs:
            bad.append((os.path.basename(p), probs))

    if args.verify:
        print("\n=== VERIFY ===")
    else:
        print("\n=== STATS ===")
        for k in sorted(STATS):
            print("  %-24s %d" % (k, STATS[k]))

    print("\n=== FILES WITH REMAINING ISSUES: %d ===" % len(bad))
    for name, probs in bad[:40]:
        print("  %-32s %s" % (name, ", ".join(probs)))
    if len(bad) > 40:
        print("  ... (%d more)" % (len(bad) - 40))
    return 0


if __name__ == "__main__":
    sys.exit(main())
