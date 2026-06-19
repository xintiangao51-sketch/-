import os, sys
from pathlib import Path
from collections import defaultdict

# Enable UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SRC = Path(r"D:\高治国资料")
DST = Path(r"D:\知识库\09-项目资料")

# Mapping: 高治国资料 project folder -> 知识库/09-项目资料/ target folder
# Key = (relative path pattern, target folder name, create_if_missing)
MAPPINGS = [
    # 01_进行中项目
    (r"01_进行中项目\X125昌南地质灾害", "昌吉地质灾害"),
    (r"01_进行中项目\海岸广场项目", "海岸广场"),
    (r"01_进行中项目\特克斯阳光谷", "特克斯阳光谷"),
    (r"01_进行中项目\道班房项目", "道班房"),
    # 2022
    (r"2022\青河G331项目", "青河G331"),
    (r"2022\华能阿克陶项目", "华能阿克陶"),
    (r"2022\成达万高铁", "成达万高铁"),
    (r"2022\拜城克深5项目", "拜城克深5"),
    # 2023
    (r"2023\口岸陈文勇项目", "口岸陈文勇"),
    (r"2023\巍山镇安置区项目", "巍山镇安置区"),
    (r"2023\那拉提桥梁工程", "那拉提桥梁"),
    # 2024
    (r"2024\天山乡项目", "天山乡"),
    # 2025
    (r"2025\G0711乌尉高速", "乌尉高速"),
    (r"2025\G217图木舒克服务区", "图木舒克"),
    (r"2025\博乐前进水源护坡", "博乐护坡"),
    (r"2025\喀什体育运动学校", "喀什体校"),
    (r"2025\新疆和田项目", "和田项目"),
    (r"2025\米兰道路工程", "米兰道路"),
    # 2026
    (r"2026\米东煤矿矿坑覆盖", "米东煤矿"),
    (r"2026\通衢隧道洞口坡面治理", "通衢隧道"),
    (r"2026\鄯善启创科技中建五局", "鄯善启创"),
    (r"2026\阿勒泰机场劳务", "阿勒泰机场"),
    # 鼎梁柱-公司运营
    (r"鼎梁柱-公司运营", "鼎梁筑/公司运营"),
]

# Build a set of all filenames (lowercase, stem only for matching) in each DST project
print("=== Scanning knowledge base for existing files ===\n")
dst_files = defaultdict(set)  # target_folder -> set of (filename_lower_stem)
for folder_path, proj_name in MAPPINGS:
    target = DST / proj_name
    if target.exists():
        for f in target.rglob("*"):
            if f.is_file() and f.name != "_index.md" and f.name != "README.md":
                dst_files[proj_name].add(f.name.lower())
    print(f"  {proj_name}: {len(dst_files[proj_name])} files in KB")

print(f"\n=== Scanning 高治国资料 for files to import ===\n")

# Now scan source and find missing
total_new = 0
total_exists = 0
report = []

for src_pattern, proj_name in MAPPINGS:
    src_dir = SRC / src_pattern
    if not src_dir.exists():
        continue
    
    existing = dst_files.get(proj_name, set())
    new_files = []
    exist_files = 0
    total_src = 0
    
    for f in src_dir.rglob("*"):
        if not f.is_file():
            continue
        total_src += 1
        name_lower = f.name.lower()
        if name_lower in existing:
            exist_files += 1
        else:
            new_files.append(f)
    
    total_new += len(new_files)
    total_exists += exist_files
    if new_files or total_src > 0:
        report.append((proj_name, src_pattern, total_src, len(new_files), exist_files))
        if new_files:
            print(f"  📥 {proj_name}: {total_src} total, {len(new_files)} NEW ({exist_files} already in KB)")

# Print summary of projects with no new files
for proj, pattern, src_count, new_count, exist_count in report:
    if new_count == 0 and src_count > 0:
        print(f"  ✅ {proj}: {src_count} files, all already in KB")

print(f"\n=== SUMMARY ===")
print(f"Total files in 高治国资料 (mapped projects): {total_new + total_exists}")
print(f"Already in knowledge base: {total_exists}")
print(f"New files to import: {total_new}")
print(f"Projects with new files: {sum(1 for r in report if r[3] > 0)}")

# Save report for import phase
import json
report_data = []
for proj, pattern, src_count, new_count, exist_count in report:
    if new_count > 0:
        report_data.append({
            "project": proj,
            "src_pattern": pattern,
            "total": src_count,
            "new": new_count,
            "exist": exist_count
        })
with open(r"D:\知识库\.tools\_import_report.json", "w", encoding="utf-8") as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)
print("\nReport saved to .tools/_import_report.json")
