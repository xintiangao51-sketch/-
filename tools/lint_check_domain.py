#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库域级 Lint 检查器 v1.0
功能：12项检查（断链/死胡同/孤立文件/标签分布/重复/空目录/frontmatter/大文件/过期/命名/图片缺失/引用统计）
用法：python lint_check_domain.py [域名称] [--fix]
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path("D:/知识库")
SKIP_DIRS = {'.obsidian', '.claude', '.git', '.archive', '.tools', '.scripts',
             '99-归档库', '98-原子知识库', '__pycache__', '.ophistory'}

# 12项检查项
CHECK_ITEMS = [
    "断裂链接",
    "死胡同页面",
    "孤立文件",
    "标签分布",
    "重复文件",
    "空目录",
    "frontmatter异常",
    "大文件检测",
    "过期文件",
    "命名规范",
    "图片缺失",
    "引用统计"
]


def should_skip(path):
    for p in path.parts:
        if p in SKIP_DIRS or p.startswith('.'):
            return True
    return False


def collect_files(domain=None):
    """收集需要检查的文件"""
    files = []
    if domain:
        target = VAULT_PATH / domain
        if not target.exists():
            print(f"[Lint] ❌ 域不存在: {domain}")
            return []
    else:
        target = VAULT_PATH

    for f in target.rglob("*.md"):
        if should_skip(f.parent):
            continue
        rel = str(f.relative_to(VAULT_PATH)).replace('\\', '/')
        files.append((f, rel))

    return files


def check_broken_links(files):
    """检查1：断裂链接"""
    issues = []
    idx = {}
    for f, rel in files:
        idx[f.stem] = rel
        idx[rel] = rel
        idx[rel.replace('.md', '')] = rel

    wl = re.compile(r'\[\[([^\]|#]+)')
    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            for link in wl.findall(content):
                target = link.strip()
                if target not in idx:
                    issues.append((rel, target))
        except:
            pass

    return issues


def check_dead_ends(files):
    """检查2：死胡同页面（无任何外链）"""
    issues = []
    outgoing = defaultdict(int)

    wl = re.compile(r'\[\[([^\]|#]+)')
    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            links = wl.findall(content)
            outgoing[rel] = len(links)
        except:
            pass

    for rel, count in outgoing.items():
        if count == 0:
            issues.append(rel)

    return issues


def check_orphans(files):
    """检查3：孤立文件（没有被任何文件引用）"""
    issues = []
    referenced = set()

    wl = re.compile(r'\[\[([^\]|#]+)')
    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            for link in wl.findall(content):
                referenced.add(link.strip())
        except:
            pass

    for f, rel in files:
        stem = f.stem
        if stem not in referenced and rel not in referenced:
            issues.append(rel)

    return issues


def check_tags(files):
    """检查4：标签分布"""
    tag_count = defaultdict(int)
    tag_files = defaultdict(list)

    tl = re.compile(r'tags:\s*\[(.*?)\]')
    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            m = tl.search(content)
            if m:
                tags = [t.strip() for t in m.group(1).split(',')]
                for tag in tags:
                    if tag:
                        tag_count[tag] += 1
                        tag_files[tag].append(rel)
        except:
            pass

    return tag_count, tag_files


def check_duplicates(files):
    """检查5：重复文件（同名文件）"""
    issues = []
    names = defaultdict(list)

    for f, rel in files:
        names[f.stem].append(rel)

    for stem, rels in names.items():
        if len(rels) > 1:
            issues.append((stem, rels))

    return issues


def check_empty_dirs(domain=None):
    """检查6：空目录"""
    issues = []
    target = VAULT_PATH / domain if domain else VAULT_PATH

    for d in target.rglob("*"):
        if d.is_dir() and should_skip(d):
            continue
        if d.is_dir():
            has_md = any(f.suffix == '.md' for f in d.iterdir() if f.is_file())
            if not has_md:
                issues.append(str(d.relative_to(VAULT_PATH)).replace('\\', '/'))

    return issues


def check_frontmatter(files):
    """检查7：frontmatter异常"""
    issues = []
    required_fields = ['tags', 'type']

    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            if not content.startswith('---'):
                issues.append((rel, '缺少frontmatter'))
                continue

            idx = content.find('---', 3)
            if idx < 0:
                issues.append((rel, 'frontmatter未闭合'))
                continue

            fm = content[3:idx]
            for field in required_fields:
                if field + ':' not in fm:
                    issues.append((rel, f'缺少字段: {field}'))
        except:
            issues.append((rel, '读取失败'))

    return issues


