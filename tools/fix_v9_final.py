#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链最终修复 v9 — 处理真实反斜杠"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
BS = chr(92)  # 真实反斜杠

# DDC 文本（裸名引用，加后缀）
fixes = []
ddc_files = [
    '06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07',
    '06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文',
    '06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文',
    '06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文',
]
for d in ddc_files:
    for ext in ['.md', '.txt']:
        if (VAULT / f'{d}{ext}').exists():
            fixes.append((f'[[{d}]]', f'[[{d}{ext}]]'))
            fixes.append((f'[[{d}|', f'[[{d}{ext}|'))
            break

# 真实反斜杠的 KC 引用（仅处理 ]] 形式）
bs_targets = [
    '08-参考规范/KC-001_造价管理办法_2026修订',
    '08-参考规范/KC-002_GB50500_2024计价标准',
    '08-参考规范/KC-003_新疆定额体系现状_202606',
    '10-索引与导航/KC-004_知识库改造方案_v1',
    '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设',
]
for t in bs_targets:
    fixes.append((f'[[{t}{BS}]]', f'[[{t}]]'))
    fixes.append((f'[[{t}{BS}|', f'[[{t}|'))

# 项目案例库反斜杠 KC
kc_bs_targets = [
    '12-项目案例库/.../KC-劳务分包价格库-2026市政与企业对下指导价',
    '12-项目案例库/.../KC-劳务扩大报价分析方法论',
    '12-项目案例库/.../KC-劳务清包合同风险条款模板',
    '12-项目案例库/.../KC-建筑设备带人租赁税务定性',
    '12-项目案例库/.../KC-旋挖钻班组最终结算案例-田让存',
    '12-项目案例库/.../KC-鄯善启创劳务扩大报价案例复盘',
]
for t in kc_bs_targets:
    actual_name = t.split('/')[-1]
    new_target = f'12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/{actual_name}'
    fixes.append((f'[[{t}{BS}]]', f'[[{new_target}]]'))
    fixes.append((f'[[{t}{BS}|', f'[[{new_target}|'))

# 标签体系 + 知识库首页（无 emoji 前缀 → 加 emoji）
fixes.append(('[[10-索引与导航/标签体系]]', '[[10-索引与导航/🏷️ 标签体系]]'))
fixes.append(('[[10-索引与导航/标签体系|', '[[10-索引与导航/🏷️ 标签体系|'))
fixes.append(('[[知识库首页]]', '[[🏠 知识库首页]]'))
fixes.append(('[[知识库首页|', '[[🏠 知识库首页|'))

# drawing-analyzer 和 md文档
fixes.append(('[[07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw.md]]',
              '[[07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw]]'))
fixes.append(('[[07-AI工具与技能/md文档/造价工作台搭建方案.md]]',
              '[[07-AI工具与技能/md文档/造价工作台搭建方案]]'))

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

# 列出剩余反斜杠 wikilink 用于调试
remaining_bs = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    import re
    for m in re.finditer(r'\[\[[^\]\n]*' + BS + r'[^\]\n]*\]\]', text):
        remaining_bs.append((src.relative_to(VAULT), m.group(0)))
print(f'\n剩余反斜杠 wikilink: {len(remaining_bs)} 个')
for path, link in remaining_bs[:10]:
    print(f'  {path}: {link[:120]}')