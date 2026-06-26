#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""孤岛清理 v3 — 精准处理剩余孤岛"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

def add_backlink(file_path, target_link, label="上级总览"):
    try:
        text = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        return False
    if f'[[{target_link}]]' in text or f'[[{target_link}|' in text:
        return False
    backlink = f'\n\n---\n\n🔗 **{label}**：[[{target_link}]]\n'
    text = text.rstrip() + backlink
    file_path.write_text(text, encoding='utf-8')
    return True

added = 0

# 1. 16-运营数据 → 16-运营数据总览
ops_root = VAULT / '16-运营数据'
if ops_root.exists():
    for src in ops_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        if src.name == '16-运营数据-总览.md':
            continue
        if add_backlink(src, '16-运营数据/16-运营数据-总览', '运营数据总览'):
            added += 1

# 2. 13-工程图纸 → 工程图纸-总览
for src in (VAULT / '13-工程图纸').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if src.name == '工程图纸-总览.md' or src.name == 'README.md':
        continue
    if add_backlink(src, '13-工程图纸/工程图纸-总览', '工程图纸总览'):
        added += 1

# 3. 14-标准模板 → 标准模板-总览
for src in (VAULT / '14-标准模板').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if src.name == '标准模板-总览.md':
        continue
    if add_backlink(src, '14-标准模板/标准模板-总览', '标准模板总览'):
        added += 1

# 4. 11-材料设备价格库 → 材料设备价格库-总览
for src in (VAULT / '11-材料设备价格库').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if src.name == '材料设备价格库-总览.md':
        continue
    if add_backlink(src, '11-材料设备价格库/材料设备价格库-总览', '材料价格库总览'):
        added += 1

# 5. 02-业务中台 → 业务中台-总览
for src in (VAULT / '02-业务中台').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if src.name == '业务中台-总览.md':
        continue
    if add_backlink(src, '02-业务中台/业务中台-总览', '业务中台总览'):
        added += 1

# 6. 17-知识库引擎 → 知识库引擎-总览 或 README
for src in (VAULT / '17-知识库引擎').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if src.name == 'README.md':
        continue
    if add_backlink(src, '17-知识库引擎/README', '知识库引擎'):
        added += 1

# 7. 09-项目资料 项目主页 → 项目资料-总览
for src in (VAULT / '09-项目资料').rglob('*-项目总览.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if add_backlink(src, '09-项目资料/项目资料-总览', '项目资料总览'):
        added += 1

# 8. KC-480.md（根目录）→ 知识库总索引
kc480 = VAULT / 'KC-480.md'
if kc480.exists():
    if add_backlink(kc480, '10-索引与导航/知识库总索引', '知识库总索引'):
        added += 1

# 9. 2026年项目跟踪清单 → 项目资料-总览
tracker = VAULT / '00-工作台' / '2026年项目跟踪清单.md'
if tracker.exists():
    if add_backlink(tracker, '09-项目资料/项目资料-总览', '项目资料'):
        added += 1

# 10. soul.md → 知识库首页
soul = VAULT / 'soul.md'
if soul.exists():
    if add_backlink(soul, '🏠 知识库首页', '知识库首页'):
        added += 1

# 11. 知识库索引.md → 知识库首页
kidx = VAULT / '知识库索引.md'
if kidx.exists():
    if add_backlink(kidx, '🏠 知识库首页', '知识库首页'):
        added += 1

# 12. 知识库规范.md → 知识库首页
kstd = VAULT / '知识库规范.md'
if kstd.exists():
    if add_backlink(kstd, '🏠 知识库首页', '知识库首页'):
        added += 1

# 13. tools/README.md → 自动化脚本工具箱
tools_readme = VAULT / 'tools' / 'README.md'
if tools_readme.exists():
    if add_backlink(tools_readme, 'tools/自动化脚本工具箱', '自动化工具箱'):
        added += 1

# 14. 98-原子知识库 → 知识库首页
for src in (VAULT / '98-原子知识库').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if add_backlink(src, '🏠 知识库首页', '知识库首页'):
        added += 1

# 15. outputs/ → 知识库首页（outputs 是爬取输出）
for src in (VAULT / 'outputs').rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if add_backlink(src, '🏠 知识库首页', '知识库首页'):
        added += 1

print(f'已添加反链: {added} 个')