def check_large_files(files, threshold_kb=100):
    """检查8：大文件检测"""
    issues = []
    for f, rel in files:
        size_kb = f.stat().st_size / 1024
        if size_kb > threshold_kb:
            issues.append((rel, f'{size_kb:.1f}KB'))

    return issues


def check_stale_files(files, days=30):
    """检查9：过期文件"""
    issues = []
    cutoff = datetime.now().timestamp() - (days * 86400)

    for f, rel in files:
        mtime = f.stat().st_mtime
        if mtime < cutoff:
            days_old = int((datetime.now().timestamp() - mtime) / 86400)
            issues.append((rel, f'{days_old}天前'))

    return issues


def check_naming(files):
    """检查10：命名规范（非法字符/空格）"""
    issues = []
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']

    for f, rel in files:
        name = f.name
        if ' ' in name:
            issues.append((rel, '包含空格'))
        for ch in illegal_chars:
            if ch in name:
                issues.append((rel, f'包含非法字符: {ch}'))
                break

    return issues


def check_missing_images(files):
    """检查11：图片缺失"""
    issues = []
    il = re.compile(r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|svg))')

    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            for img in il.findall(content):
                img_path = f.parent / img[0]
                if not img_path.exists():
                    issues.append((rel, img[0]))
        except:
            pass

    return issues


