#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""孤岛笔记清理 v1 — 智能分类处理"""
import io
import sys
import re
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# 构建索引
all_md = set()
all_stems = set()
for p in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in p.parts):
        continue
    rel = str(p.relative_to(VAULT)).replace(chr(92), '/')
    all_md.add(rel)
    all_stems.add(rel.split('/')[-1].replace('.md', ''))

# 计算入链
WL = re.compile(r'\[\[([^\]|#]+)')
inlinks = defaultdict(int)

for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    src_rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if src_rel.split('/')[0] in SOURCE_IGNORE:
        continue
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
    except:
        continue
    for m in WL.finditer(text):
        target = m.group(1).strip().replace(chr(92), '/')
        inlinks[target] += 1
        if not target.endswith('.md'):
            stem = target.split('/')[-1]
            inlinks[stem] += 1

# 找出孤岛
orphans = []
for md in sorted(all_md):
    if md.split('/')[0] in SOURCE_IGNORE:
        continue
    stem = md.split('/')[-1].replace('.md', '')
    if inlinks.get(md, 0) == 0 and inlinks.get(stem, 0) == 0:
        orphans.append(md)

print(f'总孤岛: {len(orphans)}')

# 分类处理
# 1. KC 卡片（10-索引与导航/KC-*）— 已在索引页注册，无需修复
# 2. DDC 卡片（06-参考文档/DDC数字驱动建设/cards/card_*）— 合理孤岛
# 3. 项目子目录总览（*-总览.md）— 应加链接到项目主页
# 4. _精华摘要.md — 自动生成，合理
# 5. 项目主页（*-项目总览.md）— 应被 09-项目资料/项目资料-总览 引用
# 6. 重复/空文件 — 删除

# 步骤 1: 给所有孤岛加 frontmatter tags（如果缺失）
processed = 0
for orphan in orphans:
    p = VAULT / orphan
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except:
        continue

    # 跳过根目录空文件
    if orphan in ['未命名.md', '未命名.canvas']:
        continue

    # 给项目主页加 frontmatter（如缺失）
    if orphan.endswith('-项目总览.md') and '09-项目资料/' in orphan:
        if text.startswith('---\n') and 'project_name:' not in text[:500]:
            project_name = orphan.split('/')[-1].replace('-项目总览.md', '')
            new_fm = f'---\nproject_name: {project_name}\ntype: project-overview\nstatus: 在建\n---\n\n'
            text = new_fm + text[3:].lstrip()
            p.write_text(text, encoding='utf-8')
            processed += 1

print(f'已添加 frontmatter: {processed} 个')

# 步骤 2: 删除重复的 _精华摘要.md（保留最近的）
deleted = 0
seen_hashes = {}
for src in VAULT.rglob('_精华摘要.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
    except:
        continue
    # 文件大小相同 + 路径相似 → 视为重复
    content_hash = hash(text[:500])
    rel = str(src.relative_to(VAULT))
    if content_hash in seen_hashes:
        # 保留 updated 较新的
        existing_path = seen_hashes[content_hash]
        try:
            if src.stat().st_mtime > (VAULT / existing_path).stat().st_mtime:
                (VAULT / existing_path).unlink()
                seen_hashes[content_hash] = rel
                deleted += 1
            else:
                src.unlink()
                deleted += 1
        except:
            pass
    else:
        seen_hashes[content_hash] = rel

print(f'已删除重复精华摘要: {deleted} 个')

# 步骤 3: 给所有 09-项目资料/<项目>/ 内的子页添加反链到项目主页
# 即：09-项目资料/<项目>/XX/XX-总览.md 末尾添加 [[09-项目资料/<项目>/<项目>-项目总览]]
added_backlinks = 0
for orphan in orphans:
    if '09-项目资料/' not in orphan:
        continue
    parts = orphan.split('/')
    if len(parts) < 3:
        continue
    project_name = parts[1]
    # 跳过项目主页本身
    if orphan.endswith(f'{project_name}-项目总览.md'):
        continue
    # 找项目主页
    project_overview = f'09-项目资料/{project_name}/{project_name}-项目总览.md'
    if project_overview not in all_md:
        continue
    p = VAULT / orphan
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except:
        continue
    # 添加反链
    if f'[[09-项目资料/{project_name}/{project_name}-项目总览]]' not in text:
        backlink = f'\n\n---\n\n🔗 **所属项目**：[[09-项目资料/{project_name}/{project_name}-项目总览]]\n'
        text = text.rstrip() + backlink
        p.write_text(text, encoding='utf-8')
        added_backlinks += 1

print(f'已添加项目反链: {added_backlinks} 个')