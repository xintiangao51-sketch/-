#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semantic_scan_xj.py — 新疆造价知识库 语义相似度扫描（造价版）

【来源】克隆自 灵台项目 scripts/semantic_scan.py
【改造点】
    1. VAULT 路径自动探测（Windows D:\知识库 / bash sandbox）
    2. CACHE_DIR 改为 D:\知识库\.scripts\.cache\
    3. 删除 PYTHON_SEMANTIC 硬编码
    4. 增加 --vault-root 参数
    5. 支持造价知识库的多领域目录扫描
    6. bge-small-zh-v1.5 模型 + hf-mirror 镜像

依赖：
    pip install sentence-transformers numpy --break-system-packages

用法：
    python D:\知识库\.scripts\semantic_scan_xj.py                              # 全库扫描
    python D:\知识库\.scripts\semantic_scan_xj.py --threshold 0.7              # 自定义阈值
    python D:\知识库\.scripts\semantic_scan_xj.py --page "01-造价核心/定额"     # 单页扫描
    python D:\知识库\.scripts\semantic_scan_xj.py --new-page "01-造价核心/xxx" # Ingest 用，输出 JSON
    python D:\知识库\.scripts\semantic_scan_xj.py --vault-root D:\知识库        # 指定 Vault
"""

import os
import sys
import json
import argparse
import re
import numpy as np

# ========== 路径探测 ==========
DEFAULT_VAULT_WIN = r'D:\知识库'
DEFAULT_VAULT_BASH = '/sessions/elegant-sweet-heisenberg/mnt/知识库'


def detect_vault():
    if os.path.isdir(DEFAULT_VAULT_WIN):
        return DEFAULT_VAULT_WIN
    if os.path.isdir(DEFAULT_VAULT_BASH):
        return DEFAULT_VAULT_BASH
    return os.getcwd()


# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="新疆造价知识库 语义相似度扫描")
    parser.add_argument('--threshold', type=float, default=0.75, help='相似度阈值 (0-1)')
    parser.add_argument('--page', type=str, default=None, help='扫描特定页（人类可读）')
    parser.add_argument('--new-page', type=str, default=None, help='新页路径（Ingest，输出 JSON）')
    parser.add_argument('--json', action='store_true', help='JSON 输出模式')
    parser.add_argument('--vault-root', type=str, default=None, help='知识库根目录')
    return parser.parse_args()


ARGS = parse_args()

VAULT = ARGS.vault_root or detect_vault()

# 知识库多领域目录（仅扫描这些，不扫描 09-项目资料/11-价格 等数据层）
KNOWLEDGE_DIRS = [
    '00-工作台', '01-造价核心', '02-业务中台', '03-合同与法务',
    '04-施工方案', '05-投标报价', '06-参考文档', '07-AI工具与技能',
    '08-参考规范', '10-索引与导航', '12-项目案例库',
    '14-标准模板', '98-原子知识库',
]

THRESHOLD = ARGS.threshold
CACHE_DIR = os.path.join(VAULT, '.scripts', '.cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, 'embeddings_cache.json')


def find_md_files(root, dirs_to_scan=None):
    """扫描知识库的 .md 文件（排除 .obsidian/.git/原料层/价格库）"""
    files = []
    if dirs_to_scan is None:
        # 默认扫描所有 KNOWLEDGE_DIRS
        for d in dirs_to_scan or KNOWLEDGE_DIRS:
            sub = os.path.join(root, d)
            if os.path.isdir(sub):
                files.extend(_scan_dir(sub, root))
    else:
        for d in dirs_to_scan:
            sub = os.path.join(root, d)
            if os.path.isdir(sub):
                files.extend(_scan_dir(sub, root))
    return files


def _scan_dir(sub, root):
    files = []
    for dirpath, dirnames, filenames in os.walk(sub):
        # 排除隐藏目录
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for fn in filenames:
            if fn.endswith('.md') and not fn.startswith('.'):
                rel = os.path.relpath(os.path.join(dirpath, fn), root)
                files.append((rel, os.path.join(dirpath, fn)))
    return files


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def embed_texts(texts):
    """Embed texts using bge-small-zh-v1.5 (Chinese-optimized)"""
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
    except ImportError:
        print('❌ 缺少 sentence-transformers')
        print('   安装: pip install sentence-transformers --break-system-packages')
        sys.exit(1)

    emb = model.encode(texts, show_progress_bar=False)
    return emb.tolist()


def get_page_text(files, max_files=None):
    """Extract title + first 500 chars for embedding"""
    texts = []
    paths = []
    for i, (rel, abspath) in enumerate(files):
        if max_files and i >= max_files:
            break
        try:
            with open(abspath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue

        title = os.path.splitext(os.path.basename(rel))[0]
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                fm = content[3:end]
                for line in fm.split('\n'):
                    if line.strip().startswith('标题:'):
                        title = line.split(':', 1)[1].strip()
                        break

        clean = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', content)
        clean = re.sub(r'<img[^>]+>', '', clean)

        texts.append(f"{title}. {clean[:500]}")
        paths.append(rel)

    return texts, paths


def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def scan_all(threshold=THRESHOLD, page_filter=None):
    print(f"🔍 扫描 D:\知识库 知识层（threshold={threshold}）")
    print(f"   Vault: {VAULT}")
    print(f"   扫描目录: {', '.join(KNOWLEDGE_DIRS)}")

    files = find_md_files(VAULT, KNOWLEDGE_DIRS)
    print(f"   找到 {len(files)} 个 .md 文件")

    if page_filter:
        files = [(r, p) for r, p in files if page_filter in r]
        if not files:
            print(f"   未找到匹配 '{page_filter}' 的文件")
            return
        print(f"   过滤到 {len(files)} 个匹配文件")

    texts, paths = get_page_text(files)
    print(f"   准备嵌入 {len(texts)} 个页面...")

    cache = load_cache()
    uncached_texts = []
    uncached_indices = []
    for i, (text, path) in enumerate(zip(texts, paths)):
        if path not in cache:
            uncached_texts.append(text)
            uncached_indices.append(i)

    if uncached_texts:
        print(f"   新页面需嵌入: {len(uncached_texts)} 个")
        try:
            new_embs = embed_texts(uncached_texts)
        except Exception as e:
            print(f"   ❌ 嵌入失败: {e}")
            return
        for idx, emb in zip(uncached_indices, new_embs):
            cache[paths[idx]] = emb
        save_cache(cache)
        print(f"   已缓存到 {CACHE_FILE}")
    else:
        print(f"   全部 {len(texts)} 个页面已在缓存中")

    # Build embedding matrix
    embeddings = np.array([cache[p] for p in paths])
    n = len(paths)

    # Find existing links
    existing_links = set()
    for rel, abspath in files:
        try:
            with open(abspath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue
        for match in re.finditer(r'\[\[([^\]]+?)(?:\||\])', content):
            target = match.group(1).strip()
            existing_links.add((rel, target))

    # Scan
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_sim(embeddings[i], embeddings[j])
            if sim >= threshold:
                already_linked = False
                for a, b in [(paths[i], paths[j]), (paths[j], paths[i])]:
                    a_key = a.replace('\\', '/').replace('.md', '')
                    b_key = b.replace('\\', '/').replace('.md', '')
                    for (src, tgt) in existing_links:
                        src_norm = src.replace('\\', '/').replace('.md', '')
                        tgt_norm = tgt.replace('\\', '/').replace('.md', '')
                        if a_key == src_norm and b_key == tgt_norm:
                            already_linked = True
                            break
                    if already_linked:
                        break

                if not already_linked:
                    pairs.append((sim, paths[i], paths[j]))

    pairs.sort(key=lambda x: -x[0])

    print(f"\n{'='*70}")
    print(f"📊 未关联的高相似度页面对 ({len(pairs)} pairs ≥ {threshold})")
    print(f"{'='*70}")

    for sim, p1, p2 in pairs[:30]:
        p1_short = p1.replace('\\', '/').replace('.md', '')
        p2_short = p2.replace('\\', '/').replace('.md', '')
        bar_len = int(sim * 30)
        bar = '█' * bar_len + '░' * (30 - bar_len)
        print(f"  {sim:.3f} {bar}  {p1_short}  ↔  {p2_short}")

    if len(pairs) > 30:
        print(f"  ... 还有 {len(pairs) - 30} 对")

    print(f"\n✅ 总计 {len(pairs)} 对未关联高相似度页面")
    print(f"   建议：人工判断后用 [[wikilink]] 关联 → 形成知识图谱")
    return pairs


def scan_new_page(page_path, threshold=THRESHOLD):
    """Scan a single new page against the cached corpus. Returns JSON for Ingest."""
    page_path = page_path.replace('/', os.sep).replace('\\', os.sep)
    abs_path = os.path.join(VAULT, page_path)
    if not abs_path.endswith('.md'):
        abs_path += '.md'
    if not os.path.exists(abs_path):
        return json.dumps({"error": f"Page not found: {page_path}"}, ensure_ascii=False)

    with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    title = os.path.splitext(os.path.basename(page_path))[0]
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            fm = content[3:end]
            for line in fm.split('\n'):
                if line.strip().startswith('标题:'):
                    title = line.split(':', 1)[1].strip()
                    break

    clean = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', content)
    clean = re.sub(r'<img[^>]+>', '', clean)
    page_text = f"{title}. {clean[:500]}"

    cache = load_cache()
    if not cache:
        return json.dumps({"error": "缓存为空。请先运行全库扫描。"}, ensure_ascii=False)

    try:
        new_emb = embed_texts([page_text])[0]
    except Exception as e:
        return json.dumps({"error": f"嵌入失败: {e}"}, ensure_ascii=False)

    cache[page_path] = new_emb.tolist()
    save_cache(cache)

    pairs = []
    for cached_path, cached_emb in cache.items():
        if cached_path == page_path:
            continue
        sim = cosine_sim(new_emb, np.array(cached_emb))
        if sim >= threshold:
            already = False
            for match in re.finditer(r'\[\[([^\]]+?)(?:\||\])', content):
                target = match.group(1).strip()
                target_norm = target.replace('\\', '/')
                cached_norm = cached_path.replace('\\', '/')
                if cached_norm == target_norm or cached_norm.replace('.md', '') == target_norm:
                    already = True
                    break
            if not already:
                pairs.append({
                    "similarity": round(sim, 4),
                    "page": cached_path,
                    "display": cached_path.replace('\\', '/').replace('.md', '')
                })

    pairs.sort(key=lambda x: -x["similarity"])

    result = {
        "source": page_path,
        "source_display": page_path.replace('\\', '/').replace('.md', ''),
        "threshold": threshold,
        "pairs": pairs[:10],
        "total": len(pairs)
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    if ARGS.new_page:
        result = scan_new_page(ARGS.new_page, ARGS.threshold)
        print(result)
        return

    pairs = scan_all(threshold=ARGS.threshold, page_filter=ARGS.page)

    if ARGS.json and pairs:
        json_pairs = [
            {"similarity": round(s, 4), "page_a": p1.replace('\\', '/'), "page_b": p2.replace('\\', '/')}
            for s, p1, p2 in pairs
        ]
        print()
        print(json.dumps(
            {"total": len(json_pairs), "threshold": ARGS.threshold, "pairs": json_pairs[:30]},
            ensure_ascii=False, indent=2
        ))


if __name__ == '__main__':
    main()
