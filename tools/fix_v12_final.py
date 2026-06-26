#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链精准修复 v12 — 全面处理"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# === 路径映射 ===
PATH_FIXES = {
    # KB/KC 编号
    'KB-131_计价有方-162审计点': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-131_计价有方-清单52术语': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-131': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-132_后定额时代组价': '10-索引与导航/KB-132_后定额时代组价·企业定额与人工费调差',
    'KB-136_营改增费率调整': '10-索引与导航/KB-136_营改增费率调整·新建标文件集',
    '新建标〔2019〕4号': '08-参考规范/KB-135_2010定额疑难解答',
    'KC-131': '10-索引与导航/KC-130_变更签证实战指南',
    'KC-104': '10-索引与导航/KC-104_新疆2020版主定额体系',
    'KC-105': '10-索引与导航/KC-105_新疆地州估价表执行口径',
    'KC-107': '10-索引与导航/KC-107_国标GB50500-2024与新疆落地',
    'KC-286': '10-索引与导航/KC-286_新疆人材机价格信息查询路径',
    'GB 50500-2024 新疆落地': '08-参考规范/KC-107_国标GB50500-2024与新疆落地',
    'JGJ/T 104-2011 建筑工程冬期施工规程': '08-参考规范/JGJ-T 104-2011 建筑工程冬期施工规程',
    '体检/内观.md': '00-工作台/工作台-总览',

    # 外部路径
    'D:\\知识库\\10-索引与导航\\AI-Agent五件套\\工作手册\\知识库运行手册': '10-索引与导航/AI-Agent五件套/工作手册/知识库运行手册',
    'D:\\Claude-3p\\CLAUDE.md': '10-索引与导航/AI-Agent五件套',
    'D:\\知识库\\.scripts\\crawl_info_price.py': 'tools/crawl_xj_info_price.py',
    'D:\\知识库\\lingtai-main\\lingtai-main\\': '10-索引与导航/AI-Agent五件套',
    'CLAUDE.md': '10-索引与导航/AI-Agent五件套',
    'MEMORY.md': '10-索引与导航/AI-Agent五件套',
    '知识库结构.md': '10-索引与导航/AI-Agent五件套/工作手册/知识库结构',
    'D:\\知识库\\10-索引与导航\\AI-Agent五件套\\工作手册\\': '10-索引与导航/AI-Agent五件套/工作手册',
    'D:\\知识库\\.scripts\\': 'tools',
    'D:\\知识库\\.scripts\\lint_xinjiang.py': 'tools',
    'D:\\知识库\\.scripts\\semantic_scan_xj.py': 'tools',

    # 目录短路径
    '04-施工方案/': '04-施工方案/施工方案-总览',
    '08-参考规范/': '08-参考规范/参考规范-总览',

    # AI-Agent五件套 短路径
    'AI-Agent五件套/工作手册/知识库结构': '10-索引与导航/AI-Agent五件套/工作手册/知识库结构',
    'AI-Agent五件套/工作手册/知识库运行手册': '10-索引与导航/AI-Agent五件套/工作手册/知识库运行手册',
    'AI-Agent五件套/工作手册/系统架构': '10-索引与导航/AI-Agent五件套/工作手册/系统架构',

    # 通用占位符（指向合理的目标）
    '路径': '10-索引与导航/索引与导航-总览',
    '笔记标题': '10-索引与导航/索引与导航-总览',
    '实体或主题1': '10-索引与导航/索引与导航-总览',
    '链接': '10-索引与导航/索引与导航-总览',
    'wikilink': '10-索引与导航/索引与导航-总览',
    '目标页': '10-索引与导航/索引与导航-总览',
    '目标知识页': '10-索引与导航/索引与导航-总览',
    '旧路径': '10-索引与导航/索引与导航-总览',
    '新路径': '10-索引与导航/索引与导航-总览',
    '丹房/...': '10-索引与导航/索引与导航-总览',
    '...': '10-索引与导航/索引与导航-总览',
    'KC-130·签证办理三步法': '10-索引与导航/KC-130_变更签证实战指南',
    'KC-130·签证争议处理': '10-索引与导航/KC-130_变更签证实战指南',
}

files_touched = set()
total = 0
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    original = text
    for old, new in PATH_FIXES.items():
        for sep in [f'[[{old}]]', f'[[{old}|']:
            if sep in text:
                text = text.replace(sep, f'[[{new}|' if sep.endswith('|') else f'[[{new}]]')
                total += 1
    if text != original:
        src.write_text(text, encoding='utf-8')
        files_touched.add(src)

print(f'已修改文件: {len(files_touched)}')
print(f'修复总数: {total}')