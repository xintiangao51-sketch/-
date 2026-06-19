import os
from pathlib import Path

base = Path(r"D:\知识库")

sections = [
    (r"01-造价核心\取费与税金", "[造价, 造价/取费, 索引]", "取费与税金"),
    (r"01-造价核心\变更索赔", "[造价, 造价/变更, 索引]", "变更索赔"),
    (r"01-造价核心\定额与计价", "[造价, 造价/定额, 索引]", "定额与计价"),
    (r"01-造价核心\工程量计算", "[造价, 造价/工程量, 索引]", "工程量计算"),
    (r"01-造价核心\材料价格", "[造价, 造价/材料, 索引]", "材料价格"),
    (r"02-工程图纸\平法讲座", "[图纸, 索引]", "平法讲座"),
    (r"02-工程图纸\待分类", "[图纸, 索引]", "待分类"),
    (r"02-工程图纸\练习图纸", "[图纸, 索引]", "练习图纸"),
    (r"02-工程图纸\钢筋图集", "[图纸, 索引]", "钢筋图集"),
    (r"03-合同与法务\FIDIC条款", "[合同, 合同/FIDIC, 索引]", "FIDIC条款"),
    (r"03-合同与法务\建筑法规", "[合同, 索引]", "建筑法规"),
    (r"03-合同与法务\建设合同模板", "[合同, 合同/模板, 索引]", "建设合同模板"),
    (r"03-合同与法务\施工法务", "[合同, 索引]", "施工法务"),
    (r"04-施工方案\安全管理", "[施工, 施工/安全, 索引]", "安全管理"),
    (r"04-施工方案\房建方案库", "[施工, 施工/方案, 索引]", "房建方案库"),
    (r"04-施工方案\施工组织设计", "[施工, 施工/施组, 索引]", "施工组织设计"),
    (r"04-施工方案\管理制度", "[施工, 索引]", "管理制度"),
    (r"04-施工方案\质量管理体系", "[施工, 施工/质量, 索引]", "质量管理体系"),
    (r"04-施工方案\集团体系文件", "[施工, 索引]", "集团体系文件"),
    (r"04-施工方案\集团管理制度", "[施工, 索引]", "集团管理制度"),
    (r"04-施工方案\项目管理办法", "[施工, 索引]", "项目管理办法"),
    (r"04-施工方案\高新施工技术", "[施工, 索引]", "高新施工技术"),
    (r"05-投标报价\中铁二十五局投标资料", "[投标, 索引]", "中铁二十五局投标资料"),
    (r"05-投标报价\投标文件", "[投标, 投标/编制, 索引]", "投标文件"),
    (r"05-投标报价\招标文件", "[投标, 投标/招标, 索引]", "招标文件"),
    (r"05-投标报价\项目报价", "[投标, 投标/报价, 索引]", "项目报价"),
    (r"06-参考文档\其他", "[模板, 索引]", "其他"),
    (r"06-参考文档\待分类Excel", "[模板, 索引]", "待分类Excel"),
    (r"06-参考文档\待分类PDF", "[模板, 索引]", "待分类PDF"),
    (r"06-参考文档\待分类Word", "[模板, 索引]", "待分类Word"),
    (r"06-参考文档\项目表单模板", "[模板, 索引]", "项目表单模板"),
    (r"07-AI工具与技能\drawing-analyzer", "[AI, 索引]", "drawing-analyzer"),
    (r"07-AI工具与技能\Hermes配置", "[AI, 索引]", "Hermes配置"),
    (r"07-AI工具与技能\JSON文件", "[AI, 索引]", "JSON文件"),
    (r"07-AI工具与技能\MCP插件", "[AI, 索引]", "MCP插件"),
    (r"07-AI工具与技能\md文档", "[AI, 索引]", "md文档"),
    (r"07-AI工具与技能\pdf", "[AI, 索引]", "pdf"),
    (r"07-AI工具与技能\Skills技能", "[AI, 索引]", "Skills技能"),
    (r"07-AI工具与技能\提示词库", "[AI, 索引]", "提示词库"),
]

projects = [
    ("中铁二十五局", "项目/中铁二十五局"),
    ("乌尉高速", "项目/乌尉高速"),
    ("博乐护坡", "项目/博乐护坡"),
    ("喀什体校", "项目/喀什体校"),
    ("图木舒克", "项目/图木舒克"),
    ("昌吉地质灾害", "项目/昌吉地质灾害"),
    ("海岸广场", "项目/海岸广场"),
    ("特克斯阳光谷", "项目/特克斯阳光谷"),
    ("科特迪瓦项目", "项目/科特迪瓦"),
    ("米东煤矿", "项目/米东煤矿"),
    ("米兰道路", "项目/米兰道路"),
    ("通衢隧道", "项目/通衢隧道"),
    ("道班房", "项目/道班房"),
    ("鄯善启创", "项目/鄯善启创"),
    ("阳安二线", "项目/阳安二线"),
    ("青河G331", "项目/青河G331"),
    ("高新项目", "项目/高新项目"),
    ("鼎梁筑", "项目/鼎梁筑"),
]

TEMPLATE = '---\ntags: {tags}\ncreated: 2026-06-12\ntype: index\n---\n# {title}\n\n`dataview\nTABLE file.ctime as "创建时间", tags as "标签"\nFROM "{folder}"\nWHERE file.name != "{new_file}" AND file.name != "README"\nSORT file.ctime DESC\n`\n'

count = 0
for folder_path, tags, title in sections:
    new_file = f"{title}-总览"
    fp = base / folder_path / f"{new_file}.md"
    fp.parent.mkdir(parents=True, exist_ok=True)
    folder = str(fp.parent.relative_to(base)).replace("\\", "/")
    content = TEMPLATE.format(tags=tags, title=title, folder=folder, new_file=new_file)
    fp.write_text(content, encoding="utf-8")
    count += 1

for name, tag in projects:
    new_file = f"{name}-项目总览"
    new_path = "09-项目资料\\" + name + f"\\{name}-项目总览.md"
    fp = base / new_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    folder = "09-项目资料/" + name
    content = TEMPLATE.format(tags="[项目, " + tag + ", 索引]", title=name, folder=folder, new_file=new_file)
    fp.write_text(content, encoding="utf-8")
    count += 1

print("Phase 3 done: " + str(count) + " index files created.")
