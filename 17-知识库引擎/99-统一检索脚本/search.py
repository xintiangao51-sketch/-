#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一检索脚本 · Python 版（与 search.js 对齐）
用法： python search.py "查询词"
"""
import sys
import os
import json
import re
import time
import datetime
import threading
import urllib.request
import urllib.parse
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, 'config', 'engines.json'), 'r', encoding='utf-8'))
TIMEOUT = 8


def snippet(text, query, max_len=200):
    if not text:
        return ''
    lower = text.lower()
    tokens = [t for t in query.lower().split() if t]
    idx = -1
    for t in tokens:
        idx = lower.find(t)
        if idx >= 0:
            break
    if idx < 0:
        idx = 0
    start = max(0, idx - 60)
    s = (('…' if start > 0 else '') +
         re.sub(r'\s+', ' ', text[start:start + max_len]).strip() +
         ('…' if start + max_len < len(text) else ''))
    return s


def http(url, method='GET', headers=None, body=None, timeout=TIMEOUT):
    req = urllib.request.Request(url, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, data=data, timeout=timeout) as resp:
        return resp.status, resp.read().decode('utf-8', 'replace')


# ── 引擎 1: 本地 markdown ──────────────────────────────
def search_local_md(query, out):
    cfg = CFG['engines'].get('local_md', {})
    if not cfg.get('enabled'):
        out['local_md'] = {'skipped': '未启用', 'results': []}
        return
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        out['local_md'] = {'results': []}
        return
    excludes = set(cfg.get('exclude_dirs', []))
    hits = []
    root = cfg.get('root', 'D:\\知识库')
    try:
        for cur, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in excludes]
            for fn in files:
                if not fn.lower().endswith(('.md', '.markdown', '.txt')):
                    continue
                full = os.path.join(cur, fn)
                try:
                    with open(full, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                except Exception:
                    continue
                lower = content.lower()
                score = 0
                for t in tokens:
                    cnt = lower.count(t)
                    if cnt > 0:
                        score += cnt * (2 if len(t) > 4 else 1)
                if score > 0:
                    hits.append({
                        'engine': 'local_md',
                        'score': score,
                        'title': os.path.splitext(fn)[0],
                        'path': full,
                        'url': 'file:///' + full.replace('\\', '/'),
                        'snippet': snippet(content, query),
                    })
        hits.sort(key=lambda x: -x['score'])
        out['local_md'] = {'results': hits[:CFG['output']['top_per_engine']]}
    except Exception as e:
        out['local_md'] = {'error': str(e), 'results': []}


# ── 引擎 2: Khoj ───────────────────────────────────────
def search_khoj(query, out):
    cfg = CFG['engines'].get('khoj', {})
    if not cfg.get('enabled') or not cfg.get('url'):
        out['khoj'] = {'skipped': '未启用', 'results': []}
        return
    try:
        url = f"{cfg['url']}/api/search?q={urllib.parse.quote(query)}&t=markdown&n={CFG['output']['top_per_engine']}"
        h = {'Accept': 'application/json'}
        if cfg.get('api_key'):
            h['Authorization'] = f"Bearer {cfg['api_key']}"
        status, body = http(url, headers=h)
        if status != 200:
            out['khoj'] = {'error': f'HTTP {status}', 'results': []}
            return
        data = json.loads(body)
        items = data if isinstance(data, list) else data.get('results', data.get('entries', []))
        out['khoj'] = {'results': [{
            'engine': 'khoj',
            'score': it.get('score', it.get('relevance', 1)),
            'title': it.get('title') or (it.get('compiled', '').split('\n')[0][:80] or '(no title)'),
            'path': it.get('file', it.get('url', '')),
            'url': it.get('url', it.get('file', '')),
            'snippet': snippet(it.get('entry') or it.get('compiled') or it.get('snippet', ''), query),
        } for it in items[:CFG['output']['top_per_engine']]]}
    except Exception as e:
        out['khoj'] = {'error': str(e), 'results': []}


# ── 引擎 3: AnythingLLM ────────────────────────────────
def search_anythingllm(query, out):
    cfg = CFG['engines'].get('anythingllm', {})
    if not cfg.get('enabled') or not cfg.get('url') or not cfg.get('api_key'):
        out['anythingllm'] = {'skipped': '未配置 API key', 'results': []}
        return
    if not cfg.get('workspace'):
        out['anythingllm'] = {'skipped': '未配置 workspace', 'results': []}
        return
    try:
        url = f"{cfg['url']}/api/v1/workspace/{urllib.parse.quote(cfg['workspace'])}/chat"
        h = {'Authorization': f"Bearer {cfg['api_key']}"}
        status, body = http(url, method='POST', headers=h, body={
            'message': f'请检索与"{query}"相关的文档片段，只列出引用片段，不要总结。',
            'mode': 'query',
        }, timeout=TIMEOUT * 2)
        if status != 200:
            out['anythingllm'] = {'error': f'HTTP {status}', 'results': []}
            return
        data = json.loads(body)
        sources = data.get('sources', [])
        out['anythingllm'] = {'results': [{
            'engine': 'anythingllm',
            'score': s.get('score', 0.5),
            'title': s.get('title') or s.get('docname', '(no title)'),
            'path': s.get('url', ''),
            'url': s.get('url', ''),
            'snippet': snippet(s.get('text') or s.get('chunk', ''), query),
        } for s in sources[:CFG['output']['top_per_engine']]]}
    except Exception as e:
        out['anythingllm'] = {'error': str(e), 'results': []}


# ── 引擎 4: RAGFlow ────────────────────────────────────
def search_ragflow(query, out):
    cfg = CFG['engines'].get('ragflow', {})
    if not cfg.get('enabled') or not cfg.get('url') or not cfg.get('api_key'):
        out['ragflow'] = {'skipped': '未配置', 'results': []}
        return
    try:
        url = f"{cfg['url']}/api/v1/retrieval"
        h = {'Authorization': f"Bearer {cfg['api_key']}"}
        payload = {'question': query, 'top_k': CFG['output']['top_per_engine']}
        if cfg.get('kb_id'):
            payload['kb_id'] = cfg['kb_id']
        status, body = http(url, method='POST', headers=h, body=payload)
        if status != 200:
            out['ragflow'] = {'error': f'HTTP {status}', 'results': []}
            return
        data = json.loads(body)
        chunks = data.get('data', {}).get('chunks') or data.get('chunks', [])
        out['ragflow'] = {'results': [{
            'engine': 'ragflow',
            'score': c.get('similarity', c.get('score', 0.5)),
            'title': c.get('docnm_kwd', c.get('document_name', '(no title)')),
            'path': c.get('docnm_kwd', ''),
            'url': '',
            'snippet': snippet(c.get('content_with_weight') or c.get('content', ''), query),
        } for c in chunks[:CFG['output']['top_per_engine']]]}
    except Exception as e:
        out['ragflow'] = {'error': str(e), 'results': []}


# ── 主流程 ─────────────────────────────────────────────
def main():
    query = ' '.join(sys.argv[1:]).strip()
    if not query:
        print('用法： python search.py "查询词"')
        sys.exit(1)

    print(f'\n🔍 查询: "{query}"\n')
    t0 = time.time()

    out = {}
    threads = [
        threading.Thread(target=search_local_md, args=(query, out)),
        threading.Thread(target=search_khoj, args=(query, out)),
        threading.Thread(target=search_anythingllm, args=(query, out)),
        threading.Thread(target=search_ragflow, args=(query, out)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=TIMEOUT * 3)

    elapsed = time.time() - t0
    md = [f'# 检索报告\n', f'- **查询**: `{query}`',
          f'- **时间**: {datetime.datetime.now().isoformat()}',
          f'- **耗时**: {elapsed:.2f}s\n\n---\n']

    for name in ['local_md', 'khoj', 'anythingllm', 'ragflow']:
        rep = out.get(name, {})
        label = f'[{name}]'.ljust(15)
        if rep.get('skipped'):
            print(f'{label} ⏭  跳过：{rep["skipped"]}')
            md.append(f'\n## ⏭ {name} — 跳过：{rep["skipped"]}\n')
            continue
        if rep.get('error'):
            print(f'{label} ❌ 失败：{rep["error"]}')
            md.append(f'\n## ❌ {name} — 失败：{rep["error"]}\n')
            continue
        results = rep.get('results', [])
        print(f'{label} ✅ {len(results)} 条')
        md.append(f'\n## ✅ {name} — {len(results)} 条\n')
        if not results:
            md.append('\n_无结果_\n')
            continue
        for i, r in enumerate(results, 1):
            sc = r['score']
            sc_s = f'{sc:.2f}' if isinstance(sc, float) else str(sc)
            print(f'  {i}. [{sc_s}] {r["title"]}')
            print(f'     📄 {r.get("path") or r.get("url")}')
            print(f'     {r["snippet"][:120]}...')
            md.append(f'\n### {i}. {r["title"]}')
            md.append(f'- 相关度: {sc_s}')
            md.append(f'- 路径: `{r.get("path") or r.get("url")}`')
            md.append(f'- 片段:\n\n  > {r["snippet"]}\n')

    if CFG['output'].get('save_md'):
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        safe_q = re.sub(r'[^\w\u4e00-\u9fa5]+', '_', query)[:40]
        out_dir = CFG['output']['dir']
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f'{ts}_{safe_q}.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))
        print(f'\n💾 报告: {out_path}')

    print(f'\n⏱  共 {elapsed:.2f}s\n')


if __name__ == '__main__':
    main()
