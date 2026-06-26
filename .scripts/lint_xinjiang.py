#!/usr/bin/env python3
"""lint_xinjiang.py v4 — 新疆造价知识库 Quality Lint"""
import os, re, sys
from collections import Counter
from datetime import datetime, timedelta

# 路径自动探测
_VAULT_WIN = r'D:\知识库'
_VAULT_BASH = '/sessions/elegant-sweet-heisenberg/mnt/知识库'
VAULT = _VAULT_WIN if os.path.isdir(_VAULT_WIN) else (_VAULT_BASH if os.path.isdir(_VAULT_BASH) else os.getcwd())
for i, a in enumerate(sys.argv[1:]):
    if a.startswith('--vault-root='): VAULT = a.split('=', 1)[1]
    elif a == '--vault-root' and i + 2 < len(sys.argv): VAULT = sys.argv[i + 2]

DIRS = ['00-工作台','01-造价核心','02-业务中台','03-合同与法务','04-施工方案',
        '05-投标报价','06-参考文档','07-AI工具与技能','08-参考规范','09-项目资料',
        '10-索引与导航','11-材料设备价格库','12-项目案例库','13-工程图纸',
        '14-标准模板','15-数据资产','16-运营数据','17-知识库引擎','98-原子知识库']
INDEX_PATH = os.path.join(VAULT, '10-索引与导航', '知识库总索引.md')
LOG_PATH = os.path.join(VAULT, '00-工作台', '操作日志.md')
RAW_DIR = os.path.join(VAULT, '09-项目资料')
REL_ALL = []
REL_SET = set()

def scan():
    global REL_ALL, REL_SET
    REL_ALL, REL_SET = [], set()
    # 根目录
    if os.path.isdir(VAULT):
        for f in os.listdir(VAULT):
            if f.endswith('.md') and not f.startswith('.'):
                rp = f.replace('\\', '/')
                REL_ALL.append((rp, os.path.join(VAULT, f)))
                REL_SET.add(rp)
    # 知识层目录
    for sub in DIRS:
        d = os.path.join(VAULT, sub)
        if not os.path.isdir(d): continue
        for r, dn, fs in os.walk(d):
            dn[:] = [x for x in dn if not x.startswith('.')]
            for fn in fs:
                if not fn.endswith('.md') or fn.startswith('.'): continue
                ap = os.path.join(r, fn)
                rp = os.path.relpath(ap, VAULT).replace('\\', '/')
                REL_ALL.append((rp, ap))
                REL_SET.add(rp)

def read(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
    except: return ''

def wl(text):
    """提取[[...]]链接，去#锚点/别名/D:/http"""
    r = []
    for link in re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*)?\]\]', text):
        t = link.split('#')[0].split('|')[0].strip()
        if not t: continue
        if t.startswith('D:\\') or t.startswith('D:/') or t.startswith('http'): continue
        r.append(t)
    return r

def non_md(t):
    ext = t.split('/')[-1].split('\\')[-1]
    return ext.lower().endswith(('.pdf','.dwg','.xlsx','.xls','.docx','.doc','.png','.jpg','.zip','.rar','.json','.py','.sh','.ps1'))

def resolve(t):
    if non_md(t): return None
    key = t + '.md' if not t.endswith('.md') else t
    if key in REL_SET: return key
    for r in REL_SET:
        if r.endswith('/' + key) or r == key: return r
    return None

def get_body(text):
    b = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    b = re.sub(r'```.*?```', '', b, flags=re.DOTALL)
    return b

