#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全库诊断 v1 — 标签/命名/链接/孤岛/重复"""
import io
import sys
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# === 1. 标签分析 ===
all_tags = Counter()
tag_issues = []
no_tags = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    text = src.read_text(encoding='utf-8', errors='ignore')

    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        no_tags.append(rel)
        continue
    fm = m.group(1)

    tm = re.search(r'tags:\s*\[(.*?)\]', fm, re.DOTALL)
    if not tm:
        no_tags.append(rel)
        continue

    tags = [t.strip().strip('"').strip("'") for t in tm.group(1).split(',') if t.strip()]
    for t in tags:
        all_tags[t] += 1

    if len(tags) > 5:
        tag_issues.append({'file': rel, 'tags': tags, 'count': len(tags)})
    if len(tags) == 0:
        tag_issues.append({'file': rel, 'tags': [], 'count': 0})

print('=== 标签统计 ===')
print(f'  唯一标签数: {len(all_tags)}')
print(f'  标签总数: {sum(all_tags.values())}')
print(f'  无标签笔记: {len(no_tags)}')
print(f'  标签过多笔记: {len(tag_issues)}')
print()
print('=== Top 20 标签 ===')
for tag, count in all_tags.most_common(20):
    print(f'  {count:4d} | {tag}')
print()

# === 2. 命名规范分析 ===
print('=== 命名规范 ===')
naming_issues = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    name = src.name
    # 检测问题命名
    issues = []
    # 含空格
    if ' ' in name and '价格' not in name:  # 例外：信息价等
        issues.append('含空格')
    # 含特殊字符（除中文/英文/数字/下划线/连字符/点/中文括号）
    if re.search(r'[<>:"/\\|?*]', name):
        issues.append('含非法字符')
    # 总览命名规范
    if '总览' in name and not name.endswith('-总览.md'):
        issues.append('总览命名不规范')
    if issues:
        naming_issues.append({'file': rel, 'name': name, 'issues': issues})

print(f'  命名问题文件: {len(naming_issues)}')
for n in naming_issues[:10]:
    print(f'    {n["file"]}: {n["issues"]}')
print()

# === 3. 空文件和极小文件 ===
print('=== 空文件/极小文件 ===')
empty_files = []
small_files = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    size = src.stat().st_size
    if size == 0:
        empty_files.append(rel)
    elif size < 200:  # 小于 200 字节
        try:
            text = src.read_text(encoding='utf-8', errors='ignore')
            content_lines = len([l for l in text.splitlines() if l.strip()])
            if content_lines < 3:
                small_files.append({'file': rel, 'size': size, 'lines': content_lines})
        except:
            pass

print(f'  空文件: {len(empty_files)}')
for f in empty_files[:10]:
    print(f'    {f}')
print(f'  极小文件: {len(small_files)}')
for f in small_files[:10]:
    print(f'    {f}')
print()

# === 4. 重复文件检测 ===
print('=== 重复文件检测 ===')
content_hashes = defaultdict(list)
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
        # 只用正文（去掉 frontmatter）
        body = re.sub(r'^---\n.*?\n---', '', text, count=1, flags=re.DOTALL).strip()
        h = hash(body[:1000])
        content_hashes[h].append(rel)
    except:
        pass

duplicates = {h: paths for h, paths in content_hashes.items() if len(paths) > 1}
print(f'  重复内容组: {len(duplicates)}')
for h, paths in list(duplicates.items())[:10]:
    print(f'    哈希 {str(h)[:8]}: {len(paths)} 个文件')
    for p in paths:
        print(f'      - {p}')
print()

# === 5. 标题与文件名一致性 ===
print('=== 标题与文件名一致性 ===')
title_issues = []
for src in VAULT.rglob('*.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    if rel.split('/')[0] in SOURCE_IGNORE:
        continue
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
        # 第一个 # 标题
        m = re.search(r'^#\s+(.+?)$', text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
            # 检查标题是否包含文件名关键词
            stem = src.stem
            # 简化检测：标题含文件名核心词
            stem_clean = re.sub(r'[-_]', '', stem)[:10]
            title_clean = re.sub(r'[-_《》（）()]', '', title)[:10]
            if stem_clean and title_clean and stem_clean[:5] not in title_clean and title_clean[:5] not in stem_clean:
                # 只标记明显不匹配
                if len(stem_clean) >= 4 and len(title_clean) >= 4:
                    pass  # 暂不强制一致
    except:
        pass

# === 6. _精华摘要.md 评估 ===
print('=== _精华摘要.md 评估 ===')
summary_count = 0
summary_dups = 0
seen_summary = {}
for src in VAULT.rglob('_精华摘要.md'):
    if any(part.startswith('.') for part in src.parts):
        continue
    rel = str(src.relative_to(VAULT)).replace(chr(92), '/')
    summary_count += 1
    try:
        text = src.read_text(encoding='utf-8', errors='ignore')
        h = hash(text[:500])
        if h in seen_summary:
            summary_dups += 1
        seen_summary[h] = rel
    except:
        pass
print(f'  总数: {summary_count}')
print(f'  重复内容: {summary_dups}')
print()

# === 7. 归档库统计 ===
print('=== 99-归档库 统计 ===')
archive_files = 0
archive_size = 0
for src in (VAULT / '99-归档库').rglob('*'):
    if src.is_file():
        archive_files += 1
        archive_size += src.stat().st_size
print(f'  文件数: {archive_files}')
print(f'  总大小: {archive_size / 1024 / 1024:.2f} MB')

# 按子目录统计
archive_dirs = Counter()
for src in (VAULT / '99-归档库').rglob('*.md'):
    parts = src.relative_to(VAULT / '99-归档库').parts
    if parts:
        archive_dirs[parts[0]] += 1
print(f'  子目录数: {len(archive_dirs)}')
print(f'  主要子目录:')
for d, c in archive_dirs.most_common(15):
    print(f'    {c:4d} | {d}')

# === 8. 根目录异常文件 ===
print()
print('=== 根目录异常文件 ===')
root_issues = []
for src in VAULT.iterdir():
    if not src.is_file():
        continue
    if src.suffix == '.md':
        # 检查是否应该是目录下的
        root_issues.append(f'  根目录 .md: {src.name} ({src.stat().st_size} bytes)')

for r in root_issues:
    print(r)

# 保存诊断结果
result = {
    'total_files': sum(1 for _ in VAULT.rglob('*.md') if not any(p.startswith('.') for p in _.parts)),
    'unique_tags': len(all_tags),
    'tag_issues': len(tag_issues),
    'no_tags': no_tags[:30],
    'naming_issues_count': len(naming_issues),
    'empty_files': empty_files,
    'small_files': small_files[:20],
    'duplicates_count': len(duplicates),
    'summary_count': summary_count,
    'summary_dups': summary_dups,
    'archive_files': archive_files,
    'archive_size_mb': archive_size / 1024 / 1024,
}

(VAULT / 'tools' / 'diagnose_result.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)
print('\n诊断结果已保存到 tools/diagnose_result.json')