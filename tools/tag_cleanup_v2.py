#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标签规范化 v2 — 全活动区精简"""
import io
import sys
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# === 标签规则 ===
# 1. 保留核心 5 个：类别 + 子域 + 关键属性 + 地理
# 2. 保留 `索引` 如果文件是索引页
# 3. 保留 `KC` 如果是 KC 卡片
# 4. 保留 `自动生成` 如果是 _精华摘要
# 5. 删除相似标签（如 '造价' + '造价/定额' 保留 '造价/定额'）

PRIORITY_TAGS = ['索引', 'KC', '自动生成', '精华', '模板', '参考', '规范', '管理规则']

def normalize_tags(tags):
    """规范化标签列表"""
    # 去重
    tags = list(dict.fromkeys(tags))
    # 优先标签（保留）
    priority_kept = [t for t in tags if t in PRIORITY_TAGS]
    # 其他标签
    other = [t for t in tags if t not in PRIORITY_TAGS]

    # 按优先级排序：领域/子域 > 属性 > 状态
    # 取前 5 个
    result = priority_kept + other
    if len(result) > 5:
        result = result[:5]
    return result

# === 1. 处理标签过多 ===
modified = 0
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        continue
    fm = m.group(1)
    tm = re.search(r'tags:\s*\[(.*?)\]', fm, re.DOTALL)
    if not tm:
        continue
    tags = [t.strip().strip('"').strip("'") for t in tm.group(1).split(',') if t.strip()]
    if len(tags) <= 5:
        continue

    new_tags = normalize_tags(tags)
    new_tags_str = ', '.join(new_tags)
    new_fm = re.sub(r'tags:\s*\[.*?\]', f'tags: [{new_tags_str}]', fm, flags=re.DOTALL)
    if new_fm == fm:
        continue
    # 使用 end() 定位（frontmatter 块结束在 --- 之后）
    fm_end = m.end()
    new_text = text[:m.start()] + '---\n' + new_fm + '\n---' + text[fm_end:]
    src.write_text(new_text, encoding='utf-8')
    modified += 1
    if modified <= 5:
        print(f'  {len(tags)}→{len(new_tags)} | {rel}')

print(f'\n标签过多已处理: {modified} 个')

# === 2. 处理无标签 ===
added = 0
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        continue
    fm = m.group(1)
    tm = re.search(r'tags:\s*\[(.*?)\]', fm, re.DOTALL)
    if tm:
        continue

    # 根据路径推断标签
    parts = rel.split('/')
    inferred_tags = []
    # 顶层目录
    top = parts[0] if parts else ''
    dir_tag_map = {
        '00-工作台': '工作台',
        '01-造价核心': '造价',
        '02-业务中台': '业务',
        '03-合同与法务': '合同',
        '04-施工方案': '施工',
        '05-投标报价': '投标',
        '06-参考文档': '参考',
        '07-AI工具与技能': 'AI',
        '08-参考规范': '规范',
        '10-索引与导航': '索引',
        '11-材料设备价格库': '造价/材料',
        '12-项目案例库': '案例',
        '13-工程图纸': '图纸',
        '14-标准模板': '模板',
        '16-运营数据': '运营',
        '17-知识库引擎': '引擎',
    }
    if top in dir_tag_map:
        inferred_tags.append(dir_tag_map[top])

    # 文件名推断
    name = src.stem
    if '总览' in name or '索引' in name or 'README' in name:
        inferred_tags.append('索引')
    if '精华摘要' in name or '_精华' in name:
        inferred_tags.append('自动生成')
    if '模板' in name:
        inferred_tags.append('模板')
    if 'KC' in name and name.startswith('KC'):
        inferred_tags.append('KC')
    if '项目' in name or '工程' in name:
        inferred_tags.append('项目')

    if not inferred_tags:
        inferred_tags = [dir_tag_map.get(top, '笔记')]

    # 限制 5 个
    inferred_tags = inferred_tags[:5]

    # 插入 tags
    new_fm = 'tags: [' + ', '.join(inferred_tags) + ']\n' + fm
    fm_end = m.end()
    new_text = text[:m.start()] + '---\n' + new_fm + '\n---' + text[fm_end:]
    src.write_text(new_text, encoding='utf-8')
    added += 1
    if added <= 5:
        print(f'  +{inferred_tags} | {rel}')

print(f'\n无标签已补充: {added} 个')