import os
from pathlib import Path
import re

base = Path(r"D:\知识库")

# Files to skip (binary, templates, config, or already fine)
SKIP_FOLDERS = {'.obsidian', '.claude', '.claudian', '.tools', 'node_modules', '__pycache__', '.archive'}
SKIP_PATTERNS = ['_精华摘要', '_index', '🏠', '🏷️', '📚', '🚀', 'SKILL', 'instructions.md']

def get_tags_from_path(rel_path):
    parts = Path(rel_path).parts
    if len(parts) == 0:
        return ("[未分类]", "未分类")
    
    section = parts[0]
    # Map section folders to level-1 tags
    tag_map = {
        '01-造价核心': ('[造价', '造价'),
        '02-工程图纸': ('[图纸', '图纸'),
        '03-合同与法务': ('[合同', '合同'),
        '04-施工方案': ('[施工', '施工'),
        '05-投标报价': ('[投标', '投标'),
        '06-参考文档': ('[模板', '模板'),
        '07-AI工具与技能': ('[AI', 'AI'),
        '08-参考规范': ('[规范', '规范'),
        '09-项目资料': ('[项目', '项目'),
    }
    
    for key, (tag_start, level1) in tag_map.items():
        if section == key:
            # Try to find a more specific tag from subfolder
            if len(parts) >= 3:
                sub = parts[1]
                # Map subfolder names to level-2 tags
                sub_map = {
                    '定额与计价': '/定额',
                    '工程量计算': '/工程量',
                    '材料价格': '/材料',
                    '取费与税金': '/取费',
                    '变更索赔': '/变更',
                    '钢筋图集': '/图集',
                    'FIDIC条款': '/FIDIC',
                    '建设合同模板': '/模板',
                    '建筑法规': '/法规',
                    '安全管理': '/安全',
                    '施工组织设计': '/施组',
                    '质量管理体系': '/质量',
                    '房建方案库': '/方案',
                    '提示词库': '/提示词',
                    'Skills技能': '/技能',
                    'MCP插件': '/MCP',
                    'md文档': '/文档',
                    '施工法务': '/法务',
                    '集团体系文件': '/体系',
                    '集团管理制度': '/制度',
                    '项目管理办法': '/管理',
                    '高新施工技术': '/技术',
                    '管理制度': '/制度',
                    'Hermes配置': '/配置',
                    'drawing-analyzer': '/工具',
                    'JSON文件': '/配置',
                    'pdf': '/工具',
                    '投标文件': '/编制',
                    '招标文件': '/招标',
                    '项目报价': '/报价',
                    '中铁二十五局投标资料': '/投标',
                }
                if sub in sub_map:
                    return (f"{tag_start}{sub_map[sub]}, 索引]", level1)
            return (f"{tag_start}, 索引]", level1)
    
    return ("[未分类, 索引]", "未分类")

# Collect all .md files without frontmatter
files_to_fix = []
for md_file in base.rglob("*.md"):
    rel = md_file.relative_to(base)
    parts = rel.parts
    
    # Skip certain folders
    if any(p in SKIP_FOLDERS for p in parts):
        continue
    
    # Skip files matching skip patterns
    fname = md_file.stem
    if any(p in fname for p in SKIP_PATTERNS):
        continue
    
    # Check if has frontmatter
    try:
        first_line = md_file.read_text(encoding='utf-8').strip().split('\n')[0] if md_file.stat().st_size > 0 else ''
    except:
        continue
    if first_line == '---':
        continue  # Already has frontmatter
    
    files_to_fix.append(md_file)

# Add frontmatter
count = 0
for md_file in files_to_fix:
    rel = str(md_file.relative_to(base))
    tags, _ = get_tags_from_path(rel)
    
    # Read content
    content = md_file.read_text(encoding='utf-8')
    
    # Build frontmatter
    fm = f"---\ntags: {tags}\ncreated: 2026-06-12\ntype: reference\n---\n\n"
    
    # Write back
    md_file.write_text(fm + content, encoding='utf-8')
    count += 1
    # Print relative path
    print(f"  +frontmatter: {rel}")

print(f"\nPhase 4 done: {count} files updated with frontmatter.")
