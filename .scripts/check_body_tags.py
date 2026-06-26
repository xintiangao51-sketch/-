#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_body_tags.py — 正文 #主标签 合规检查（P1-4 渗透率提升）

作用：
    1. 扫描所有知识层 .md 文件，检查正文第一段是否包含 #主标签
    2. 输出缺失清单 + 推断建议标签
    3. 可 dry-run 预览，--apply 才写

用法：
    python D:\知识库\.scripts\check_body_tags.py               # dry-run 预览
    python D:\知识库\.scripts\check_body_tags.py --apply        # 正式写入正文第一行 #标签
    python D:\知识库\.scripts\check_body_tags.py --list         # 只输出清单
"""

import os, re, sys
from collections import Counter

DEFAULT_VAULT_WIN = r'D:\知识库'
DEFAULT_VAULT_BASH = '/sessions/elegant-sweet-heisenberg/mnt/知识库'

def detect_vault():
    if len(sys.argv) > 2 and sys.argv[1] == '--vault-root':
        return sys.argv[2]
    if os.path.isdir(DEFAULT_VAULT_WIN):
        return DEFAULT_VAULT_WIN
    if os.path.isdir(DEFAULT_VAULT_BASH):
        return DEFAULT_VAULT_BASH
    return os.getcwd()

VAULT = detect_vault()
APPLY = '--apply' in sys.argv
LIST_ONLY = '--list' in sys.argv

KNOWLEDGE_DIRS = ['00-工作台','01-造价核心','02-业务中台','03-合同与法务',
                  '04-施工方案','05-投标报价','06-参考文档','07-AI工具与技能',
                  '08-参考规范','10-索引与导航','11-材料设备价格库','12-项目案例库',
                  '14-标准模板','98-原子知识库']

def infer_body_tag(rel, text):
    """从路径/FM tags/文件名推断合适的正文 #主标签"""
    base = os.path.basename(rel).replace('.md', '')

    # 1. 从 frontmatter tags 推断
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    fm_tags = []
    if m:
        for line in m.group(1).split('\n'):
            mm = re.match(r'^\s*tags:\s*\[(.+)\]', line)
            if mm:
                fm_tags = [t.strip().strip('"\'') for t in mm.group(1).split(',') if t.strip()]
                break

    fm_to_body = {
        '造价/变更': '签证', '造价/定额': '定额', '造价/清单': '清单',
        '造价/取费': '取费', '造价/材料': '材料', '造价/结算': '结算',
        '合同/法务': '合同', '施工/方案': '施工方案', '施工/安全': '安全',
        '投标': '投标', '规范': '规范', '案例': '案例', '模板': '模板',
    }
    for fm_t in fm_tags:
        for k, v in fm_to_body.items():
            if k in fm_t:
                return v
        if 'AI' in fm_t:
            return 'AI'
        if 'KC' in fm_t or 'KC-' in fm_t:
            return 'KC'
        if '索引' in fm_t:
            return '索引'

    # 2. 从文件名推断
    kw_map = {
        '合同': '合同', '签证': '签证', '变更': '签证', '索赔': '签证',
        '定额': '定额', '清单': '清单', '取费': '取费', '材料': '材料',
        '机械': '机械', '图纸': '图纸', '规范': '规范', '国标': '规范',
        '案例': '案例', '模板': '模板', '结算': '结算', '投标': '投标',
        '报价': '投标', '施工': '施工方案', '冬施': '施工方案',
        '驾驶舱': '索引', '导航': '索引', '总索引': '索引', '速查': '参考',
        '看板': '索引', '入口': '索引', '总览': '索引', '参数': '参考',
        '信息价': '材料', '价格': '材料', '日志': '索引',
        'KC-': 'KC', 'GB': '规范', 'JGJ': '规范', '提示词': 'AI',
        'SKILL': 'AI', 'Skill': 'AI', '说明': '参考',
    }
    for kw, tag in kw_map.items():
        if kw in base:
            return tag

    return '参考'


def has_body_tags_on_first_line(text):
    """检查正文第一段是否有 #主标签"""
    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    first = body.strip()
    if not first:
        return False
    first_line = first.split('\n')[0]
    return bool(re.findall(r'#([a-zA-Z一-鿿][\w一-鿿_-]*)', first_line))


def add_body_tag(fp, tag):
    """在正文第一段末尾追加 #标签"""
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # 找到正文开始位置
    body_start = 0
    m = re.match(r'^---\n.*?\n---\n', text, re.DOTALL)
    if m:
        body_start = m.end()

    if body_start == 0:
        # 无 frontmatter
        body_start = 0

    before = text[:body_start]
    after = text[body_start:]

    # 找到正文第一行尾
    first_newline = after.find('\n')
    first_line = after[:first_newline] if first_newline > 0 else after

    # 在第一行末尾追加 #标签
    new_first = first_line.rstrip() + f' 相关标签：#{tag}'
    new_after = new_first + after[first_newline:] if first_newline > 0 else new_first

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(before + new_after)


def main():
    print(f'正文 #主标签 合规检查')
    print(f'Vault: {VAULT}')
    mode = '🔍 DRY-RUN' if not APPLY else '✏️  APPLY'
    print(f'模式: {mode}')
    print()

    missing = []
    total = 0

    for d in KNOWLEDGE_DIRS:
        sd = os.path.join(VAULT, d)
        if not os.path.isdir(sd): continue
        for r, dn, fs in os.walk(sd):
            dn[:] = [x for x in dn if not x.startswith('.')]
            for f in fs:
                if not f.endswith('.md'): continue
                fp = os.path.join(r, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        text = fh.read()
                except:
                    continue
                total += 1
                rel = os.path.relpath(fp, VAULT).replace('\\', '/')

                if not has_body_tags_on_first_line(text):
                    inferred = infer_body_tag(rel, text)
                    missing.append((rel, inferred, fp))

    has_pct = 100 * (total - len(missing)) / total if total > 0 else 0
    print(f'扫描：{total} 个文件')
    print(f'已有正文 #主标签：{total - len(missing)} ({has_pct:.1f}%)')
    print(f'缺失正文 #主标签：{len(missing)} ({100 - has_pct:.1f}%)')
    print()

    # 按目录分布
    dir_cnt = Counter(r.split('/')[0] for r, _, _ in missing)
    print('=== 按目录分布 ===')
    for d, c in dir_cnt.most_common():
        print(f'  {d:30s} {c:4d}')
    print()

    if LIST_ONLY:
        print('=== 全量清单（供手动检查）===')
        for rel, inferred, _ in missing:
            print(f'{rel}')
        return

    print(f'=== 前 30 个示例（推断标签）===')
    for rel, inferred, _ in missing[:30]:
        print(f'  {rel:65s} → #{inferred}')
    print(f'\n  ... 共 {len(missing)} 个')

    if APPLY:
        ok = 0
        for rel, inferred, fp in missing:
            try:
                add_body_tag(fp, inferred)
                ok += 1
            except:
                pass
        print(f'\n✅ 写入完成：{ok} / {len(missing)}')
        print('⚠ 注意：正文标签是语义标签，自动推断可能不准确，建议人工抽查。')
    else:
        print(f'\n  Dry-run 完成。运行 --apply 以写入。')
        print(f'  ⚠ 正文标签需要语义判断，自动推断可能不准确，建议先抽查 20 个样本。')


if __name__ == '__main__':
    main()
