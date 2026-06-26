#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""定额速查专用脚本"""
import sys
import os
import re
import time

ROOT = r"D:\知识库\08-参考规范\定额规范"
QUOTA_ROOT = r"D:\定额库\31、新疆定额全套\markdown版定额"

def search_quota_files(query):
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return []
    
    results = []
    
    # 搜索索引目录
    for cur, dirs, files in os.walk(ROOT):
        for fn in files:
            if not fn.lower().endswith(('.md', '.markdown')):
                continue
            full = os.path.join(cur, fn)
            try:
                with open(full, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            score = 0
            for t in tokens:
                cnt = content.lower().count(t)
                if cnt > 0:
                    score += cnt
            
            if score > 0:
                results.append({
                    'type': 'index',
                    'title': os.path.splitext(fn)[0],
                    'path': full,
                    'score': score
                })
    
    # 搜索源定额文件
    for cur, dirs, files in os.walk(QUOTA_ROOT):
        dirs[:] = [d for d in dirs if d not in ['.archive']]
        for fn in files:
            if not fn.lower().endswith(('.md', '.markdown')):
                continue
            full = os.path.join(cur, fn)
            try:
                with open(full, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            score = 0
            snippet = ""
            for t in tokens:
                cnt = content.lower().count(t)
                if cnt > 0:
                    score += cnt
                    idx = content.lower().find(t)
                    if idx >= 0:
                        start = max(0, idx - 50)
                        end = min(len(content), idx + 100)
                        snippet = content[start:end].replace('\n', ' ').strip()
            
            if score > 0:
                results.append({
                    'type': 'source',
                    'title': os.path.splitext(fn)[0],
                    'path': full,
                    'score': score,
                    'snippet': snippet[:150] if len(snippet) > 150 else snippet
                })
    
    results.sort(key=lambda x: -x['score'])
    return results[:20]

def main():
    query = ' '.join(sys.argv[1:]).strip()
    if not query:
        print('用法：python quota_search.py "查询词"')
        print('示例：python quota_search.py "土方工程"')
        sys.exit(1)
    
    print(f'\n🔍 定额速查: "{query}"\n')
    t0 = time.time()
    results = search_quota_files(query)
    elapsed = time.time() - t0
    
    print(f'找到 {len(results)} 条结果 ({elapsed:.2f}s)\n')
    print('=' * 60)
    
    for i, r in enumerate(results, 1):
        print(f'\n{i}. [{r["type"]}] {r["title"]}')
        print(f'   分数: {r["score"]}')
        if 'snippet' in r and r['snippet']:
            print(f'   片段: {r["snippet"][:80]}...')

if __name__ == '__main__':
    main()
