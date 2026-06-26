#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标签规范化 v3 — 09-项目资料子页"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

added = 0
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if not rel.startswith('09-项目资料/'):
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if m:
        tm = re.search(r'tags:\s*\[(.*?)\]', m.group(1), re.DOTALL)
        if tm:
            continue  # 已有 tag

    parts = rel.split('/')
    # 09-项目资料/<项目>/<子目录>/<子目录>-总览.md
    inferred = ['项目', '索引']
    if len(parts) >= 3:
        sub_dir = parts[2]
        dir_map = {
            '01-合同招投标': '合同',
            '02-工程量与计价': '造价',
            '03-图纸资料': '图纸',
            '04-施工方案': '施工',
            '05-变更签证': '造价/变更',
            '06-物资采购': '造价/材料',
            '07-质量安全': '施工/安全',
            '08-结算归档': '造价/结算',
            '09-人员与行政': '管理',
        }
        if sub_dir in dir_map:
            inferred.append(dir_map[sub_dir])
        # 项目总览
        if rel.endswith('-项目总览.md'):
            inferred = ['项目', '总览', '索引']
        # 子目录总览
        if rel.endswith('-总览.md'):
            inferred.append('总览')

    inferred = inferred[:5]

    # 插入
    new_fm = 'tags: [' + ', '.join(inferred) + ']\n' + (m.group(1) if m else '')
    if m:
        fm_end = m.end()
        new_text = text[:m.start()] + '---\n' + new_fm + '\n---' + text[fm_end:]
    else:
        # 无 frontmatter
        new_text = '---\n' + new_fm + '\n---\n\n' + text

    src.write_text(new_text, encoding='utf-8')
    added += 1

print(f'已补充 09-项目资料 tags: {added} 个')

# === 处理剩余的几个其他目录的 ===
remaining = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] == '99-归档库':
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if m:
        tm = re.search(r'tags:\s*\[(.*?)\]', m.group(1), re.DOTALL)
        if tm:
            continue
    remaining.append(rel)

print(f'剩余无标签: {len(remaining)}')
for r in remaining:
    print(f'  {r}')