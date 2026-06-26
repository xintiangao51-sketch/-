#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链批量修复 v12 — 处理所有活动区断链"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# 路径映射表
PATH_FIXES = {
    # 缺失的 KB-131 实际指向 KB-132（最接近）
    'KB-131_计价有方-162审计点': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-131_计价有方-清单52术语': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-131': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',

    # 缺失的 KC-131 实际指向 KC-130
    'KC-131': '10-索引与导航/KC-130_变更签证实战指南',

    # KC 互引
    'KC-105': '10-索引与导航/KC-105_新疆地州估价表执行口径',
    'KC-286': '10-索引与导航/KC-286_新疆人材机价格信息查询路径',
    'KC-104': '10-索引与导航/KC-104_新疆2020版主定额体系',
    'KC-107': '10-索引与导航/KC-107_国标GB50500-2024与新疆落地',

    # 缺失的 00-工作台 引用（指向外部路径）
    '体检/内观.md': '体检',
    'D:\\知识库\\10-索引与导航\\AI-Agent五件套\\工作手册\\知识库运行手册': '10-索引与导航/AI-Agent五件套/工作手册/知识库运行手册',
    'D:\\Claude-3p\\CLAUDE.md': 'CLAUDE.md',
    'D:\\知识库\\.scripts\\crawl_info_price.py': 'tools/crawl_xj_info_price.py',
    'D:\\知识库\\lingtai-main\\lingtai-main\\': '10-索引与导航/AI-Agent五件套',
    'CLAUDE.md': '10-索引与导航/AI-Agent五件套',
    'MEMORY.md': '10-索引与导航/AI-Agent五件套',
    '知识库结构.md': '10-索引与导航/AI-Agent五件套/工作手册/知识库结构',
    'D:\\知识库\\10-索引与导航\\AI-Agent五件套\\工作手册\\': '10-索引与导航/AI-Agent五件套/工作手册',
    'D:\\知识库\\.scripts\\': 'tools',
    'D:\\知识库\\.scripts\\lint_xinjiang.py': 'tools',
    'D:\\知识库\\.scripts\\semantic_scan_xj.py': 'tools',

    # 04-施工方案/冬施方案模板 引用
    'GB 50500-2024 新疆落地': '08-参考规范/KC-107_国标GB50500-2024与新疆落地',
    'JGJ/T 104-2011 建筑工程冬期施工规程': '08-参考规范/JGJ-T 104-2011 建筑工程冬期施工规程',
    '04-施工方案/': '04-施工方案/施工方案-总览',
    '08-参考规范/': '08-参考规范/参考规范-总览',

    # 11-材料设备价格库 已修复
    '11-材料设备价格库/乌鲁木齐2026-04_速查.md': '11-材料设备价格库/乌鲁木齐2026-04_速查',

    # KC 引用 → 总索引
    'GB 50500-2024 新疆落地': '08-参考规范/KC-107_国标GB50500-2024与新疆落地',

    # AI-Agent五件套 引用 → 实际文件
    'AI-Agent五件套/工作手册/知识库结构': '10-索引与导航/AI-Agent五件套/工作手册/知识库结构',
    'AI-Agent五件套/工作手册/知识库运行手册': '10-索引与导航/AI-Agent五件套/工作手册/知识库运行手册',
}

# 直接处理：找出所有断链目标并创建 stub 或修复
all_md = set()
all_filenames = set()
for p in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in p.parts):
        continue
    rel = str(p.relative_to(VAULT)).replace(chr(92), '/')
    all_md.add(rel)
    all_filenames.add(rel.split('/')[-1])

# 收集所有断链
WL = re.compile(r'\[\[([^\]\n]+?)\]\]')
unresolved_by_target = {}
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    src_rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if src_rel.split('/')[0] in SOURCE_IGNORE:
        continue
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
    except: continue
    for m in WL.finditer(text):
        target = m.group(1).split('|')[0].split('#')[0].strip()
        if not target: continue
        t = target.replace(chr(92), '/')
        direct = t + '.md' if not t.endswith('.md') else t
        if direct in all_md or t in all_md: continue
        if '/' not in t and ((t+'.md') in all_filenames or t in all_filenames): continue
        for prefix in ['🏠 ', '🏷️ ', '📊 ', '📚 ', '🗂️ ', '🧭 ', '🔗 ', '📁 ', '💰 ', '📋 ', '📐 ', '🔍 ', '🌐 ', '⭐ ', '🎯 ']:
            if t.startswith(prefix):
                stem = t[len(prefix):]
                if stem in all_filenames or (stem+'.md') in all_filenames: continue
        unresolved_by_target.setdefault(target, []).append(src_rel)

# 统计
print(f'真实断链目标数: {len(unresolved_by_target)}')
print()
print('=== 断链目标 Top 30 ===')
for t, srcs in sorted(unresolved_by_target.items(), key=lambda x: -len(x[1]))[:30]:
    in_fixes = t in PATH_FIXES
    print(f'  [{"映射" if in_fixes else "未映射"}] [{len(srcs):2d}] {t}')