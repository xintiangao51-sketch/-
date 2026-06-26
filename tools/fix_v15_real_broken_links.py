#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断链修复 v15 — 真实断链专项修复"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

PATH_FIXES = {
    # 顶管工程目录链接
    '09-项目资料/顶管，顶进涵工程/08-结算归档/2': '09-项目资料/顶管，顶进涵工程',
    '09-项目资料/顶管，顶进涵工程/08-结算归档/3': '09-项目资料/顶管，顶进涵工程',
    '09-项目资料/顶管，顶进涵工程/08-结算归档/4': '09-项目资料/顶管，顶进涵工程',
    
    # 建筑业增值税抵扣全攻略附件 - 指向总览页
    '建筑业供应商资质审核表': '03-合同与法务/建筑法规/建筑业增值税抵扣全攻略',
    '增值税申报表自动校验公式': '03-合同与法务/建筑法规/建筑业增值税抵扣全攻略',
    '留抵退税申请材料清单': '03-合同与法务/建筑法规/建筑业增值税抵扣全攻略',
    '建筑业税务稽查红线清单': '03-合同与法务/建筑法规/建筑业增值税抵扣全攻略',
    
    # tools配置链接
    '链接': 'tools/自动化脚本工具箱',
    
    # .scripts目录 - 已归档
    'D:\\知识库\\.scripts\\N4_README_原始资料目录': '99-归档库/README',
    
    # KB-137水利定额链接
    'KB-137_水利工程施工机械台时费定额': '10-索引与导航/KB-139_水利工程定额体系_2024',
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

print(f'\n已修改文件: {len(files_touched)}')
print(f'修复总数: {total}')

for f in sorted(files_touched):
    print(f'  - {f.relative_to(VAULT)}')
