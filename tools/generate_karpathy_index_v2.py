#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karpathy 全量索引生成器 - 添加⚡核心和🔒门控标记
遍历知识库目录，生成AI友好的全量索引
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
    """从文件内容中提取摘要（前30个字符，去掉特殊符号）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # 移除markdown标题符号和特殊符号
            summary = re.sub(r'^#+\s*', '', first_line)
            summary = re.sub(r'[*#\[\](){}]', '', summary)
            # 限制长度
            return summary[:15] if summary else "文档"
    except:
        return "文档"

def is_core_file(file_path):
    """判断是否为核心文件"""
    core_patterns = [
        # 00-工作台核心文件
        r'00-工作台/工作台-总览',
        r'00-工作台/常用参数-新疆2024',
        # 01-造价核心核心文件
        r'01-造价核心/定额与计价/定额与计价-总览',
        r'01-造价核心/工程量计算/工程量计算-总览',
        r'01-造价核心/造价实战经验库'
    ]
    
    for pattern in core_patterns:
        if re.search(pattern, str(file_path)):
            return True
    return False

def is_gate_file(file_path):
    """判断是否为门控文件"""
    gate_patterns = [
        r'10-索引与导航/AI-Agent五件套',
        r'10-索引与导航/知识库管理核心规则'
    ]
    
    for pattern in gate_patterns:
        if re.search(pattern, str(file_path)):
            return True
    return False

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
    """生成索引内容"""
    content = "# 鼎梁筑知识库全量索引\n\n"
    content += "> Karpathy 式全量目录。AI 读一遍后即看到所有页面。每次新页面后 AI 追加新行。\n\n"
    content += "## 标记规则\n"
    content += "| 标记 | 含义 | AI 行为 |\n"
    content += "|------|------|---------|\n"
    content += "| ⚡核心 | 架构层面不可跳过 | 处理该域前必须先读此页 |\n"
    content += "| 🔒门控 | 某类操作必读检查点 | 执行对应操作前必须确认约束 |\n\n"
    
    sorted_dirs = sorted(directories.keys())
    
    for dir_name in sorted_dirs:
        dir_title = re.sub(r'^\d{2}-', '', dir_name)
        
        content += f"## {dir_title}（{dir_name}）\n"
        
        files = directories[dir_name]
        files.sort(key=lambda x: x[0])
        
        for file_path, summary in files:
            # 判断标记类型
            marker = ""
            if is_core_file(file_path):
                marker = "⚡ "
            elif is_gate_file(file_path):
                marker = "🔒 "
            
            # 生成Obsidian链接格式
            link_path = file_path.replace('\\', '/').replace('.md', '')
            content += f"- {marker}[[{link_path}]] — {summary}\n"
        
        content += "\n"
    
    content += "---\n"
    content += "*索引生成时间：2026-06-26，已添加 ⚡核心 和 🔒门控 标记*\n"
    
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
    
    print("📝 生成带标记的索引内容...")
    content = generate_index_content(directories)
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 带标记索引已生成: {output_path}")
    print("📋 已添加的标记:")
    print("  ⚡核心: 00-工作台(2个) + 01-造价核心(3个) = 5个")
    print("  🔒门控: 10-索引与导航(2个)")

if __name__ == "__main__":
    main()
