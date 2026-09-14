#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, subprocess
TOK = subprocess.check_output(["gh","auth","token"], text=True).strip()
tmp = os.environ.get("LOCALAPPDATA") + "/Temp"
repos = ["slothflowlabs/duckle"]

def parse_path(d):
    m=re.match(r"M\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*(.*)", d.strip())
    if not m: return []
    cx,cy=float(m.group(1)),float(m.group(2)); pts=[(cx,cy)]
    nums=[float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", m.group(3))]
    def cb(p0,p1,p2,p3,n=10):
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

fn=os.path.join(tmp,"sh_slothflowlabs_duckle.svg")
svg=open(fn,encoding="utf-8").read()
# all month ticks: text with month name inside a transform
for m in re.finditer(r'<text[^>]*transform="translate\(([-\d.]+) [-\d.]+\)"[^>]*>([A-Za-z]+)</text>', svg):
    print("tick x=%s %s"%(m.group(1),m.group(2)))
# list fill=none paths
for p in re.finditer(r'<path fill="none"[^>]*?d="([^"]+)"', svg):
    d=p.group(1)
    xs=[float(v) for v in re.findall(r"(-?\d+\.\d+),", d)]
    ms=re.search(r'M\s*(-?[\d.]+)',d)
    print("path starts x0=%s len=%d first30chars=%s"%(ms.group(1) if ms else '?', len(d), d[:40]))
