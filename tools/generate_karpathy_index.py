#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karpathy 全量索引生成器
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
    
    # 检查是否包含跳过模式
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

def traverse_knowledge_base(root_path):
    """遍历知识库目录结构"""
    root = Path(root_path)
    directories = {}
    
    # 获取所有第一级目录（00-17编号开头的）
    for item in root.iterdir():
        if item.is_dir() and not should_skip_path(item):
            dir_name = item.name
            # 匹配数字编号目录
            if re.match(r'^\d{2}-', dir_name):
                directories[dir_name] = []
                
                # 遍历子目录和文件
                for subitem in item.rglob('*'):
                    if subitem.is_file() and subitem.suffix == '.md':
                        # 计算相对路径
                        rel_path = subitem.relative_to(root)
                        # 跳过根目录的md文件
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
    
    # 按目录顺序排序
    sorted_dirs = sorted(directories.keys())
    
    for dir_name in sorted_dirs:
        # 提取目录中文名
        dir_title = re.sub(r'^\d{2}-', '', dir_name)
        
        content += f"## {dir_title}（{dir_name}）\n"
        
        # 按路径排序文件
        files = directories[dir_name]
        files.sort(key=lambda x: x[0])
        
        for file_path, summary in files:
            # 生成Obsidian链接格式
            link_path = file_path.replace('\\', '/').replace('.md', '')
            content += f"- [[{link_path}]] — {summary}\n"
        
        content += "\n"
    
    content += "---\n"
    content += "*索引生成时间：自动生成，待人工审查补充 ⚡🔒 标记*\n"
    
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
    
    print("📝 生成索引内容...")
    content = generate_index_content(directories)
    
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 索引已生成: {output_path}")
    print("\n📋 下一步建议:")
    print("1. 优先为 01-造价核心 和 00-工作台 添加 ⚡核心 标记")
    print("2. 为 10-索引与导航 添加 🔒门控 标记")
    print("3. 逐域人工审查，确保关键页面已标记")

if __name__ == "__main__":
    main()
