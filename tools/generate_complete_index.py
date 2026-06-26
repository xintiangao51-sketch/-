#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karpathy 全量索引生成器 - 完整版本
为所有目录添加⚡核心和🔒门控标记
"""

import os
import re
from pathlib import Path

def should_skip_path(path):
    """判断是否应该跳过该路径"""
    skip_patterns = [
        '.obsidian', '.claude', '.git', '.archive', 
        '.tools', '.scripts', '.skillhub-install',
        '99-归档库', '98-原子知识库',
        '__pycache__', '.pyc'
    ]
    
    for pattern in skip_patterns:
        if pattern in str(path):
            return True
    return False

def get_file_summary(file_path):
    """从文件内容中提取摘要"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            summary = re.sub(r'^#+\s*', '', first_line)
            summary = re.sub(r'[*#\[\](){}]', '', summary)
            return summary[:15] if summary else "文档"
    except:
        return "文档"

def analyze_core_files():
    """分析所有目录的核心文件"""
    core_files = {
        # 00-工作台（已有）
        r'00-工作台/工作台-总览': '工作台总览',
        r'00-工作台/常用参数-新疆2024': '常用参数速查',
        
        # 01-造价核心（已有）
        r'01-造价核心/定额与计价/定额与计价-总览': '定额与计价总览',
        r'01-造价核心/工程量计算/工程量计算-总览': '工程量计算总览',
        r'01-造价核心/造价实战经验库': '造价实战经验库',
        
        # 02-业务中台
        r'02-业务中台/业务中台-总览': '业务中台总览',
        r'02-业务中台/AI方法论/总览': 'AI方法论总览',
        
        # 03-合同与法务
        r'03-合同与法务/合同与法务-总览': '合同法务总览',
        r'03-合同与法务/合同审查实战清单': '合同审查清单',
        r'03-合同与法务/高风险条款库': '高风险条款库',
        
        # 04-施工方案
        r'04-施工方案/施工方案-总览': '施工方案总览',
        r'04-施工方案/安全管理/安全管理-总览': '安全管理总览',
        r'04-施工方案/施工组织设计/施工组织设计-总览': '施工组织设计',
        
        # 05-投标报价
        r'05-投标报价/投标报价-总览': '投标报价总览',
        r'05-投标报价/招标文件/招标文件-总览': '招标文件总览',
        r'05-投标报价/投标编制/投标报价编制全流程': '投标编制流程',
        
        # 06-参考文档
        r'06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设': 'DDC数字驱动',
        
        # 07-AI工具与技能
        r'07-AI工具与技能/AI工具与技能-总览': 'AI工具总览',
        r'07-AI工具与技能/提示词库/提示词库-总览': '提示词库总览',
        r'07-AI工具与技能/Skills技能/Skills技能-总览': 'Skills技能总览',
        
        # 08-参考规范
        r'08-参考规范/参考规范-总览': '参考规范总览',
        r'08-参考规范/KC-001_造价管理办法_2026修订': '造价管理办法',
        r'08-参考规范/KC-002_GB50500_2024计价标准': 'GB50500计价标准',
        
        # 09-项目资料
        r'09-项目资料/📋 项目资料浓缩索引': '项目资料索引',
        
        # 10-索引与导航（已有）
        r'10-索引与导航/AI-Agent五件套/': 'AI-Agent五件套',
        r'10-索引与导航/知识库管理核心规则': '管理核心规则',
        
        # 11-材料设备价格库
        r'11-材料设备价格库/材料设备价格库-总览': '材料价格总览',
        r'11-材料设备价格库/劳务指导价/劳务指导价-总览': '劳务指导价总览',
        
        # 12-项目案例库
        r'12-项目案例库/项目案例库-总览': '项目案例总览',
        r'12-项目案例库/劳务分包与扩大劳务报价/劳务分包与扩大劳务报价-总览': '劳务分包总览',
        
        # 13-工程图纸
        r'13-工程图纸/工程图纸-总览': '工程图纸总览',
        
        # 14-标准模板
        r'14-标准模板/标准模板-总览': '标准模板总览',
        r'14-标准模板/00-项目总览模板': '项目总览模板',
        r'14-标准模板/输出质量标准与自检清单': '质量标准自检',
        
        # 15-数据资产
        r'15-数据资产/数据资产-总览': '数据资产总览',
        
        # 16-运营数据
        r'16-运营数据/16-运营数据-总览': '运营数据总览',
        
        # 17-知识库引擎
        r'17-知识库引擎/README': '知识库引擎'
    }
    
    return core_files

