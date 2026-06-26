#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目复盘沉淀自动化 v1.0
功能：扫描项目资料中的实战经验/变更索赔/策略分析，自动生成KC卡片
      沉淀到 12-项目案例库/ 和 01-造价核心/造价实战经验库.md
用法：python auto_project_review.py [--dry]
"""
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path("D:/知识库")
PROJECTS_DIR = VAULT / "09-项目资料"
EXPERIENCE_DB = VAULT / "01-造价核心/造价实战经验库.md"
CASE_DB_DIR = VAULT / "12-项目案例库"


def extract_experience(md_path):
    """从项目笔记中提取经验教训"""
    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception:
        return None

    rel = str(md_path.relative_to(VAULT))

    # 提取项目名
    project = None
    m = re.search(r'project:\s*(.+)', text)
    if m:
        project = m.group(1).strip()
    if not project:
        parts = rel.split('/')
        if len(parts) >= 2:
            project = parts[1]

    # 提取经验关键词
    insights = []
    patterns = [
        (r'风险[:：]\s*(.+)', 'risk'),
        (r'建议[:：]\s*(.+)', 'suggestion'),
        (r'结论[:：]\s*(.+)', 'conclusion'),
        (r'教训[:：]\s*(.+)', 'lesson'),
        (r'经验[:：]\s*(.+)', 'experience'),
        (r'处理方式[:：]\s*(.+)', 'solution'),
    ]
    for pat, tag in patterns:
        for m in re.finditer(pat, text):
            val = m.group(1).strip()
            if len(val) > 10 and len(val) < 300:
                insights.append({"tag": tag, "content": val, "project": project})

    return {"project": project, "insights": insights, "file": rel} if insights else None


def generate_case_card(entry):
    """生成案例KC卡片"""
    today = datetime.now().strftime("%Y-%m-%d")
    project = entry["project"]
    file = entry["file"]
    insights = entry["insights"]

    tags = ["案例复盘", "KC", "自动生成"]

    parts = []
    parts.append("---")
    parts.append(f"tags: {tags}")
    parts.append(f"created: {today}")
    parts.append(f"source: {file}")
    parts.append("type: case-study")
    parts.append("status: 草稿")
    parts.append("---")
    parts.append("")
    parts.append(f"# 案例复盘: {project}")
    parts.append("")
    parts.append(f"> [AUTO] 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    parts.append(f"> 来源: [[{file.replace('.md', '')}]]")
    parts.append("")

    parts.append("## 关键发现")
    for i, item in enumerate(insights[:5], 1):
        parts.append(f"{i}. **{item['tag']}**: {item['content']}")
    parts.append("")

    parts.append("## 经验提炼")
    parts.append("待人工补充：可复用的经验教训。")
    parts.append("")
    parts.append("## 关联")
    parts.append(f"- 项目: [[{file.replace('.md', '')}]]")
    parts.append("- 经验库: [[01-造价核心/造价实战经验库]]")
    parts.append("")
    parts.append("---")
    parts.append("[[知识库首页]]")

    return "\n".join(parts)


def main(dry_run=False):
    print(f"[{datetime.now():%H:%M}] auto_project_review v1.0")

    all_insights = []
    scan_count = 0
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        for pattern in ["**/变更*", "**/策略*", "**/总结*", "**/复盘*", "**/分析*"]:
            for md in sorted(proj_dir.glob(pattern))[:3]:  # 每类最多3个
                if "总览" in md.stem:
                    continue
                result = extract_experience(md)
                if result:
                    all_insights.append(result)
                    scan_count += 1

    # 按项目分组
    from collections import defaultdict
    by_project = defaultdict(list)
    for item in all_insights:
        by_project[item["project"]].extend(item["insights"])

    print(f"  scanned: {scan_count} files")
    print(f"  projects with insights: {len(by_project)}")

    generated = 0
    for project, insights in by_project.items():
        if len(insights) < 2:
            continue
        entry = {
            "project": project,
            "file": f"09-项目资料/{project}",
            "insights": sorted(insights, key=lambda x: len(x['content']), reverse=True),
        }
        card = generate_case_card(entry)
        if dry_run:
            print(f"  [DRY] {project}: {len(insights)} insights")
        else:
            safe_name = project.replace("/", "-").replace("\\", "-")
            out_path = CASE_DB_DIR / f"案例复盘_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(card, encoding='utf-8')
            print(f"  [OK] {out_path.relative_to(VAULT)}")
            generated += 1

    print(f"  {'DRY RUN' if dry_run else 'DONE'}: {generated} cases")
    return generated


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
