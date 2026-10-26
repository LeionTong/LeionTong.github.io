#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""近 30 天 star 增量：主用 stargazers starred_at 实测，接口不可用时回退 star-history.com 曲线推算。"""
import os, re, sys, json, subprocess, time
from datetime import datetime, timezone, timedelta

TOK = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
CUT = datetime.now(timezone.utc) - timedelta(days=30)
TODAY = datetime.now().date()
SCRATCH = os.environ.get("TMPDIR") or os.path.join(os.environ.get("LOCALAPPDATA", "."), "Temp")


def meta(repo):
    return json.loads(subprocess.check_output(
        ["gh", "api", "repos/" + repo, "--jq", "{s:.stargazers_count,c:.created_at}"], text=True))


def via_api(repo, total):
    page = (total + 99) // 100
    inc = 0
    while page >= 1:
        p = subprocess.run(["gh", "api", "repos/%s/stargazers?per_page=100&page=%d" % (repo, page),
                            "-H", "Accept: application/vnd.github.star+json"],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return None
        try:
            arr = json.loads(p.stdout)
        except Exception:
            return None
        if not isinstance(arr, list) or not arr or "starred_at" not in arr[0]:
            return None
        for it in arr:
            sa = datetime.fromisoformat(it["starred_at"].replace("Z", "+00:00"))
            if sa >= CUT:
                inc += 1
        oldest = min(datetime.fromisoformat(i["starred_at"].replace("Z", "+00:00")) for i in arr)
        if oldest < CUT:
            break
        page -= 1
    return inc


def curve_points(d):
    m = re.match(r"M\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*(.*)", d.strip())
    if not m:
        return []
    cx, cy = float(m.group(1)), float(m.group(2))
    pts = [(cx, cy)]
    nums = [float(v) for v in re.findall(r"-?(?:\d+\.?\d*|\.\d+)", m.group(3))]

    def cb(p0, p1, p2, p3, n=16):
        o = []
        for i in range(n + 1):
            t = i / n
            mt = 1 - t
            o.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                      mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
        return o

    for k in range(0, len(nums) - 5, 6):
        dx1, dy1, dx2, dy2, dx, dy = nums[k:k + 6]
        p0, p1, p2, p3 = (cx, cy), (cx + dx1, cy + dy1), (cx + dx2, cy + dy2), (cx + dx, cy + dy)
        pts += cb(p0, p1, p2, p3)
        cx, cy = p3
    return pts


def via_starhistory(repo, cur, created):
    fn = os.path.join(SCRATCH, "sh_%s.svg" % repo.replace("/", "_"))
    subprocess.run(["curl", "-sL", "--max-time", "50",
                    "https://api.star-history.com/svg?repos=%s&theme=light" % repo, "-o", fn])
    try:
        svg = open(fn, encoding="utf-8").read()
    except OSError:
        return None
    cands = re.findall(r'<path fill="none" stroke="#[0-9a-fA-F]{6}"[^>]*d="([^"]+)"', svg)
    best = None
    for d in cands:
        pts = curve_points(d)
        if len(pts) < 40:
            continue
        if best is None or pts[-1][1] < best[-1][1]:
            best = pts
    if best is None:
        return None
    pts = best
    y0, y1 = pts[0][1], pts[-1][1]
    x0, x1 = pts[0][0], pts[-1][0]
    if abs(y1 - y0) < 1e-6:
        return None

    def stars(y):
        return cur * (y0 - y) / (y0 - y1)

    days = max((TODAY - created).days, 1)
    x30 = x1 - 30 * ((x1 - x0) / days)
    past = stars(min(pts, key=lambda p: abs(p[0] - x30))[1])
    return cur - past


def count30(repo):
    m = meta(repo)
    cur = m["s"]
    created = datetime.fromisoformat(m["c"].replace("Z", "+00:00")).date()
    inc = via_api(repo, cur)
    if inc is not None:
        return inc, "api"
    return via_starhistory(repo, cur, created), "star-history"


for repo in sys.argv[1:]:
    inc, src = count30(repo)
    if inc is None:
        print("%-38s 未获取到" % repo)
    else:
        print("%-38s 30d +%d (%s)" % (repo, round(inc), src))
    time.sleep(0.5)
