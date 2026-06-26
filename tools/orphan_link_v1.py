#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""孤岛页面关联 v1 — 给孤岛添加链接关系"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# 孤岛页面列表
ORPHAN_PAGES = [
    "AGENTS.md",
    "06-参考文档/2025年房屋建筑与装饰工程工程量计算规范.md",
    "06-参考文档/工程量清单项目特征描述指南_标准页码版.md",
    "06-参考文档/工程量清单项目特征描述指南_章节标记版.md",
    "06-参考文档/工程量清单项目特征描述指南_连续文本版.md",
    "06-参考文档/建筑与装饰工程工程量清单项目特征描述指南.md",
    "06-参考文档/建设工程施工机械台班费用编制规则.md",
    "06-参考文档/水利工程施工机械台时费定额2024.md",
    "06-参考文档/水利设备安装工程预算定额2024(OCR版).md",
    "06-参考文档/水土保持工程概算定额2025.md",
]

# 给每个孤岛页面添加"推荐阅读"部分链接到相关页面
related_links = {
    "AGENTS.md": [
        "[[10-索引与导航/AI-Agent五件套/HERMES_PROFILE]]",
        "[[10-索引与导航/AI-Agent五件套/CLAUDE_CODE_PROFILE]]",
        "[[知识库规范]]",
    ],
    "2025年房屋建筑与装饰工程工程量计算规范.md": [
        "[[10-索引与导航/KB-140_2025版工程量计算规范_房屋建筑与装饰]]",
        "[[08-参考规范/参考规范-总览]]",
    ],
    "工程量清单项目特征描述指南_标准页码版.md": [
        "[[10-索引与导航/KB-138_工程量清单项目特征描述指南]]",
        "[[06-参考文档/建筑与装饰工程工程量清单项目特征描述指南]]",
    ],
    "工程量清单项目特征描述指南_章节标记版.md": [
        "[[10-索引与导航/KB-138_工程量清单项目特征描述指南]]",
        "[[06-参考文档/建筑与装饰工程工程量清单项目特征描述指南]]",
    ],
    "工程量清单项目特征描述指南_连续文本版.md": [
        "[[10-索引与导航/KB-138_工程量清单项目特征描述指南]]",
        "[[06-参考文档/建筑与装饰工程工程量清单项目特征描述指南]]",
    ],
    "建筑与装饰工程工程量清单项目特征描述指南.md": [
        "[[10-索引与导航/KB-138_工程量清单项目特征描述指南]]",
        "[[01-造价核心/定额与计价/定额与计价-总览]]",
    ],
    "建设工程施工机械台班费用编制规则.md": [
        "[[10-索引与导航/KB-137_建设工程施工机械台班费用编制规则]]",
        "[[01-造价核心/定额与计价/定额与计价-总览]]",
    ],
    "水利工程施工机械台时费定额2024.md": [
        "[[10-索引与导航/KB-139_水利工程定额体系_2024]]",
        "[[01-造价核心/定额与计价/定额与计价-总览]]",
    ],
    "水利设备安装工程预算定额2024(OCR版).md": [
        "[[10-索引与导航/KB-139_水利工程定额体系_2024]]",
        "[[01-造价核心/定额与计价/定额与计价-总览]]",
    ],
    "水土保持工程概算定额2025.md": [
        "[[10-索引与导航/KB-139_水利工程定额体系_2024]]",
        "[[01-造价核心/定额与计价/定额与计价-总览]]",
    ],
}

files_touched = 0

for page in ORPHAN_PAGES:
    page_path = VAULT / page
    if not page_path.exists():
        print(f"不存在: {page}")
        continue
    
    text = page_path.read_text(encoding='utf-8', errors='ignore')
    
    # 如果没有"推荐阅读"部分，添加它
    if "## 推荐阅读" not in text and "---" in text:
        # 找到frontmatter结束位置
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2]
            
            # 获取文件名对应的链接
            filename = page_path.name
            links = related_links.get(filename, ["[[06-参考文档/参考文档-总览]]"])
            
            recommended = "\n\n## 推荐阅读\n\n" + "\n".join([f"- {link}" for link in links]) + "\n"
            
            new_text = f"---{frontmatter}---{content}{recommended}"
            page_path.write_text(new_text, encoding='utf-8')
            files_touched += 1
            print(f"已关联: {page}")

print(f"\n已处理孤岛页面: {files_touched}")
