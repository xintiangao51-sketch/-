# -*- coding: utf-8 -*-
from pathlib import Path
ROOT = Path(r"D:\\知识库")
FILES = [
    "00-工作台/首页-项目驾驶舱.md",
    "00-工作台/知识库健康度报告.md",
    "00-工作台/新疆工程造价智能工作台V2.0建设任务书.md",
    "00-工作台/快速入口.md",
    "00-工作台/W-知识库重构记录-P1-P2_20260621.md",
]
for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        print("miss", rel); continue
    t = p.read_text(encoding="utf-8")
    t2 = t.replace("05-数据资产", "15-数据资产")
    if t != t2:
        p.write_text(t2, encoding="utf-8")
        print("updated", rel)
    else:
        print("no-op", rel)
