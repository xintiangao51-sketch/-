#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归档库清理 v2 — 删除已确认的冗余"""
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
    try:
        p = Path(path)
        if p.is_file():
            size = p.stat().st_size
            p.unlink()
            deleted.append(f'{reason}: {p.relative_to(VAULT)} ({size} bytes)')
        elif p.is_dir():
            try:
                p.rmdir()
                deleted.append(f'{reason}: {p.relative_to(VAULT)}/ (empty)')
            except OSError:
                size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
                shutil.rmtree(p)
                deleted.append(f'{reason}: {p.relative_to(VAULT)}/ ({size} bytes)')
    except Exception as e:
        errors.append(f'错误 {path}: {e}')

# === 1. 删除 _vault_pre_p1_20260621.tar.gz（139M 旧库快照）===
p = ARCHIVE / '_vault_pre_p1_20260621.tar.gz'
if p.exists():
    safe_delete(p, '旧库完整快照(P2前)')

# === 2. 删除 _工程造价知识库_README.md（重复）===
# 保留作为历史档案，跳过

# === 3. 删除 📚 知识库总索引_BACKUP_20260615.md（已被新总索引替代）===
p = ARCHIVE / '📚 知识库总索引_BACKUP_20260615.md'
if p.exists():
    safe_delete(p, '旧总索引备份')

# === 4. 删除 扩充总体规划_v2.md（早期规划文档，已被新方案替代）===
p = ARCHIVE / '扩充总体规划_v2.md'
if p.exists():
    safe_delete(p, '早期规划文档')

# === 5. _00-整理中枢 内的小文件清理 ===
# 保留主要的：审查报告、整理总览、参数核验表、沉淀报告、项目资料自动索引、配置脚本
# 一些超小文件可能是过程产物
small_files_to_check = [
    ('2026-06-15.md', 1891, '临时记录文件'),
    ('知识库整理规则.md', 681, '极小规则文件'),
    ('造价工作台上下文.md', 576, '极小上下文文件'),
    ('老高造价上下文记忆.md', 2669, '老上下文文件'),
]
for fname, expected_size, reason in small_files_to_check:
    p = ARCHIVE / '_00-整理中枢' / fname
    if p.exists() and p.stat().st_size == expected_size:
        # 检查是否被引用
        # 暂时保留（作为历史档案）
        pass

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

# 显示归档库当前总大小
total_size = sum(f.stat().st_size for f in ARCHIVE.rglob('*') if f.is_file())
print(f'归档库当前大小: {total_size / 1024 / 1024:.2f} MB')