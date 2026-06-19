# -*- coding: utf-8 -*-
import os, sys, shutil
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r"D:\知识库\09-项目资料")
LOOSE = BASE / "零散项目"

# 合并映射: 空壳文件夹 → 有内容的规范名
MERGE_MAP = {
    "新疆中科能源项目图纸": "新疆中科能源项目",
    "吐哈油田鄯善东风电项目": "吐哈油田鄯善东风电",
    "和田昆仑文化园（一期）": "和田昆仑文化园一期",
    "乌市米东区农业水价综合改革项目": "乌市米东区水价改革",
    "S334乌恰县公路结构物工程": "S334乌恰县公路结构物",
    "G219温泉至霍尔果斯公路防护工程": "G219温泉霍尔果斯防护",
    "兰张（武金段）": "兰张武金段",
    "昌吉州地质灾害治理项目呼18": "昌吉州地质灾害治理呼18",
    "中煤条湖项目110KV变电站、职工食堂装修工程": "中煤条湖变电站",
    "智控试验室配套建设项目": "智控试验室配套建设",
    "乌市沙区老旧改造管网工程": "乌市沙区老旧改造管网",
    "伊犁州都拉塔口岸防护工程": "伊犁州都拉塔口岸防护",
    "水暖电材料询价报价表": "水暖电材料询价",
    "水渠、排水沟等工程展示图片": "水渠排水沟展示图片",
    "甘泉堡项目报价（安装劳务+辅材）": "甘泉堡项目报价",
    "独库高速询价清单": "独库高速询价",
    "昌吉2025农村公路项目防护工程": "昌吉2025农村公路防护",
    "G219线昭苏-温宿ZW-3标防护工程": "G219昭苏温宿防护",
    "敦德": "敦德项目",
    "中建交通G331变电所，水泵房": "中建交通G331变电所",
    "新疆托克逊项目": "新疆托克逊项目",  # 招标资料 merges here
    "S239线五彩湾-吉木萨尔改扩建桥涵工程 - 副本": "S239五彩湾吉木萨尔桥涵",
}

# 与KB已有文件夹冲突的：文件归入现有文件夹
CONFLICT_MERGE = {
    "米兰道路工程": "米兰道路",
    "G0711乌尉高速": "乌尉高速",
    "昌吉地质灾害治理": "昌吉地质灾害",
}

# 2025/2026 临时归档合并
LOOSE_ARCHIVE = "临时归档文件"
LOOSE_ARCHIVE_SOURCES = [
    "2025临时归档", "2026临时归档", "2025散落文件",
    "2025年3月对接项目（杂项）", "2025招标采购资料", "2026临时桌面",
]

# 规范项目名（直接保留原名）
KEEP_NAMES = {
    "116中学综合教学楼", "G219昭苏温宿防护", "G219温泉霍尔果斯防护",
    "G315交安工程", "S334乌恰县公路结构物", "S239五彩湾吉木萨尔桥涵",
    "丝路玉海黄金珠宝大厦", "中建交通G331变电所",
    "中煤条湖变电站", "乌市沙区老旧改造管网", "乌市米东区水价改革",
    "乌市西山部队山体大字", "乌市黄金大厦基坑", "五家渠中水回用",
    "五彩湾融创铝制品厂房", "伊犁化工厂电气安装工程",
    "伊犁州都拉塔口岸防护", "克拉玛依面包大师", "兰张武金段",
    "其他零散文件", "南疆水利", "博乐达镇库房工程", "厂前区装修工程",
    "吐哈油田鄯善东风电", "和田昆仑文化园一期", "孔兑沟矿井锅炉房",
    "孵化器F1", "宁夏肉鸡厂", "富蕴冷库", "山东风电",
    "库尔勒凌爵室外绿化景观", "建筑资质业绩", "新疆托克逊项目",
    "敦德项目", "新建石油项目", "新疆中科能源项目", "新疆华贸百盈",
    "新疆艺术学院坡面防护", "昌吉2025农村公路防护",
    "昌吉州地质灾害治理呼18", "昭苏喀拉峻公路灰土桩",
    "智控试验室配套建设", "水暖电材料询价", "水渠排水沟展示图片",
    "独库高速询价", "甘泉堡项目报价", "若羌车尔臣河输水",
    "莎车县道路提升改造", "蓝琪小镇项目", "那拉提景区结构物工程",
    "郑州航空港青州明渠", "附件文件3 蓝天大厦幕墙图纸（新）2026.4.15",
    "陈文勇联系新建乌市附近变电站项目", "陕西奥维锅炉改造招标文件",
    "霍尔果斯檀悦府房建", "顶管，顶进涵工程",
    "额敏县库鲁斯台草原引洪灌溉工程",
    "清单----莎车县交通运输局2026年乡（镇）村组道路提升改造项目施工(1)",
}

