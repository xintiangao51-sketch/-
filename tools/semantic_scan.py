#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义相似度扫描器 v1.0
功能：使用 bge-small-zh 模型扫描知识库，找出语义重复的知识卡片
依赖：pip install sentence-transformers numpy
用法：python semantic_scan.py [--threshold 0.85] [--dry]
"""

import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np

VAULT_PATH = Path("D:/知识库")
OUTPUT_PATH = VAULT_PATH / "00-工作台/语义重复检测报告.md"
THRESHOLD_DEFAULT = 0.85

# 跳过的目录
SKIP_DIRS = {'.obsidian', '.claude', '.git', '.archive', '.tools', '.scripts',
             '99-归档库', '98-原子知识库', '__pycache__', '.ophistory'}


def should_skip(path):
    """判断是否跳过"""
    for p in path.parts:
        if p in SKIP_DIRS or p.startswith('.'):
            return True
    return False


def load_model():
    """加载语义模型"""
    try:
        from sentence_transformers import SentenceTransformer
        print("[语义扫描] 加载模型 bge-small-zh...")
        model = SentenceTransformer('BAAI/bge-small-zh')
        return model
    except ImportError:
        print("[语义扫描] ❌ 未安装 sentence-transformers")
        print("  请运行: pip install sentence-transformers")
        return None
    except Exception as e:
        print(f"[语义扫描] ❌ 模型加载失败: {e}")
        return None


def extract_text(file_path):
    """提取文件文本内容（取标题+前500字）"""
    try:
        text = file_path.read_text(encoding='utf-8')
        # 去掉 frontmatter
        if text.startswith('---'):
            idx = text.find('---', 3)
            if idx > 0:
                text = text[idx+3:]
        # 取前500字符
        return text[:500].strip()
    except:
        return ""


def compute_similarities(model, files):
    """计算文件间的语义相似度"""
    print(f"[语义扫描] 编码 {len(files)} 个文件...")

    texts = [extract_text(f) for f, _ in files]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    print("[语义扫描] 计算相似度矩阵...")
    sim_matrix = np.dot(embeddings, embeddings.T)

    return sim_matrix, files


def find_duplicates(sim_matrix, files, threshold):
    """找出相似度超过阈值的文件对"""
    results = []
    seen = set()

    for i in range(len(files)):
        for j in range(i+1, len(files)):
            score = sim_matrix[i][j]
            if score >= threshold:
                key = tuple(sorted([i, j]))
                if key not in seen:
                    seen.add(key)
                    results.append((score, files[i], files[j]))

    results.sort(reverse=True)
    return results


def generate_report(results, threshold, dry_run):
    """生成检测报告"""
    lines = []
    lines.append('---')
    lines.append(f'tags: [自动化, 语义扫描, 报告]')
    lines.append(f'created: {VAULT_PATH.stat().st_mtime if hasattr(VAULT_PATH, "stat") else "2026-06-27"}')
    lines.append(f'type: report')
    lines.append('---')
    lines.append('')
    lines.append('# 语义重复检测报告')
    lines.append('')
    lines.append(f'- 阈值: {threshold}')
    lines.append(f'- 检测对数: {len(results)}')
    lines.append(f'- 生成时间: {Path(__file__).stat().st_mtime}')
    lines.append('')

    if not results:
        lines.append('✅ 未发现语义重复内容。')
        lines.append('')
    else:
        lines.append('## 疑似重复内容')
        lines.append('')
        lines.append('| 相似度 | 文件A | 文件B |')
        lines.append('|:-----:|:-----|:-----|')

        for score, (f1, rel1), (f2, rel2) in results[:50]:  # 最多显示50条
            lines.append(f'| {score:.3f} | [[{rel1}]] | [[{rel2}]] |')

        lines.append('')

    lines.append('---')
    lines.append('[[🏠 知识库首页]] | [[00-工作台/知识库健康度报告|健康度报告]]')
    lines.append('')

    content = '\n'.join(lines)

    if not dry_run:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(content, encoding='utf-8')
        print(f"[语义扫描] ✅ 报告已生成: {OUTPUT_PATH}")
    else:
        print("[语义扫描] [DRY] 报告预览:")
        print(content[:500])

    return content


def main():
    parser = argparse.ArgumentParser(description='语义相似度扫描器')
    parser.add_argument('--threshold', type=float, default=THRESHOLD_DEFAULT,
                        help=f'相似度阈值 (默认 {THRESHOLD_DEFAULT})')
    parser.add_argument('--dry', action='store_true', help='预览模式，不写入文件')
    args = parser.parse_args()

    print("[语义扫描] v1.0 启动...")

    # 收集所有 md 文件
    files = []
    for f in VAULT_PATH.rglob("*.md"):
        rel = str(f.relative_to(VAULT_PATH)).replace('\\', '/')
        if should_skip(f.parent):
            continue
        files.append((f, rel))

    print(f"[语义扫描] 发现 {len(files)} 个文件")

    if len(files) < 2:
        print("[语义扫描] 文件数量不足，退出")
        return

    # 加载模型
    model = load_model()
    if model is None:
        return

    # 计算相似度
    sim_matrix, files = compute_similarities(model, files)

    # 找出重复
    results = find_duplicates(sim_matrix, files, args.threshold)

    print(f"[语义扫描] 发现 {len(results)} 对疑似重复内容")

    # 生成报告
    generate_report(results, args.threshold, args.dry)

    print(f"[语义扫描] DONE. 共 {len(results)} 对疑似重复。")


if __name__ == '__main__':
    main()
