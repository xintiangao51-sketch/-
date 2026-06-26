#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链终极修复 v11 — 处理最后 9 个"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# 最后 9 个的真实情况：
# 1. 乌鲁木齐2026-04_速查.md → 实际是 .md 文件但脚本检测不到（已修复过）
# 2. 标签体系 → 加 emoji 前缀
# 3. 知识库首页 → 加 emoji 前缀
# 4-7. DDC 文本不存在 → 指向总览
# 8. Drawing 文件不存在 → 指向总览
# 9. 造价工作台搭建方案 → 指向 _精华摘要 或 _index

fixes = [
    # 标签体系 + 知识库首页（用 Obsidian 别名机制）
    ('[[10-索引与导航/标签体系]]', '[[10-索引与导航/🏷️ 标签体系]]'),
    ('[[10-索引与导航/标签体系|', '[[10-索引与导航/🏷️ 标签体系|'),
    ('[[知识库首页]]', '[[🏠 知识库首页]]'),
    ('[[知识库首页|', '[[🏠 知识库首页|'),
    # 乌鲁木齐速查
    ('[[11-材料设备价格库/乌鲁木齐2026-04_速查.md]]',
     '[[11-材料设备价格库/乌鲁木齐2026-04_速查.md|乌鲁木齐速查]]'),
    # DDC 文本（不存在）
    ('[[06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|数字住建规划 2024]]'),
    ('[[06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|BIM通知]]'),
    ('[[06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|智能建造青岛会议]]'),
    ('[[06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文]]',
     '[[06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设|住建部乌鲁木齐调研]]'),
    # drawing-analyzer 文件（不存在具体文件，指向总览）
    ('[[07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw.md]]',
     '[[07-AI工具与技能/drawing-analyzer/drawing-analyzer-总览|Drawing 2026-06-08]]'),
    # md文档造价工作台搭建方案（不存在）
    ('[[07-AI工具与技能/md文档/造价工作台搭建方案.md]]',
     '[[07-AI工具与技能/md文档/_精华摘要|造价工作台搭建方案]]'),
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