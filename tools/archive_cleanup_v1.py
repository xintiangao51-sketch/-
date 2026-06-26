#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归档库清理 v1 — 删除明显冗余/无价值内容"""
import io
import sys
import os
import shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
ARCHIVE = VAULT / '99-归档库'

deleted = []
errors = []

def safe_delete(path, reason):
    """安全删除"""
    try:
        p = Path(path)
        if p.is_file():
            size = p.stat().st_size
            p.unlink()
            deleted.append(f'{reason}: {p.relative_to(VAULT)} ({size} bytes)')
        elif p.is_dir():
            # 先尝试删除空目录
            try:
                p.rmdir()
                deleted.append(f'{reason}: {p.relative_to(VAULT)}/ (empty dir)')
            except OSError:
                # 非空，使用 shutil
                size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
                shutil.rmtree(p)
                deleted.append(f'{reason}: {p.relative_to(VAULT)}/ ({size} bytes)')
    except Exception as e:
        errors.append(f'错误 {path}: {e}')

# === 1. 删除 S239线五彩湾 空目录（"副本"）===
p = ARCHIVE / '_09项目资料_杂项' / 'S239线五彩湾-吉木萨尔改扩建桥涵工程 - 副本'
if p.exists():
    safe_delete(p, 'S239空目录')

# === 2. 删除 _哈密综合能源集控服务中心_已合并（已合并到 09-项目资料）===
p = ARCHIVE / '_哈密综合能源集控服务中心_已合并'
if p.exists():
    # 已合并到 09-项目资料/哈密国源综合能源集控服务中心，可删除
    safe_delete(p, '已合并到09-项目资料')

# === 3. 删除 试运行项目-道班房四Agent协同闭环（仅1个md，属于历史测试）===
p = ARCHIVE / '试运行项目-道班房四Agent协同闭环'
if p.exists():
    safe_delete(p, '历史测试文件')

# === 4. 删除 _待分类文件_待人工分类（未分类文件，长期未处理）===
p = ARCHIVE / '_待分类文件_待人工分类'
if p.exists():
    safe_delete(p, '长期未分类文件')

# === 5. 删除 _crawl_output_archived（已归档的爬虫输出）===
p = ARCHIVE / '_crawl_output_archived'
if p.exists():
    safe_delete(p, '已归档的爬虫输出')

# === 6. 删除 89M _06参考文档_旧杂项（与当前参考文档重复）===
p = ARCHIVE / '_06参考文档_旧杂项'
if p.exists():
    safe_delete(p, '旧的参考文档杂项')

print('=' * 60)
print('已删除:')
for d in deleted:
    print(f'  ✅ {d}')
print()
if errors:
    print('错误:')
    for e in errors:
        print(f'  ❌ {e}')
print('=' * 60)
print(f'总计删除: {len(deleted)} 项')