def check_reference_stats(files):
    """检查12：引用统计"""
    ref_count = defaultdict(int)

    wl = re.compile(r'\[\[([^\]|#]+)')
    for f, rel in files:
        try:
            content = f.read_text(encoding='utf-8')
            for link in wl.findall(content):
                ref_count[link.strip()] += 1
        except:
            pass

    # 排序
    sorted_refs = sorted(ref_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_refs[:20]  # 返回TOP20


def run_all_checks(files, domain=None):
    """运行全部12项检查"""
    results = {}

    print("[Lint] 1/12 断裂链接...")
    results['broken_links'] = check_broken_links(files)

    print("[Lint] 2/12 死胡同页面...")
    results['dead_ends'] = check_dead_ends(files)

    print("[Lint] 3/12 孤立文件...")
    results['orphans'] = check_orphans(files)

    print("[Lint] 4/12 标签分布...")
    tag_count, tag_files = check_tags(files)
    results['tag_count'] = tag_count
    results['tag_files'] = tag_files

    print("[Lint] 5/12 重复文件...")
    results['duplicates'] = check_duplicates(files)

    print("[Lint] 6/12 空目录...")
    results['empty_dirs'] = check_empty_dirs(domain)

    print("[Lint] 7/12 frontmatter异常...")
    results['frontmatter'] = check_frontmatter(files)

    print("[Lint] 8/12 大文件检测...")
    results['large_files'] = check_large_files(files)

    print("[Lint] 9/12 过期文件...")
    results['stale_files'] = check_stale_files(files)

    print("[Lint] 10/12 命名规范...")
    results['naming'] = check_naming(files)

    print("[Lint] 11/12 图片缺失...")
    results['missing_images'] = check_missing_images(files)

    print("[Lint] 12/12 引用统计...")
    results['ref_stats'] = check_reference_stats(files)

    return results


def generate_report(results, domain=None, output_path=None):
    """生成检查报告"""
    lines = []
    lines.append('---')
    lines.append('tags: [自动化, Lint, 报告]')
    lines.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    lines.append('type: report')
    lines.append('---')
    lines.append('')
    lines.append('# 知识库Lint检查报告')
    lines.append('')

    if domain:
        lines.append(f'- 检查域: {domain}')
    else:
        lines.append('- 检查范围: 全库')

    total_issues = sum([
        len(results.get('broken_links', [])),
        len(results.get('dead_ends', [])),
        len(results.get('orphans', [])),
        len(results.get('duplicates', [])),
        len(results.get('empty_dirs', [])),
        len(results.get('frontmatter', [])),
        len(results.get('large_files', [])),
        len(results.get('stale_files', [])),
        len(results.get('naming', [])),
        len(results.get('missing_images', []))
    ])

    lines.append(f'- 总问题数: {total_issues}')
    lines.append(f'- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')

    # 1. 断裂链接
    lines.append('## 1. 断裂链接')
    lines.append('')
    if results.get('broken_links'):
        for src, tgt in results['broken_links'][:20]:
            lines.append(f'- [[{src}]] → {tgt}')
    else:
        lines.append('✅ 无断裂链接')
    lines.append('')

    # 2. 死胡同
    lines.append('## 2. 死胡同页面')
    lines.append('')
    if results.get('dead_ends'):
        for rel in results['dead_ends'][:20]:
            lines.append(f'- [[{rel}]]')
    else:
        lines.append('✅ 无死胡同页面')
    lines.append('')

    # 3. 孤立文件
    lines.append('## 3. 孤立文件')
    lines.append('')
    if results.get('orphans'):
        for rel in results['orphans'][:20]:
            lines.append(f'- [[{rel}]]')
    else:
        lines.append('✅ 无孤立文件')
    lines.append('')

    # 4. 标签分布
    lines.append('## 4. 标签分布')
    lines.append('')
    if results.get('tag_count'):
        for tag, cnt in sorted(results['tag_count'].items(), key=lambda x: x[1], reverse=True)[:20]:
            lines.append(f'- {tag}: {cnt}')
    else:
        lines.append('⚠️ 未检测到标签')
    lines.append('')

    # 5. 重复文件
    lines.append('## 5. 重复文件')
    lines.append('')
    if results.get('duplicates'):
        for stem, rels in results['duplicates'][:20]:
            lines.append(f'- {stem}: {", ".join(rels)}')
    else:
        lines.append('✅ 无重复文件')
    lines.append('')

    # 6. 空目录
    lines.append('## 6. 空目录')
    lines.append('')
    if results.get('empty_dirs'):
        for d in results['empty_dirs'][:20]:
            lines.append(f'- {d}')
    else:
        lines.append('✅ 无空目录')
    lines.append('')

    # 7. frontmatter异常
    lines.append('## 7. frontmatter异常')
    lines.append('')
    if results.get('frontmatter'):
        for rel, issue in results['frontmatter'][:20]:
            lines.append(f'- [[{rel}]]: {issue}')
    else:
        lines.append('✅ 无frontmatter异常')
    lines.append('')

    # 8. 大文件
    lines.append('## 8. 大文件')
    lines.append('')
    if results.get('large_files'):
        for rel, size in results['large_files'][:20]:
            lines.append(f'- [[{rel}]]: {size}')
    else:
        lines.append('✅ 无大文件')
    lines.append('')

    # 9. 过期文件
    lines.append('## 9. 过期文件')
    lines.append('')
    if results.get('stale_files'):
        for rel, days in results['stale_files'][:20]:
            lines.append(f'- [[{rel}]]: {days}')
    else:
        lines.append('✅ 无过期文件')
    lines.append('')

    # 10. 命名规范
    lines.append('## 10. 命名规范')
    lines.append('')
    if results.get('naming'):
        for rel, issue in results['naming'][:20]:
            lines.append(f'- [[{rel}]]: {issue}')
    else:
        lines.append('✅ 无命名问题')
    lines.append('')

    # 11. 图片缺失
    lines.append('## 11. 图片缺失')
    lines.append('')
    if results.get('missing_images'):
        for rel, img in results['missing_images'][:20]:
            lines.append(f'- [[{rel}]]: {img}')
    else:
        lines.append('✅ 无缺失图片')
    lines.append('')

    # 12. 引用统计
    lines.append('## 12. 引用统计 TOP20')
    lines.append('')
    if results.get('ref_stats'):
        for ref, cnt in results['ref_stats']:
            lines.append(f'- {ref}: {cnt}次')
    else:
        lines.append('⚠️ 未检测到引用')
    lines.append('')

    lines.append('---')
    lines.append('[[🏠 知识库首页]] | [[00-工作台/知识库健康度报告|健康度报告]]')
    lines.append('')

    content = '\n'.join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        print(f"[Lint] ✅ 报告已生成: {output_path}")

    return content


def main():
    import argparse
    parser = argparse.ArgumentParser(description='知识库域级Lint检查器')
    parser.add_argument('domain', nargs='?', help='指定域名称（如 01-造价核心），不指定则检查全库')
    parser.add_argument('--fix', action='store_true', help='自动修复（实验性）')
    args = parser.parse_args()

    print("[Lint] v1.0 启动...")

    files = collect_files(args.domain)
    if not files:
        return

    print(f"[Lint] 发现 {len(files)} 个文件，开始12项检查...")

    results = run_all_checks(files, args.domain)

    output_name = f'Lint检查报告_{args.domain or "全库"}.md'
    output_path = VAULT_PATH / "00-工作台" / output_name
    generate_report(results, args.domain, output_path)

    print(f"[Lint] DONE. 报告: {output_path}")


if __name__ == '__main__':
    main()
