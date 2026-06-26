#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链修复 v13 — 处理剩余断链"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

PATH_FIXES = {
    # KC-107 等在 10-索引与导航 而非 08-参考规范
    '08-参考规范/KC-107_国标GB50500-2024与新疆落地': '10-索引与导航/KC-107_国标GB50500-2024与新疆落地',
    '08-参考规范/KB-135_2010定额疑难解答': '10-索引与导航/KB-135_2010定额疑难解答',

    # 16-运营数据 子目录 → 16-运营数据-总览
    '16-运营数据/利润分析': '16-运营数据/16-运营数据-总览',
    '16-运营数据/市场采集': '16-运营数据/16-运营数据-总览',
    '16-运营数据/收支明细': '16-运营数据/16-运营数据-总览',
    '16-运营数据/数据看板': '16-运营数据/16-运营数据-总览',
    '16-运营数据/经验复盘': '16-运营数据/16-运营数据-总览',
    '16-运营数据/营销素材': '16-运营数据/16-运营数据-总览',
    '16-运营数据/项目台账': '16-运营数据/16-运营数据-总览',

    # 通用占位
    '笔记标题': '10-索引与导航/索引与导航-总览',
    '工具': 'tools',
    'tools': 'tools/自动化脚本工具箱',
    'tools/crawl_xj_info_price.py': 'tools/crawl_xj_info_price.py',
    '10-索引与导航/AI-Agent五件套/AI-Agent五件套-总览': '10-索引与导航/索引与导航-总览',
    '10-索引与导航/AI-Agent五件套/工作手册': '10-索引与导航/AI-Agent五件套/工作手册/知识库运行手册',
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