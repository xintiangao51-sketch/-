#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链最终修复 v10 — 处理完全不存在的文件"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# 不存在文件 → 转外链或指向总览
fixes = [
    # DDC 文本（不存在 → 指向总览）
    ('[[06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|数字住建规划 2024-02-07]]'),
    ('[[06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|BIM全生命周期通知]]'),
    ('[[06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|智能建造工作现场会 青岛]]'),
    ('[[06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|住建部调研乌鲁木齐]]'),
    # drawing-analyzer（不存在具体文件）
    ('[[07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw]]',
     '[[07-AI工具与技能/drawing-analyzer/drawing-analyzer-总览|Drawing 2026-06-08]]'),
    # 造价工作台搭建方案（不存在）
    ('[[07-AI工具与技能/md文档/造价工作台搭建方案]]',
     '[[07-AI工具与技能/md文档/_精华摘要|造价工作台搭建方案]]'),
    # 乌鲁木齐速查（实际是 .md）
    ('[[11-材料设备价格库/乌鲁木齐2026-04_速查]]',
     '[[11-材料设备价格库/乌鲁木齐2026-04_速查.md]]'),
]

files_touched = set()
total = 0
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    original = text
    for old, new in fixes:
        if old in text:
            text = text.replace(old, new)
            total += 1
    if text != original:
        src.write_text(text, encoding='utf-8')
        files_touched.add(src)

print(f'已修改文件: {len(files_touched)}')
print(f'修复总数: {total}')