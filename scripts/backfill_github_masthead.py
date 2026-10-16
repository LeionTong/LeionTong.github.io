#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回补 Daily-Github 单期报头（h1 / .mh-sub / .mh-top 期次 / <title>）。

背景：09-14 起 h1 退化成栏目固定名「GitHub 每日优质项目」、.mh-sub 退化成固定模板句，
索引卡片（标题取 h1、摘要取 mh-sub）连续多期一模一样，失去辨识度。
本脚本按各期自有内容（lede / mh-sub / 条目）重写报头三件套，与 Daily-AI / Daily-Terminal 对齐。
幂等：只替换这四处。
"""
import pathlib
import re
import sys

HUGO = pathlib.Path(r"C:\Users\Leion\T\LeionTong.github.io-hugo")
SD = HUGO / "static" / "daily-github"

# (slug, NO, h1, mh-sub | None=保留原值)
ROWS = [
    ("2026-09-14-1109", 11,
     "Agent 从聊天框走向自主执行，上下文与取数层成为采购项",
     "本期收录图原生上下文与溯源基础设施 Semantica、给每个 Agent 配一台电脑的 OpenBot、本地优先 Agent、基于 DuckDB 的自托管 ETL Duckle 与本地网页抽取 webclaw：Agent 正从回答问题走向操作用户的浏览器与本机，被买账的是它脚下的上下文与取数层。"),
    ("2026-09-15-1038", 12,
     "Agent 的治理先于智能，策略门禁与隔离工作区同日出现",
     "本期收录带 CEL 策略门禁的 OpenBot、可被 Agent 读写的开源 3D 编辑器 editor、按项目分配 Incus 隔离工作区的 AgentVerse-OS、收拢六个 coding agent 的启动器与本地短视频生产线 OpenShorts：方向是把操作权关进策略与隔离，把数据留在本机。"),
    ("2026-09-16-1020", 13,
     "把付费 SaaS 与云端推理搬回自己机器",
     "本期收录阿里 open-code-review、纯 C 零依赖的 MoE 推理引擎 colibri、自托管销售 OS DeskcommCRM、多智能体投研终端与 SSH 原生隔离运行时 Containarium：一类自托管替代代码评审、CRM 与研报终端，一类把模型推理搬回本地机器。"),
    ("2026-09-17-1022", 14,
     "Agent 补齐取数与交付能力，评测与端侧基建同步硬化",
     "本期收录免 API 钥读取社媒的 Agent-Reach、直接产出原生 PPTX 的 ppt-master、RLVR 隔离评测 VeriRun、边缘视频分析引擎 cosmo-edge 与把 coding agent 变成研究 agent 的 OpenResearch：一边补 Agent 的具体能力，一边把订阅费与云依赖往本地搬。"),
    ("2026-09-18-1012", 15,
     "安全审计、真登录浏览器与 Agent 界面层同周补齐",
     "本期收录 Cloudflare 的 agent 安全审计 skill、腾讯用真实已登录浏览器的 BrowserSkill、选区即用的网页 Agent、抖音直播电商 Agent Studio 与面向 agentic 界面的 React 设计系统：替代对象是按席位计费的审计、浏览器自动化与 UI 套件。"),
    ("2026-09-19-1829", 16,
     "Agent 基础设施自托管化，浏览器到沙箱五层均为宽松许可",
     None),
    ("2026-09-20-1008", 17,
     "Agent 商业化两头分化，降本基建与带定价的垂直蓝图并存",
     None),
    ("2026-09-21-1015", 18,
     "投入从更聪明的模型转向可控可审计的 Agent 管道",
     None),
    ("2026-09-23-1132", 19,
     "Agent 的执行环境被拆成可单独售卖的一层",
     None),
    ("2026-09-24-1030", 20,
     "把模型要处理的信息压成更小的结构",
     None),
    ("2026-09-25-1025", 21,
     "编排、工作区、检索、记忆与调试，Agent 底座被逐层补齐",
     "本期收录多 Agent 编排层 Omnigent、自托管 AI 工作区 Odysseus、面向 AI 的数据搜索引擎 XERJ、Git 原生 Agent 记忆 OKF 与 x64dbg 的 MCP 插件：本周标的共同指向同一件事——给 Agent 配齐运行时、检索、记忆与调试环境。"),
    ("2026-10-15-1721", 22,
     "账单与数据边界一起往下压，端侧推理与小模型决策同步出现",
     "本期收录 12GB 显存跑 125B 的本地推理引擎 Strata、替代 LLM 做决策的 Laya、纯 CPU 的 Indra OCR、schema 约束输出的 TypeLLM 与写不可读的日志加密库 Scuttle：五项都在把调用云端模型这一步换掉或压小。"),
    ("2026-10-16-0945", 23,
     "Agent 的产出扩到 CAD 图档、音频栈与机器人控制回路",
     "本期收录给 coding agent 装上 CAD 的 text-to-cad、跨供应商切换模型的 magpie、纯 C++ 音频运行时 audio.cpp、智能眼镜运行时 MentraOS 与机器人实时中间件 HORUS：Agent 的产出正从文本扩到工程文件与物理设备。"),
]


def main() -> int:
    changed = 0
    for slug, no, h1, mh in ROWS:
        p = SD / f"{slug}.html"
        if not p.exists():
            print(f"缺文件：{p}")
            return 1
        raw = p.read_text(encoding="utf-8", newline="")
        date, hhmm = slug.split("-")[0] + "-" + slug.split("-")[1] + "-" + slug.split("-")[2], slug.split("-")[3]
        hhmm_fmt = f"{hhmm[:2]}:{hhmm[2:]}"
        orig = raw

        raw = re.sub(r"<title>[\s\S]*?</title>",
                     f"<title>LEION · DAILY GITHUB NO.{no:02d} — {date}</title>", raw, count=1)
        raw = re.sub(r"<div class=\"mh-top\">[\s\S]*?</div>",
                     f'<div class="mh-top"><b>LEION · DAILY GITHUB</b>'
                     f'<span>NO.{no:02d} · {date} · {hhmm_fmt} GMT+8</span></div>', raw, count=1)
        raw, n1 = re.subn(r"<h1>[\s\S]*?</h1>", f"<h1>{h1}</h1>", raw, count=1)
        assert n1 == 1, slug
        if mh:
            raw, n2 = re.subn(r'<p class="mh-sub">[\s\S]*?</p>',
                              f'<p class="mh-sub">{mh}</p>', raw, count=1)
            assert n2 == 1, slug
        if raw != orig:
            p.write_text(raw, encoding="utf-8", newline="")
            changed += 1
            print(f"OK {slug} NO.{no:02d} | {h1}")
    print(f"共改写 {changed} 期")
    return 0


if __name__ == "__main__":
    sys.exit(main())