# Step 1: 把空壳文件夹的内容合并到规范名
moved_count = 0
for empty_name, target_name in MERGE_MAP.items():
    src = LOOSE / empty_name
    dst = LOOSE / target_name
    if src.exists() and dst.exists():
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src)
                target_file = dst / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    moved_count += 1
        # Remove empty dirs
        try:
            shutil.rmtree(str(src))
        except:
            pass

# 临时归档合并
archive_dst = LOOSE / LOOSE_ARCHIVE
archive_dst.mkdir(parents=True, exist_ok=True)
for src_name in LOOSE_ARCHIVE_SOURCES:
    src = LOOSE / src_name
    if src.exists():
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src)
                target_file = archive_dst / src_name / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    moved_count += 1
        try:
            shutil.rmtree(str(src))
        except:
            pass

# 合并招标资料到新疆托克逊项目
bid_src = LOOSE / "招标资料(新疆托克逊项目)"
tosksun_dst = LOOSE / "新疆托克逊项目"
if bid_src.exists() and tosksun_dst.exists():
    for f in bid_src.rglob("*"):
        if f.is_file():
            rel = f.relative_to(bid_src)
            target_file = tosksun_dst / "招标资料" / rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if not target_file.exists():
                shutil.move(str(f), str(target_file))
                moved_count += 1
    try:
        shutil.rmtree(str(bid_src))
    except:
        pass

print(f"Step 1: Merged {moved_count} files from empty shells into canonical folders")

# Step 2: 处理冲突项(归入已有文件夹)
for src_name, dst_name in CONFLICT_MERGE.items():
    src = LOOSE / src_name
    dst = BASE / dst_name
    if src.exists() and dst.exists():
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src)
                target_file = dst / "Z_零散补充" / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    moved_count += 1
        try:
            shutil.rmtree(str(src))
        except:
            pass

print(f"Step 2: Merged conflict folders into existing KB projects")

# Step 3: 把所有独立项目提升到 09-项目资料 下
TEMPLATE = '---\ntags: [项目, {tag}, 索引]\ncreated: 2026-06-12\ntype: index\n---\n# {title}\n\n> 来自高治国资料 Z_零散归档\n\n`dataview\nTABLE file.ctime as "创建时间"\nFROM "09-项目资料/{title}"\nWHERE file.name != "_index"\nSORT file.ctime DESC\n`\n'

promoted = 0
existing_folders = {d.name for d in BASE.iterdir() if d.is_dir() and d.name != "零散项目"}

for subdir in sorted(LOOSE.iterdir()):
    if not subdir.is_dir():
        continue
    name = subdir.name
    
    # Skip already-handled
    if name in ("_index.md",):
        continue
    
    # Determine canonical name
    canonical = name
    for k, v in CONFLICT_MERGE.items():
        if name == k:
            canonical = None  # already handled
            break
    
    if canonical is None:
        continue
    
    # Check if this is one of the remaining merge targets
    # (all KEEP_NAMES projects plus LOOSE_ARCHIVE)
    
    dst = BASE / canonical
    if dst.exists():
        # Folder already exists as an independent project
        # Move files under Z_零散补充
        for f in subdir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(subdir)
                target_file = dst / "Z_零散补充" / rel
                target_file.parent.mkdir(parents=True, exist_ok=True)
                if not target_file.exists():
                    shutil.move(str(f), str(target_file))
                    moved_count += 1
        try:
            shutil.rmtree(str(subdir))
        except:
            pass
    else:
        # New independent project - move entire folder
        try:
            shutil.move(str(subdir), str(dst))
            promoted += 1
            # Create _index.md
            tag = f"项目/{canonical}"
            index_content = TEMPLATE.format(tag=tag, title=canonical)
            (dst / "_index.md").write_text(index_content, encoding="utf-8")
            print(f"  ✅ {canonical}")
        except Exception as e:
            print(f"  ❌ {canonical}: {e}")

print(f"\nStep 3: Promoted {promoted} projects to 09-项目资料/")

# Step 4: Clean up empty dirs in 零散项目
for subdir in LOOSE.iterdir():
    if subdir.is_dir():
        try:
            remaining = list(subdir.rglob("*"))
            if not remaining or all(f.is_dir() and not list(f.iterdir()) for f in remaining):
                shutil.rmtree(str(subdir))
        except:
            pass

print("Phase 1 complete.")
