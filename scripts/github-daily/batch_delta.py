#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, subprocess, json, time
from datetime import date
TOK=subprocess.check_output(["gh","auth","token"],text=True).strip()
tmp=os.environ.get("LOCALAPPDATA")+"/Temp"
TODAY=date(2026,9,14)

cands=["Zleap-AI/SAG","getnao/nao","Kaelio/ktx","ENTERPILOT/GoModel","fuyuxiang/echo-agent",
       "astronomer/agents","rocky-data/rocky","AtomicBot-ai/atomic-agent","codedogQBY/ReadAny",
       "ClemensElflein/OpenMower","einsteinpy?x","netease-youdao/EmotiVoice2","x","whiteguo233/OpenBiliClaw",
       "semantica-agi/semantica","codedogQBY/ReadAny","adjust?x","mehdiirh/defog","x",
       "marin-community/marin","ttofum/punkt","x","jundot/omlx","p-e-w/heretic"]

def meta(repo):
    try:
        d=json.loads(subprocess.check_output(["gh","api","repos/"+repo,"--jq",
          "{s:.stargazers_count,c:.created_at,l:.language,lic:.license.spdx_id,p:.pushed_at}"],text=True).encode().decode())
        return d
    except Exception as e:
        return None

def parse_path(d):
    m=re.match(r"M\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*(.*)", d.strip())
    if not m: return []
    cx,cy=float(m.group(1)),float(m.group(2)); pts=[(cx,cy)]
    nums=[float(v) for v in re.findall(r"-?(?:\d+\.?\d*|\.\d+)", m.group(3))]
    def cb(p0,p1,p2,p3,n=14):
        o=[]
        for i in range(n+1):
            t=i/n; mt=1-t
            o.append((mt**3*p0[0]+3*mt*mt*t*p1[0]+3*mt*t*t*p2[0]+t**3*p3[0],
                      mt**3*p0[1]+3*mt*mt*t*p1[1]+3*mt*t*t*p2[1]+t**3*p3[1]))
        return o
    for k in range(0,len(nums)-5,6):
        dx1,dy1,dx2,dy2,dx,dy=nums[k:k+6]
        p0=(cx,cy); p1=(cx+dx1,cy+dy1); p2=(cx+dx2,cy+dy2); p3=(cx+dx,cy+dy)
        pts+=cb(p0,p1,p2,p3); cx,cy=p3
    return pts

def delta(repo, cd, cur):
    fn=os.path.join(tmp,"sh_%s.svg"%repo.replace("/","_"))
    subprocess.run(["curl","-sL","--max-time","45","-H","Authorization: bearer "+TOK,
                    "https://api.star-history.com/svg?repos=%s&theme=light"%repo,"-o",fn])
    try: svg=open(fn,encoding="utf-8").read()
    except: return None
    colored=re.findall(r'<path fill="none" stroke="#[0-9a-fA-F]{6}"[^>]*d="([^"]+)"', svg)
    best=None
    for d in colored:
        pts=parse_path(d)
        if len(pts)<40: continue
        if best is None or pts[-1][1]<best[-1][1]: best=pts
    if best is None: return None
    pts=best
    y0=pts[0][1]; y1=pts[-1][1]; x0=pts[0][0]; x1=pts[-1][0]
    if abs(y1-y0)<1e-6: return None
    def stars(y): return cur*(y0-y)/(y0-y1)
    created=date(*map(int,cd.split("-"))); days=max((TODAY-created).days,1)
    x30=x1-30*((x1-x0)/days)
    past=stars(min(pts,key=lambda p:abs(p[0]-x30))[1])
    return cur-past

seen=set()
for repo in cands:
    if repo=="x" or repo in seen: continue
    seen.add(repo)
    m=meta(repo)
    if not m: continue
    cur=m["s"]
    d=delta(repo, m["c"][:10], cur)
    print("%-40s star=%d lang=%s lic=%s pushed=%s  d30=%s"%(
        repo,cur,m["l"],m["lic"],m["p"][:10], ("%+.0f"%d) if d is not None else "NA"))
    time.sleep(1)
