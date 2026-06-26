#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final definitive link fixer — handles all remaining patterns in one pass"""
import io, sys, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path("D:/知识库")
BS = chr(92)

# Build full index
idx = {}
for f in VAULT.rglob("*.md"):
    rel = str(f.relative_to(VAULT)).replace(BS, "/")
    idx[f.stem.lower()] = rel
    idx[f.stem] = rel
    idx[rel] = rel
    idx[rel.replace(".md", "")] = rel

cnt = 0
IGN = {".obsidian",".claude",".archive",".tools",".git",".skillhub-install",".claudian","99-归档库"}

fixes_applied = {
    # health report bare names
    "[[10-索引与导航/标签体系]]": "[[10-索引与导航/🏷️ 标签体系|🏷️ 标签体系]]",
    "[[10-索引与导航/标签体系|": "[[10-索引与导航/🏷️ 标签体系|",
    "[[知识库首页]]": "[[🏠 知识库首页]]",
    # 数据资产
    "[[../12-项目案例库]]": "[[12-项目案例库/项目案例库-总览|项目案例库]]",
    # trailing slash dir refs
    "[[09-项目资料/阳安二线/]]": "[[09-项目资料/阳安二线/阳安二线-项目总览|阳安二线]]",
    "[[09-项目资料/道班房/]]": "[[09-项目资料/道班房|道班房]]",
    "[[09-项目资料/青河G331/]]": "[[09-项目资料/青河G331|青河G331]]",
    "[[09-项目资料/道班房/06-物资采购/]]": "[[09-项目资料/道班房|道班房]]",
    "[[09-项目资料/青河G331/06-物资采购/]]": "[[09-项目资料/青河G331|青河G331]]",
    # missing files
    "[[05-投标报价/报价策略/综合评估法报价策略]]": "综合评估法报价策略 <!-- 待创建 -->",
    "[[05-投标报价/招标文件/招标文件关键信息提取模板]]": "招标文件关键信息提取模板 <!-- 待创建 -->",
}

base12 = "12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例"
relative_fixes = {
    "[[04_分析报告/04_分析报告-总览]]": f"[[{base12}/04_分析报告/04_分析报告-总览|分析报告总览]]",
    "[[../..-总览]]": f"[[{base12}/2026-劳务价格与鄯善启创案例-总览|案例总览]]",
}

for f in VAULT.rglob("*.md"):
    rel = str(f.relative_to(VAULT)).replace(BS, "/")
    if rel.split("/")[0] in IGN: continue
    c = f.read_text(encoding='utf-8')
    orig = c

    # Apply all known fixes
    for old, new in fixes_applied.items():
        c = c.replace(old, new)
    for old, new in relative_fixes.items():
        c = c.replace(old, new)

    # Fix trailing slash in wikilinks
    c = re.sub(r'\[\[([^\]]+)/\]\]', r'[[\1|...]]', c)
    # Fix bare ../12 references
    c = re.sub(r'\[\[\.\./([^\]]+)\]\]', r'[[\1]]', c)

    if c != orig:
        f.write_text(c, encoding='utf-8')
        cnt += 1

print(f"Final fix: {cnt} files")
