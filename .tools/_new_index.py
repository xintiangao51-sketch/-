from pathlib import Path

base = Path(r"D:\知识库")

new_projects = [
    ("华能阿克陶", "项目/华能阿克陶"),
    ("成达万高铁", "项目/成达万高铁"),
    ("拜城克深5", "项目/拜城克深5"),
    ("口岸陈文勇", "项目/口岸陈文勇"),
    ("巍山镇安置区", "项目/巍山镇安置区"),
    ("那拉提桥梁", "项目/那拉提桥梁"),
    ("天山乡", "项目/天山乡"),
    ("和田项目", "项目/和田项目"),
    ("阿勒泰机场", "项目/阿勒泰机场"),
]

TEMPLATE = '---\ntags: [项目, {tag}, 索引]\ncreated: 2026-06-12\ntype: index\n---\n# {title}\n\n`dataview\nTABLE file.ctime as "创建时间", tags as "标签"\nFROM "09-项目资料/{title}"\nWHERE file.name != "{new_file}" AND file.name != "README"\nSORT file.ctime DESC\n`\n'

count = 0
for name, tag in new_projects:
    new_file = f"{name}-项目总览"
    fp = base / "09-项目资料" / name / f"{name}-项目总览.md"
    fp.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE.format(tag=tag, title=name, new_file=new_file)
    fp.write_text(content, encoding="utf-8")
    count += 1
    print(f"  Created: 09-项目资料/{name}/{name}-项目总览.md")

# Also for 鼎梁筑/公司运营
new_file2 = "公司运营-总览"
fp2 = base / "09-项目资料" / "鼎梁筑" / "公司运营" / "公司运营-总览.md"
fp2.parent.mkdir(parents=True, exist_ok=True)
content2 = '---\ntags: [项目, 项目/鼎梁筑, 索引]\ncreated: 2026-06-12\ntype: index\n---\n# 公司运营\n\n`dataview\nTABLE file.ctime as "创建时间", tags as "标签"\nFROM "09-项目资料/鼎梁筑/公司运营"\nWHERE file.name != "公司运营-总览" AND file.name != "README"\nSORT file.ctime DESC\n`\n'
fp2.write_text(content2, encoding="utf-8")
count += 1
print(f"  Created: 09-项目资料/鼎梁筑/公司运营/公司运营-总览.md")

print(f"\n{count} index files created for new projects.")
