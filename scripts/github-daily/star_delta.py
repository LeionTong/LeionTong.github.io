#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30-day star delta: calibrate star-history curve using creation(=0) and today(=API stars)."""
import re, os, subprocess
from datetime import date
TOK=subprocess.check_output(["gh","auth","token"],text=True).strip()
tmp=os.environ.get("LOCALAPPDATA")+"/Temp"
TODAY=date(2026,9,14)

def parse_path(d):
    m=re.match(r"M\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*(.*)", d.strip())
    if not m: return []
    cx,cy=float(m.group(1)),float(m.group(2)); pts=[(cx,cy)]
    nums=[float(v) for v in re.findall(r"-?(?:\d+\.?\d*|\.\d+)", m.group(3))]
    def cb(p0,p1,p2,p3,n=16):
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

repos=[("evidentlyai/evidently","2020-11-25",7913),
       ("CopilotKit/OpenBot","2026-08-17",4857),
       ("slothflowlabs/duckle","2026-05-21",1297),
       ("AltimateAI/altimate-code","2026-02-27",811),
       ("0xMassi/webclaw","2026-03-10",2342)]
for repo,cd,cur in repos:
    fn=os.path.join(tmp,"sh_%s.svg"%repo.replace("/","_"))
    subprocess.run(["curl","-sL","--max-time","50","-H","Authorization: bearer "+TOK,
                    "https://api.star-history.com/svg?repos=%s&theme=light"%repo,"-o",fn],check=True)
    svg=open(fn,encoding="utf-8").read()
    colored=re.findall(r'<path fill="none" stroke="#[0-9a-fA-F]{6}"[^>]*d="([^"]+)"', svg)
    best=None
    for d in colored:
        pts=parse_path(d)
        if len(pts)<40: continue
        if best is None or pts[-1][1]<best[-1][1]: best=pts
    if best is None: print(repo,"nopath"); continue
    pts=best
    y0=pts[0][1]; y1=pts[-1][1]; x0=pts[0][0]; x1=pts[-1][0]
    if abs(y1-y0)<1e-6: print(repo,"flat"); continue
    def stars(y): return cur*(y0-y)/(y0-y1)
    created=date(*map(int,cd.split("-"))); days=(TODAY-created).days
    def xfordate(d): return x0+(d-x0)*(x1-x0)/max((x1-x0),1)  # placeholder
    def dayoffset(off): return x1 + (off/30.0)*((x1-x0)/ (days/30.0)) if False else x1-(30.0*((x1-x0)/days))
    x30=x1-30*((x1-x0)/days)
    past=stars(min(pts,key=lambda p:abs(p[0]-x30))[1])
    print("%-28s curapi=%d  read_cur=%.0f  delta≈%+.0f"%(repo,cur,stars(y1),cur-past))
