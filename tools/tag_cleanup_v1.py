#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标签精简 v1 — 每个文件精简到 5 个标签"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# 标签精简映射表
TAG_FIXES = {
    '08-参考规范/KC-005_GB50856-2013_通用安装工程量计算规范.md':
        ['国标/工程量计算', '国标', '通用安装', '扫描件', '参考规范'],

    '08-参考规范/KC-008_GBT50856-2024_通用安装工程量计算标准.md':
        ['国标/工程量计算', '国标', '2024新标', '扫描件', '参考规范'],

    '10-索引与导航/KC-107_国标GB50500-2024与新疆落地.md':
        ['造价/清单', '国标', 'GB50500', '新疆落地', '公开依据'],

    '10-索引与导航/KC-108_智能建造建筑机器人消耗量定额.md':
        ['造价/定额', '智能建造', '新疆', '公开依据', '基础定额'],

    '10-索引与导航/KC-227_新疆费率与取费查询路径.md':
        ['造价/取费', '新疆', '费率取费', '公开依据', 'KC'],

    '10-索引与导航/KC-286_新疆人材机价格信息查询路径.md':
        ['造价/材料', '新疆', '信息价', '人工单价', '公开依据'],

    '10-索引与导航/KC-480_新疆造价公开依据清单总索引.md':
        ['造价', '总索引', '新疆', '公开依据', 'KC'],

    '10-索引与导航/KC-D01_数字驱动建设主题资源.md':
        ['数字驱动', 'BIM', '智能建造', '数字住建', 'KC'],

    '10-索引与导航/KC-T01_造价管理办法正式版追踪.md':
        ['造价/法规', '251号令', '新疆', '追踪', 'KC'],

    '01-造价核心/定额与计价/2026-新疆配套调整/公路工程定额/_文件清单.md':
        ['造价', '公路定额', '新疆', '文件清单', '定额'],
}

files_modified = 0
total_changes = 0

for rel_path, new_tags in TAG_FIXES.items():
    p = VAULT / rel_path
    if not p.exists():
        print(f'❌ 不存在: {rel_path}')
        continue

    text = p.read_text(encoding='utf-8', errors='ignore')

    # 找到 tags 行
    m = re.match(r'^(---\n)(.*?)(\n---)', text, re.DOTALL)
    if not m:
        print(f'⚠️ 无 frontmatter: {rel_path}')
        continue

    fm = m.group(2)
    # 替换 tags
    new_tags_str = ', '.join(new_tags)
    new_fm = re.sub(r'tags:\s*\[.*?\]', f'tags: [{new_tags_str}]', fm, flags=re.DOTALL)

    # 如果没找到 inline tags 格式，尝试 yaml list 格式
    if new_fm == fm:
        # 尝试 yaml 列表格式
        # tags:\n  - tag1\n  - tag2
        new_yaml_tags = '\n'.join(f'  - {t}' for t in new_tags)
        new_fm = re.sub(r'tags:\s*\n((?:\s*-\s*.+\n?)+)', f'tags:\n{new_yaml_tags}\n', fm)
        if new_fm == fm:
            print(f'⚠️ 未匹配 tags: {rel_path}')
            continue

    new_text = text[:m.start(2)] + new_fm + text[m.end(2):]
    p.write_text(new_text, encoding='utf-8')
    files_modified += 1
    total_changes += len(new_tags)
    print(f'✅ {rel_path}')
    print(f'   新标签: {new_tags}')

print(f'\n已修改: {files_modified} 个文件')
print(f'标签总数: {total_changes}')