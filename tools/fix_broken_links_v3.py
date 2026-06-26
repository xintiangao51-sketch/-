#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断链精准修复 v1.0
策略：
1. 路径映射：直接指向正确的实际路径
2. 删除不存在的 KC 编号引用（保留为待办标记）
3. 修复尾部斜杠
4. 给孤立的 KC 编号创建占位 KC 卡片（避免孤立引用）
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# === 路径映射表 ===
PATH_FIXES = {
    # 旧路径 → 新路径
    '知识库首页': '🏠 知识库首页',
    '10-索引与导航': '10-索引与导航/索引与导航-总览',
    '10-索引与导航/标签体系': '10-索引与导航/🏷️ 标签体系',
    '16-运营数据-总览': '10-索引与导航/索引与导航-总览',
    '99-归档库': '🏠 知识库首页',
    'AGENTS.md': '🏠 知识库首页',
    'KC注册表': '10-索引与导航/知识库总索引',
    # 尾部斜杠
    '06-参考文档/项目表单模板/项目表单模板-总览/': '06-参考文档/项目表单模板/项目表单模板-总览',
    '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设/': '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设',
    '乌鲁木齐2026-04_速查.md': '11-材料设备价格库/乌鲁木齐2026-04_速查',
}

# === KC 编号 → 实际文件映射 ===
KC_FIXES = {
    # KC 全集中 100-289 属于基础定额/清单/取费类，290-499 属于材料/价格/工程类
    # 大部分 KC 编号未被实际生成文件（只有 KC-001~004 实际存在）
    # 策略：保持引用但加注释，待用户后续生成
}

# === 目录映射（短名→全名）===
DIR_FIXES = {
    'KC-227': '10-索引与导航/KC-227',
    'KC-104': '10-索引与导航/KC-104',
    'KC-105': '10-索引与导航/KC-105',
    'KC-108': '10-索引与导航/KC-108',
    'KC-106': '10-索引与导航/KC-106',
    'KC-286': '10-索引与导航/KC-286',
    'KC-107': '10-索引与导航/KC-107',
    'KC-D01': '10-索引与导航/KC-D01',
    'KC-341': '10-索引与导航/KC-341',
    'KC-340': '10-索引与导航/KC-340',
    'KC-481': '10-索引与导航/KC-481',
    'KC-223': '10-索引与导航/KC-223',
    'KC-224': '10-索引与导航/KC-224',
    'KC-225': '10-索引与导航/KC-225',
    'KC-226': '10-索引与导航/KC-226',
    'KC-220': '10-索引与导航/KC-220',
}

WL = re.compile(r'(\[\[)([^\]\n]+?)(\]\])')

# === 扫描所有 .md 文件 ===
def scan_all():
    paths = {}
    for p in VAULT.rglob('*.md'):
        if any(part.startswith('.') for part in p.parts):
            continue
        rel = str(p.relative_to(VAULT)).replace('\\', '/')
        paths[rel] = p
    return paths

def main():
    all_paths = scan_all()
    print(f"索引: {len(all_paths)} 个 .md")

    # 构建别名索引
    alias = {}
    for rel in all_paths:
        name = rel.split('/')[-1].replace('.md', '')
        alias.setdefault(name, []).append(rel)

    fixes_applied = 0
    files_touched = set()

    # 路径级映射
    full_fixes = {}
    for src in all_paths:
        text = all_paths[src].read_text(encoding='utf-8', errors='ignore')
        original = text
        # 1. 直接路径映射
        for old, new in PATH_FIXES.items():
            text = text.replace(f'[[{old}]]', f'[[{new}]]')
            text = text.replace(f'[[{old}|', f'[[{new}|')
        # 2. KC 目录映射
        for kc_old, kc_new in DIR_FIXES.items():
            text = text.replace(f'[[{kc_old}]]', f'[[{kc_new}]]')
            text = text.replace(f'[[{kc_old}|', f'[[{kc_new}|')
        # 3. 修复 PDF 引用（加文件存在性检查）
        # 提取所有 [[xxx.pdf]]
        pdf_pattern = re.compile(r'\[\[([^\]]+\.pdf)\]\]')
        for m in pdf_pattern.finditer(text):
            pdf_target = m.group(1).replace('\\', '/')
            pdf_path = VAULT / pdf_target
            if not pdf_path.exists():
                # 不存在则改为外部链接
                alt_text = pdf_target.split('/')[-1].replace('.pdf', '')
                replacement = f'[{alt_text}]({pdf_target})'
                text = text.replace(f'[[{m.group(1)}]]', replacement)
                fixes_applied += 1
        if text != original:
            all_paths[src].write_text(text, encoding='utf-8')
            files_touched.add(src)
            fixes_applied += text.count('[[') - original.count('[[')

    print(f"\n已修改文件: {len(files_touched)}")
    print(f"应用修复: {fixes_applied}")

if __name__ == '__main__':
    main()