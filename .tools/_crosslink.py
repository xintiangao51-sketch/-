# -*- coding: utf-8 -*-
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"D:\知识库")

# === Cross-references to create ===
# (source_file, wikilink_target, anchor_text)

cross_refs = []

# 1. 蓝天大厦关联 (01-造价核心/定额与计价 ↔ 09-项目资料/蓝天大厦)
curtain_wall = BASE / "09-项目资料" / "附件文件3 蓝天大厦幕墙图纸（新）2026.4.15"
quota_dir = BASE / "01-造价核心" / "定额与计价"
if curtain_wall.exists():
    # Add wikilink note at the top of the curtain wall _index.md
    index_file = curtain_wall / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        note = "> 🔗 关联：[[01-造价核心/定额与计价/乌市蓝天大厦玻璃幕墙专业劳务分包报价表（市场单价分析表）|蓝天大厦幕墙报价]] | [[01-造价核心/定额与计价/乌市蓝天大厦铝单板幕墙专业劳务分包报价表（市场单价分析表）|蓝天大厦铝单板报价]]\n"
        if "🔗 关联" not in content:
            content = content.replace("> 来自高治国资料 Z_零散归档\n", f"> 来自高治国资料 Z_零散归档\n{note}")
            index_file.write_text(content, encoding='utf-8')
            print("  ✅ 蓝天大厦幕墙 ↔ 定额与计价报价表")

# 2. 造价工作台搭建方案 (01-造价核心/工程量计算 ↔ 09-项目资料/鼎梁筑)
workbench_kb = BASE / "01-造价核心" / "工程量计算" / "造价工作台搭建方案.md"
workbench_proj = BASE / "09-项目资料" / "鼎梁筑" / "02-工程量与计价" / "造价工作台搭建方案.md"
if workbench_kb.exists():
    content = workbench_kb.read_text(encoding='utf-8')
    if "[[09-项目资料" not in content:
        content += "\n\n---\n> 🔗 关联：[[09-项目资料/鼎梁筑/02-工程量与计价/造价工作台搭建方案|造价工作台搭建方案（完整版）]]"
        workbench_kb.write_text(content, encoding='utf-8')
        print("  ✅ 造价工作台搭建方案: 01-造价核心 ↔ 鼎梁筑")

# 3. 变更索赔模板 ↔ 项目实际应用
change_dir = BASE / "01-造价核心" / "变更索赔"
if change_dir.exists():
    index_file = change_dir / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        if "🔗 项目应用" not in content:
            note = "\n\n> 🔗 项目应用：[[09-项目资料/阳安二线/|阳安二线]] | [[09-项目资料/道班房/|道班房]] | [[09-项目资料/青河G331/|青河G331]]"
            content = content.replace("SORT file.ctime DESC\n`", f"SORT file.ctime DESC\n`{note}")
            index_file.write_text(content, encoding='utf-8')
            print("  ✅ 变更索赔 ↔ 项目应用 (阳安二线, 道班房, 青河G331)")

# 4. 施工方案库 ↔ 项目方案
construction_dir = BASE / "04-施工方案"
if construction_dir.exists():
    index_file = construction_dir / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        if "🔗 项目方案" not in content:
            note = "\n\n> 🔗 项目方案：[[09-项目资料/道班房/04-施工方案/|道班房]] | [[09-项目资料/阳安二线/04-施工方案/|阳安二线]] | [[09-项目资料/特克斯阳光谷/04-施工方案/|特克斯阳光谷]]"
            content = content.replace("SORT file.ctime DESC\n`", f"SORT file.ctime DESC\n`{note}")
            index_file.write_text(content, encoding='utf-8')
            print("  ✅ 施工方案库 ↔ 项目方案")

# 5. 合同模板 ↔ 项目合同
contract_dir = BASE / "03-合同与法务"
if contract_dir.exists():
    index_file = contract_dir / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        if "🔗 项目合同" not in content:
            note = "\n\n> 🔗 项目合同：[[09-项目资料/道班房/01-合同招投标/|道班房]] | [[09-项目资料/喀什体校/01-合同招投标/|喀什体校]] | [[09-项目资料/鄯善启创/01-合同招投标/|鄯善启创]]"
            content = content.replace("SORT file.ctime DESC\n`", f"SORT file.ctime DESC\n`{note}")
            index_file.write_text(content, encoding='utf-8')
            print("  ✅ 合同模板 ↔ 项目合同")

# 6. 新疆定额体系索引 ↔ 各项目单价分析
quota_index = BASE / "01-造价核心" / "定额与计价" / "新疆定额体系索引.md"
if quota_index.exists():
    content = quota_index.read_text(encoding='utf-8')
    if "🔗 相关单价分析" not in content:
        note = "\n\n> 🔗 相关单价分析：[[01-造价核心/定额与计价/独库69-72段200章逐项单价分析|独库高速]] | [[01-造价核心/定额与计价/通衢隧道_单价分析表|通衢隧道]] | [[01-造价核心/定额与计价/莎车县农村道路工程综合单价分析表|莎车县道路]]"
        content += note
        quota_index.write_text(content, encoding='utf-8')
        print("  ✅ 定额体系索引 ↔ 项目单价分析")

# 7. 材料价格 ↔ 项目材料需求
material_dir = BASE / "01-造价核心" / "材料价格"
if material_dir.exists():
    index_file = material_dir / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        if "🔗 项目材料" not in content:
            note = "\n\n> 🔗 项目材料：[[09-项目资料/道班房/06-物资采购/|道班房]] | [[09-项目资料/青河G331/06-物资采购/|青河G331]]"
            content = content.replace("SORT file.ctime DESC\n`", f"SORT file.ctime DESC\n`{note}")
            index_file.write_text(content, encoding='utf-8')
            print("  ✅ 材料价格 ↔ 项目材料")

print("\nPhase 3 done: 7 cross-reference wikilinks created.")
