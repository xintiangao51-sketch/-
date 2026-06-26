#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""孤岛清理 v2 — 全模块反链注入"""
import io
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# 给孤岛注入反链的策略
# 1. 10-索引与导航/KC-xxx → 知识库总索引
# 2. 06-参考文档/DDC数字驱动建设/cards/card_* → _index_DDC数字驱动建设
# 3. 07-AI工具与技能/* → AI工具与技能-总览
# 4. 12-项目案例库/... → 项目案例库-总览

def add_backlink(file_path, target_link, label="上级总览"):
    """添加反链到文件末尾"""
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

# 策略 1: KC 卡片 → 知识库总索引
for src in VAULT.rglob('10-索引与导航/KC-*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if add_backlink(src, '10-索引与导航/知识库总索引', '知识库总索引'):
        added += 1

# 策略 2: DDC 卡片 → DDC 总览
for src in VAULT.rglob('06-参考文档/DDC数字驱动建设/cards/*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    if add_backlink(src, '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设', 'DDC总览'):
        added += 1

# 策略 3: 07-AI工具子目录 → AI工具与技能-总览
ai_root = VAULT / '07-AI工具与技能'
if ai_root.exists():
    for src in ai_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        # 跳过 _精华摘要（已被索引）
        if rel.endswith('_精华摘要.md'):
            continue
        # 跳过总览本身
        if rel == '07-AI工具与技能/AI工具与技能-总览.md':
            continue
        if add_backlink(src, '07-AI工具与技能/AI工具与技能-总览', 'AI工具总览'):
            added += 1

# 策略 4: 12-项目案例库 → 项目案例库-总览
case_root = VAULT / '12-项目案例库'
if case_root.exists():
    for src in case_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel == '12-项目案例库/项目案例库-总览.md':
            continue
        if add_backlink(src, '12-项目案例库/项目案例库-总览', '案例库总览'):
            added += 1

# 策略 5: 06-参考文档/其他 → 参考文档-总览
ref_root = VAULT / '06-参考文档'
if ref_root.exists():
    for src in ref_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel in ['06-参考文档/参考文档-总览.md', '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设.md']:
            continue
        if 'DDC数字驱动建设/cards/' in rel and rel.endswith('.md'):
            continue  # 已被策略 2 处理
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '06-参考文档/参考文档-总览', '参考文档总览'):
            added += 1

# 策略 6: 01-造价核心 子目录 → 造价核心-总览
cost_root = VAULT / '01-造价核心'
if cost_root.exists():
    for src in cost_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel in ['01-造价核心/造价核心-总览.md',
                   '01-造价核心/造价实战经验库.md',
                   '01-造价核心/投标报价策略库.md',
                   '01-造价核心/材料设备价格趋势.md']:
            continue
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '01-造价核心/造价核心-总览', '造价核心总览'):
            added += 1

# 策略 7: 04-施工方案 → 施工方案-总览
plan_root = VAULT / '04-施工方案'
if plan_root.exists():
    for src in plan_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel.endswith('04-施工方案/施工方案-总览.md'):
            continue
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '04-施工方案/施工方案-总览', '施工方案总览'):
            added += 1

# 策略 8: 03-合同与法务 → 合同与法务-总览
contract_root = VAULT / '03-合同与法务'
if contract_root.exists():
    for src in contract_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel.endswith('合同与法务-总览.md') or rel == '03-合同与法务/README.md':
            continue
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '03-合同与法务/合同与法务-总览', '合同法务总览'):
            added += 1

# 策略 9: 05-投标报价 → 投标报价-总览
bid_root = VAULT / '05-投标报价'
if bid_root.exists():
    for src in bid_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel.endswith('投标报价-总览.md') or rel == '05-投标报价/README.md':
            continue
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '05-投标报价/投标报价-总览', '投标报价总览'):
            added += 1

# 策略 10: 08-参考规范 → 参考规范-总览
spec_root = VAULT / '08-参考规范'
if spec_root.exists():
    for src in spec_root.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
        if rel.endswith('参考规范-总览.md') or rel == '08-参考规范/README.md':
            continue
        if rel.endswith('_精华摘要.md'):
            continue
        if add_backlink(src, '08-参考规范/参考规范-总览', '参考规范总览'):
            added += 1

print(f'已添加反链: {added} 个')