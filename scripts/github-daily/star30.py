#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Count stars added in last 30 days via GitHub stargazers starred_at (real data)."""
import subprocess, json, sys
from datetime import datetime, timezone, timedelta

TOK=subprocess.check_output(["gh","auth","token"],text=True).strip()
CUT=datetime(2026,8,15,tzinfo=timezone.utc)  # 30 days before 2026-09-14

def count30(repo):
    # total stargazers
    total=int(subprocess.check_output(["gh","api","repos/"+repo,"--jq",".stargazers_count"],text=True).strip())
    n=total; got=0; inc=0
    page=(total+99)//100  # last page
    while True:
        url=f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page={page}"
        p=subprocess.run(["curl","-s","-H","Authorization: bearer "+TOK,
                          "-H","Accept: application/vnd.github.star+json","--max-time","50",url],
                         capture_output=True,text=True)
        try:
            arr=json.loads(p.stdout)
        except Exception as e:
            print(repo,page,"json err",p.stdout[:80]); break
        if not arr: break
        got+=len(arr)
        for it in arr:
            sa=datetime.fromisoformat(it["starred_at"].replace("Z","+00:00"))
            if sa>=CUT: inc+=1
        # move to earlier page; if we've covered well below the cutoff we can stop
        page-=1
        if page<1 or got> total+200: break
        # early stop: the earliest item of this page is the newest of this page
        # if the whole page is before CUT and we already passed, break
        oldest_in_page = min(datetime.fromisoformat(i["starred_at"].replace("Z","+00:00")) for i in arr)
        if oldest_in_page < CUT and page < (total+99)//100:
            # page fully or partially older; but keep counting this page above; stop scanning older pages
            break
    return inc

for repo in ["evidentlyai/evidently","CopilotKit/OpenBot","slothflowlabs/duckle",
             "AltimateAI/altimate-code","0xMassi/webclaw"]:
    inc=count30(repo)
    print(repo,"30d +",inc)