# === MAIN ===
def main():
    scan()
    n = len(REL_ALL)

    print('=' * 60)
    print(f'新疆造价知识库 Lint v4')
    print(f'文件数: {n}')
    print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('=' * 60)

    # [1] 缺口
    gaps = []
    for rel, ap in REL_ALL:
        for t in wl(get_body(read(ap))):
            if not resolve(t): gaps.append((rel, t))
    print()
    print(f'[1] 缺口: {len(gaps)}')
    for rel, t in gaps[:15]: print(f'  GAP {rel}: [[{t}]]')
    if len(gaps) > 15: print(f'  ... 共 {len(gaps)}')

    # [3] 索引缺口
    idx_gaps = []
    if os.path.isfile(INDEX_PATH):
        idx_links = set(wl(get_body(read(INDEX_PATH))))
        actual = set(r for r, _ in REL_ALL)
        for link in sorted(idx_links):
            if (link + '.md') not in actual: idx_gaps.append(f'索引引用缺失: [[{link}]]')
        for rel in sorted(actual):
            if rel.startswith('10-索引与导航/'): continue
            if rel.startswith('99-归档库/'): continue
            rn = rel[:-3] if rel.endswith('.md') else rel
            if rn not in idx_links and rel.count('/') <= 1: idx_gaps.append(f'顶层文件未入索引: {rel}')
    else: idx_gaps = ['索引文件不存在']
    print()
    print(f'[3] 索引缺口: {len(idx_gaps)}')
    for g in idx_gaps[:10]: print(f'  {g}')
    if len(idx_gaps) > 10: print(f'  ... 共 {len(idx_gaps)}')

    # [4] 死胡同 + [5] 孤立
    out_c, in_c = {}, Counter()
    for rel, ap in REL_ALL:
        links = wl(get_body(read(ap)))
        out_c[rel] = len(links)
        for t in links: in_c[t] += 1
    deadends = [r for r, _ in REL_ALL if out_c.get(r, 0) > 0 and in_c.get(r.replace('\\','/'), 0) == 0 and in_c.get(r[:-3], 0) == 0]
    isolated = [r for r, _ in REL_ALL if out_c.get(r, 0) == 0 and in_c.get(r.replace('\\','/'), 0) == 0 and in_c.get(r[:-3], 0) == 0]
    print()
    print(f'[4] 死胡同: {len(deadends)}')
    for d in deadends[:10]: print(f'  {d}')
    if len(deadends) > 10: print(f'  ... 共 {len(deadends)}')
    print()
    print(f'[5] 孤立: {len(isolated)}')
    for i in isolated[:10]: print(f'  {i}')
    if len(isolated) > 10: print(f'  ... 共 {len(isolated)}')

    # [6] 标签
    tags = Counter()
    for rel, ap in REL_ALL:
        for t in re.findall(r'#([\w一-鿿_-]+)', get_body(read(ap))):
            tags[t] += 1
    print()
    print(f'[6] 标签 Top15')
    for tag, c in tags.most_common(15):
        bar = '#' * min(c, 30)
        print(f'  #{tag:20s} {c:4d} {bar}')

    # [8] 时效
    stale = []
    for rel, ap in REL_ALL:
        text = read(ap)
        m = re.match(r'^---\n.*?\n---', text, re.DOTALL)
        if not m: continue
        if '时效: 有效' not in m.group(0): continue
        dt = re.search(r'日期:\s*(\d{4}-\d{2}-\d{2})', m.group(0))
        if dt:
            try:
                d = datetime.strptime(dt.group(1), '%Y-%m-%d')
                if d < datetime.now() - timedelta(days=90): stale.append(rel)
            except: pass
    print()
    print(f'[8] 时效过期: {len(stale)}')

    # [9] 推荐区
    ws, gs = [], []
    for rel, ap in REL_ALL:
        body = get_body(read(ap))
        m = re.search(r'^## 推荐阅读\n(.+?)(?:\n## |\n---|\Z)', body, re.MULTILINE|re.DOTALL)
        if not m: continue
        sec = m.group(1)
        links = re.findall(r'\[\[([^\]]+?)\]\]', sec)
        if len(links) > 6: ws.append(f'{rel}: 超上限({len(links)})')
        for line in sec.strip().split(chr(10)):
            lm = re.search(r'\[\[([^\]]+?)\]\]', line)
            if not lm: continue
            after = re.sub(r'\[\[.+?\]\]', '', line).strip()
            if not after or len(after) < 3: ws.append(f'{rel}: 缺说明→[[{lm.group(1)}]]')
    print()
    print(f'[9] 推荐区: W{len(ws)}')
    for w in ws[:10]: print(f'  WARN {w}')

    # [10] 日志
    lw = []
    if os.path.isfile(LOG_PATH):
        c = read(LOG_PATH)
        for d in re.findall(r'^# \d{4}-\d{2}-\d{2}', c, re.MULTILINE): lw.append(f'{d}: 日期用了h1')
    else: lw = ['日志文件不存在']
    print()
    print(f'[10] 日志: {len(lw)}')
    for w in lw: print(f'  WARN {w}')

    # [11] 原料
    rw = []
    if os.path.isdir(RAW_DIR):
        wh = {'处理状态','处理日期','来源链接','tags','created','type','title','date'}
        for r, dn, fs in os.walk(RAW_DIR):
            for fn in fs:
                if not fn.endswith('.md'): continue
                text = read(os.path.join(r, fn))
                m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
                if not m: continue
                for line in m.group(1).split(chr(10)):
                    if ':' in line:
                        k = line.split(':')[0].strip()
                        if k and k not in wh: rw.append(f'{fn}: 多余字段->{k}'); break
    print()
    print(f'[11] 原料FM: {len(rw)}')

    # [12] 链路
    rl = []
    if os.path.isdir(RAW_DIR):
        for r, dn, fs in os.walk(RAW_DIR):
            for fn in fs:
                if not fn.endswith('.md'): continue
                text = read(os.path.join(r, fn))
                if re.search(r'^处理状态:\s+已提炼', text, re.MULTILINE) and not re.search(r'-> \[\[', text):
                    rl.append(f'{fn}: 已提炼但缺wikilink')
    print()
    print(f'[12] 原料链路: {len(rl)}')

    # 汇总
    print()
    print('=' * 60)
    print(f'缺口{len(gaps)} | 死胡同{len(deadends)} | 孤立{len(isolated)} | 索引缺口{len(idx_gaps)} | 时效{len(stale)} | 推荐区W{len(ws)} | 日志{len(lw)} | 原料FM{len(rw)} | 链路{len(rl)}')
    print('=' * 60)

if __name__ == '__main__':
    main()
