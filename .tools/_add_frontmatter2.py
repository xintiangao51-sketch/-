import os, sys
from pathlib import Path

# Fix encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

base = Path(r"D:\知识库")

SKIP_FOLDERS = {'.obsidian', '.claude', '.claudian', '.tools', 'node_modules', '__pycache__', '.archive'}
SKIP_PATTERNS = ['_精华摘要', '_index', '🏠', '🏷️', '📚', '🚀', 'SKILL.md', 'instructions.md']

def get_tags(rel):
    parts = rel.parts
    tag_map = {
        '01-造价核心': ('[造价, 索引]', '造价'),
        '02-工程图纸': ('[图纸, 索引]', '图纸'),
        '03-合同与法务': ('[合同, 索引]', '合同'),
        '04-施工方案': ('[施工, 索引]', '施工'),
        '05-投标报价': ('[投标, 索引]', '投标'),
        '06-参考文档': ('[模板, 索引]', '模板'),
        '07-AI工具与技能': ('[AI, 索引]', 'AI'),
        '08-参考规范': ('[规范, 索引]', '规范'),
        '09-项目资料': ('[项目, 索引]', '项目'),
    }
    section = parts[0]
    for key, (tags, _) in tag_map.items():
        if section == key:
            return tags
    return "[未分类]"

# Find files still missing frontmatter
remaining = []
for md_file in base.rglob("*.md"):
    parts = md_file.relative_to(base).parts
    if any(p in SKIP_FOLDERS for p in parts):
        continue
    fname = md_file.stem
    if any(p in fname for p in SKIP_PATTERNS):
        continue
    try:
        if md_file.stat().st_size == 0:
            continue
        with open(md_file, 'r', encoding='utf-8', errors='replace') as f:
            first_line = f.readline().strip()
        if first_line == '---':
            continue
    except:
        continue
    remaining.append(md_file)

count = 0
for md_file in remaining:
    rel = md_file.relative_to(base)
    tags = get_tags(rel)
    try:
        with open(md_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        fm = f"---\ntags: {tags}\ncreated: 2026-06-12\ntype: reference\n---\n\n"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(fm + content)
        count += 1
        print(f"  +frontmatter: {rel}")
    except Exception as e:
        print(f"  ERROR: {rel} - {e}")

print(f"\nRemaining files fixed: {count}")