def analyze_gate_files():
    """分析门控文件"""
    gate_files = {
        # 约束和规范类
        r'10-索引与导航/AI-Agent五件套/': 'AI-Agent五件套',
        r'10-索引与导航/知识库管理核心规则': '管理核心规则',
        
        # 法规和标准
        r'08-参考规范/KC-001_造价管理办法_2026修订': '造价管理办法',
        r'08-参考规范/KC-002_GB50500_2024计价标准': 'GB50500计价标准',
        r'03-合同与法务/高风险条款库': '高风险条款库',
        
        # 质量和控制
        r'14-标准模板/输出质量标准与自检清单': '质量标准自检',
        r'01-造价核心/取费与税金/新疆费率参数体系': '新疆费率参数',
        
        # 重要流程
        r'05-投标报价/投标编制/投标报价编制全流程': '投标编制流程'
    }
    
    return gate_files

def traverse_knowledge_base(root_path):
    """遍历知识库目录结构"""
    root = Path(root_path)
    directories = {}
    
    for item in root.iterdir():
        if item.is_dir() and not should_skip_path(item):
            dir_name = item.name
            if re.match(r'^\d{2}-', dir_name):
                directories[dir_name] = []
                
                for subitem in item.rglob('*'):
                    if subitem.is_file() and subitem.suffix == '.md':
                        rel_path = subitem.relative_to(root)
                        if len(rel_path.parts) > 1:
                            summary = get_file_summary(subitem)
                            directories[dir_name].append((str(rel_path), summary))
    
    return directories

def generate_index_content(directories):
    """生成带完整标记的索引内容"""
    content = "# 鼎梁筑知识库全量索引\n\n"
    content += "> Karpathy 式全量目录。AI 读一遍后即看到所有页面。每次新页面后 AI 追加新行。\n\n"
    content += "## 标记规则\n"
    content += "| 标记 | 含义 | AI 行为 |\n"
    content += "|------|------|---------|\n"
    content += "| ⚡核心 | 架构层面不可跳过 | 处理该域前必须先读此页 |\n"
    content += "| 🔒门控 | 某类操作必读检查点 | 执行对应操作前必须确认约束 |\n\n"
    
    core_patterns = analyze_core_files()
    gate_patterns = analyze_gate_files()
    
    sorted_dirs = sorted(directories.keys())
    
    for dir_name in sorted_dirs:
        dir_title = re.sub(r'^\d{2}-', '', dir_name)
        
        content += f"## {dir_title}（{dir_name}）\n"
        
        files = directories[dir_name]
        files.sort(key=lambda x: x[0])
        
        for file_path, summary in files:
            # 判断标记类型
            marker = ""
            
            # 检查是否为核心文件
            for pattern, _ in core_patterns.items():
                if re.search(pattern, file_path.replace('\\', '/')):
                    marker = "⚡ "
                    break
            
            # 检查是否为门控文件
            if not marker:
                for pattern, _ in gate_patterns.items():
                    if re.search(pattern, file_path.replace('\\', '/')):
                        marker = "🔒 "
                        break
            
            # 生成Obsidian链接格式
            link_path = file_path.replace('\\', '/').replace('.md', '')
            content += f"- {marker}[[{link_path}]] — {summary}\n"
        
        content += "\n"
    
    content += "---\n"
    content += "*索引生成时间：2026-06-26，已为所有目录添加 ⚡核心 和 🔒门控 标记*\n"
    
    return content

def main():
    """主函数"""
    root_path = r"D:\知识库"
    output_path = r"D:\知识库\10-索引与导航\索引.md"
    
    print("🔍 开始遍历知识库目录...")
    directories = traverse_knowledge_base(root_path)
    
    print(f"📊 发现 {len(directories)} 个主要目录:")
    for dir_name in directories:
        print(f"  - {dir_name}: {len(directories[dir_name])} 个文件")
    
    print("📝 分析并生成带完整标记的索引内容...")
    content = generate_index_content(directories)
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 完整标记索引已生成: {output_path}")
    
    # 统计标记数量
    core_count = len(analyze_core_files())
    gate_count = len(analyze_gate_files())
    print(f"📋 标记统计:")
    print(f"  ⚡核心: {core_count} 个")
    print(f"  🔒门控: {gate_count} 个")
    print(f"  总计: {core_count + gate_count} 个")

if __name__ == "__main__":
    main()
