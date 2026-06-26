#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链修复 v14 — DDC辐页+KB编号+模板示例专项修复"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# 路径映射修复
PATH_FIXES = {
    # DDC辐页链接修复
    'DDC知识卡片辐页·III数据框架': '06-参考文档/DDC数字驱动建设/cards/DDC知识卡片辐页/III数据框架',
    'DDC知识卡片辐页·V造价与工期': '06-参考文档/DDC数字驱动建设/cards/DDC知识卡片辐页/V造价与工期',
    'DDC知识卡片辐页·VIBIM生态': '06-参考文档/DDC数字驱动建设/cards/DDC知识卡片辐页/VIBIM生态',
    'DDC知识卡片辐页·VII智能建造': '06-参考文档/DDC数字驱动建设/cards/DDC知识卡片辐页/VII智能建造',
    'DDC知识卡片辐页·VIII产业互联': '06-参考文档/DDC数字驱动建设/cards/DDC知识卡片辐页/VIII产业互联',
    
    # KB编号修复
    'KB-136': '10-索引与导航/KB-136_营改增费率调整·新建标文件集',
    'KC-286': '10-索引与导航/KB-137_建设工程施工机械台班费用编制规则',
    'KB-370_造价实战经验库': '01-造价核心/造价实战经验库',
    'KC-370': '01-造价核心/造价实战经验库',
    'KB-134': '10-索引与导航/KB-134_2020版计价依据问题解释',
    'KB-133': '10-索引与导航/KB-133_土建审计·黑与白',
    'KB-136_营改增费率调整': '10-索引与导航/KB-136_营改增费率调整·新建标文件集',
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
                replacement = f'[[{new}|' if sep.endswith('|') else f'[[{new}]]'
                text = text.replace(sep, replacement)
                total += 1
                print(f'修复: {old} -> {new}')
    
    if text != original:
        src.write_text(text, encoding='utf-8')
        files_touched.add(src)

print(f'\\n已修改文件: {len(files_touched)}')
print(f'修复总数: {total}')

# 列出被修改的文件
for f in sorted(files_touched):
    print(f'  - {f.relative_to(VAULT)}')
