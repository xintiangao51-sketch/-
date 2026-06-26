#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semantic_scan_tfidf.py — TF-IDF 版语义相似度扫描（零下载）

当 bge 模型下载失败时的替代方案。用 sklearn TfidfVectorizer
做字符级 n-gram 相似度扫描，精度略低于 bge-small-zh 但立即可用。

用法：
    python D:\知识库\.scripts\semantic_scan_tfidf.py
    python D:\知识库\.scripts\semantic_scan_tfidf.py --threshold 0.3
    python D:\知识库\.scripts\semantic_scan_tfidf.py --vault-root D:\知识库
"""

import os, re, sys, json
from collections import Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_VAULT = r'D:\知识库'
VAULT = DEFAULT_VAULT
THRESHOLD = 0.35  # TF-IDF 相似度普遍偏低，0.35 约等于 bge 的 0.75

# 解析参数
for i, arg in enumerate(sys.argv[1:]):
    if arg.startswith('--vault-root='):
        VAULT = arg.split('=', 1)[1]
    elif arg == '--vault-root' and i + 2 < len(sys.argv):
        VAULT = sys.argv[i + 2]
    elif arg.startswith('--threshold='):
        THRESHOLD = float(arg.split('=', 1)[1])
    elif arg == '--threshold' and i + 2 < len(sys.argv):
        THRESHOLD = float(sys.argv[i + 2])

KNOWLEDGE_DIRS = [
    '00-工作台', '01-造价核心', '02-业务中台', '03-合同与法务',
    '04-施工方案', '05-投标报价', '06-参考文档', '07-AI工具与技能',
    '08-参考规范', '10-索引与导航', '12-项目案例库', '14-标准模板', '98-原子知识库',
]


def find_files():
    files = []
    for d in KNOWLEDGE_DIRS:
        sd = os.path.join(VAULT, d)
        if not os.path.isdir(sd):
            continue
        for r, dn, fs in os.walk(sd):
            dn[:] = [x for x in dn if not x.startswith('.')]
            for f in fs:
                if not f.endswith('.md'):
                    continue
                fp = os.path.join(r, f)
                rel = os.path.relpath(fp, VAULT).replace('\\', '/')
                files.append((rel, fp))
    return files


def read_text(fp):
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            text = fh.read()
    except:
        return ''
    # 去 frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    # 去代码块
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # 去 wikilink (保留文本内容)
    text = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', text)
    return text.strip()


def main():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    files = find_files()
    print(f'🔍 TF-IDF 语义扫描 D:\\知识库')
    print(f'   Vault: {VAULT}')
    print(f'   扫描目录: {len(KNOWLEDGE_DIRS)} 个')
    print(f'   找到 .md 文件: {len(files)} 个')
    print(f'   阈值: {THRESHOLD}')
    print()

    # 读取内容
    paths, texts_raw = [], []
    for rel, fp in files:
        text = read_text(fp)
        if len(text) < 50:  # 过短页面跳过
            continue
        paths.append(rel)
        texts_raw.append(text)

    print(f'   有效页面: {len(paths)} 个（过滤掉长度<50字的页面）')
    print()

    # TF-IDF 向量化（字符 n-gram, 1-3 字）
    print('   正在计算 TF-IDF ...')
    vec = TfidfVectorizer(
        analyzer='char',          # 字符级 n-gram（中文不用分词）
        ngram_range=(1, 3),      # 1-3 字组合
        max_features=20000,       # 最多 20000 个特征
        min_df=2,                 # 至少在 2 个文档中出现
    )
    matrix = vec.fit_transform(texts_raw)
    print(f'   特征维度: {matrix.shape[1]}')
    print()

    # 成对计算相似度
    print('   计算相似度对 ...')
    n = len(paths)
    pairs = []
    batch_size = 100
    for i in range(n):
        sims = cosine_similarity(matrix[i], matrix).flatten()
        for j in range(i + 1, min(i + batch_size, n)):
            if j >= n:
                break
            sim = float(sims[j])
            if sim >= THRESHOLD:
                pairs.append((sim, paths[i], paths[j]))

    pairs.sort(key=lambda x: -x[0])

    # 输出结果
    print(f'\n{"="*70}')
    print(f'📊 未关联高相似度页面对 ({len(pairs)} pairs ≥ {THRESHOLD})')
    print(f'{"="*70}')

    for sim, p1, p2 in pairs[:40]:
        bar_len = int(sim * 30)
        bar = '█' * bar_len + '░' * (30 - bar_len)
        p1s = p1.replace('.md', '').split('/')[-1][:40]
        p2s = p2.replace('.md', '').split('/')[-1][:40]
        print(f'  {sim:.3f} {bar}  {p1s}  ↔  {p2s}')

    if len(pairs) > 40:
        print(f'\n  ... 共 {len(pairs)} 对')

    # 按目录分组统计
    print(f'\n{"="*70}')
    print(f'📂 按目录分组 Top')
    dir_pairs = Counter()
    for sim, p1, p2 in pairs:
        d1, d2 = p1.split('/')[0], p2.split('/')[0]
        if d1 == d2:
            dir_pairs[d1] += 1
        else:
            dir_pairs[f'{d1} ↔ {d2}'] += 1
    for d, c in dir_pairs.most_common(15):
        print(f'  {d:40s} {c:4d} 对')

    # 高级决策建议
    print(f'\n{"="*70}')
    print(f'💡 决策建议')
    print(f'{"="*70}')
    high = [p for p in pairs if p[0] >= 0.6]
    med = [p for p in pairs if 0.45 <= p[0] < 0.6]
    print(f'  🔴 ≥ 0.60（强烈建议合并/链接）: {len(high)} 对')
    print(f'  🟡 0.45-0.59（建议审查后决定）: {len(med)} 对')
    print(f'  🟢 {THRESHOLD}-0.44（备用信号，暂忽略）: {len(pairs)-len(high)-len(med)} 对')
    print()

    for sim, p1, p2 in high[:10]:
        fn1 = p1.replace('.md', '').split('/')[-1][:35]
        fn2 = p2.replace('.md', '').split('/')[-1][:35]
        print(f'  🔴 {sim:.3f}  {fn1}  ↔  {fn2}')

    print(f'\n✅ Done at {datetime.now().strftime("%H:%M")}')
    return pairs


if __name__ == '__main__':
    main()
