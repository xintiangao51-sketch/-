# -*- coding: utf-8 -*-
import os, sys, shutil, re
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"D:\知识库\09-项目资料")

CATEGORIES = {
    "01-合同招投标": ["合同", "协议", "承包", "招投标", "投标", "招标", "中标", "委托书", "授权"],
    "02-工程量与计价": ["报价", "计价", "单价", "成本", "费用", "清单", "预算", "核算", "工程量", "价格", "询价单"],
    "03-图纸资料": ["图纸", "设计", "施工图", "平面", "剖面", "大样", "节点", "CAD", "dwg", "PDF图"],
    "04-施工方案": ["方案", "施组", "组织设计", "进度计划", "报告", "汇报", "施工方案", "技术方案", "专项方案"],
    "05-变更签证": ["变更", "签证", "签认", "索赔", "洽商", "联系单", "变更设计", "签证单"],
    "06-物资采购": ["材料", "采购", "物资", "供应", "设备", "材料表", "材料单", "需求计划", "采购单"],
    "07-质量安全": ["安全", "质量", "检查", "整改", "验收", "检测", "试验", "监督", "许可"],
    "08-结算归档": ["结算", "竣工", "工资", "支付", "发票", "回执", "付款", "拨付", "代发", "委托书", "承诺函", "汇总表", "统计表", "台账", "登记表"],
    "09-人员与行政": ["人员", "花名册", "信息", "机构", "身份证", "银行卡", "驾照", "行驶证", "保险", "简历", "证件", "资格", "资质", "人事"],
}

EXCLUDE_PREFIXES = ["01-", "02-", "03-", "04-", "05-", "06-", "07-", "08-", "09-", "_index", "README"]
TEMPLATE = '---\ntags: [项目, 索引]\ncreated: 2026-06-12\ntype: index\n---\n# {title}\n\n`dataview\nTABLE file.ctime as "创建时间"\nFROM "09-项目资料/{parent}/{title}"\nWHERE file.name != "_index"\nSORT file.ctime DESC\n`\n'

def classify_file(name):
    """Return category name based on filename."""
    name_lower = name.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in name_lower:
                return cat
    # Special: .dwg files → 03-图纸资料
    if name_lower.endswith('.dwg') or name_lower.endswith('.dxf'):
        return "03-图纸资料"
    # Special: .pdf with 图纸-related → 03
    # Default → 02-工程量与计价
    return "02-工程量与计价"

def ensure_categories(project_path):
    """Create 01-09 directories if they don't exist."""
    for cat in CATEGORIES:
        (project_path / cat).mkdir(parents=True, exist_ok=True)

def organize_project(project_path, project_name):
    """Classify flat files into 01-09 subdirs."""
    moved = 0
    ensure_categories(project_path)
    
    for item in project_path.iterdir():
        if not item.is_file():
            continue
        name = item.name
        if name == "_index.md" or name == "README.md" or any(name.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        
        cat = classify_file(name)
        dst = project_path / cat / name
        if not dst.exists():
            shutil.move(str(item), str(dst))
            moved += 1
    
    # Create/update _index.md for each category subfolder
    for cat in CATEGORIES:
        cat_dir = project_path / cat
        index_file = cat_dir / "_index.md"
        if cat_dir.exists() and not index_file.exists():
            parent_rel = project_path.relative_to(BASE)
            content = TEMPLATE.format(title=cat, parent=str(parent_rel).replace("\\","/"))
            index_file.write_text(content, encoding="utf-8")
    
    return moved

# Projects to organize (focus on those with flat files)
projects_to_org = []
for proj_dir in sorted(BASE.iterdir()):
    if not proj_dir.is_dir():
        continue
    flat_count = sum(1 for f in proj_dir.iterdir() if f.is_file() and f.name != "_index.md" and f.name != "README.md")
    if flat_count > 0:
        projects_to_org.append((proj_dir, flat_count))

# Also handle nested projects (鼎梁筑/公司运营)
dingliangzhu_ops = BASE / "鼎梁筑" / "公司运营"
if dingliangzhu_ops.exists():
    flat_count = sum(1 for f in dingliangzhu_ops.iterdir() if f.is_file() and f.name != "_index.md" and f.name != "README.md")
    if flat_count > 0:
        projects_to_org.append((dingliangzhu_ops, flat_count))

print("=== Phase 2: Organizing flat files into 01-09 structure ===\n")
total_moved = 0
for proj_path, flat_count in sorted(projects_to_org, key=lambda x: -x[1]):
    if flat_count == 0:
        continue
    proj_name = str(proj_path.relative_to(BASE))
    moved = organize_project(proj_path, proj_name)
    total_moved += moved
    if moved > 0:
        print(f"  {proj_name}: {moved} flat files -> 01-09 subdirs")

print(f"\nTotal flat files classified: {total_moved}")
