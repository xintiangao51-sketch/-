#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_tags.py — 批量补充 frontmatter tags（P0 第 1 项：335 个两轨皆无页面）

用法：
    python D:\知识库\.scripts\fix_tags.py                      # dry-run 预览
    python D:\知识库\.scripts\fix_tags.py --apply              # 正式运行
    python D:\知识库\.scripts\fix_tags.py --vault-root D:\知识库 # 指定 Vault

原理：
    基于路径 + 文件名关键词 + 正文首段关键词，为"两轨皆无"的 .md 文件
    推断并补充 frontmatter tags + type + created 字段。
    不修改已有 frontmatter tags 的文件。
"""

import os
import re
import sys
from datetime import date
from collections import Counter

# ========== 路径探测 ==========
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

KNOWLEDGE_DIRS = [
    '00-工作台', '01-造价核心', '02-业务中台', '03-合同与法务',
    '04-施工方案', '05-投标报价', '06-参考文档', '07-AI工具与技能',
    '08-参考规范', '10-索引与导航', '11-材料设备价格库', '12-项目案例库',
    '13-工程图纸', '14-标准模板', '15-数据资产', '16-运营数据',
    '17-知识库引擎', '98-原子知识库', '99-归档库',
]

# ── 推断规则 ──────────────────────────────────────

DIR_TAGS = {
    '00-工作台': ['索引', '工作台'],
    '01-造价核心': ['造价', '核心'],
    '02-业务中台': ['造价', '业务'],
    '03-合同与法务': ['合同/法务', '合同'],
    '04-施工方案': ['施工/方案', '施工'],
    '05-投标报价': ['投标', '报价'],
    '06-参考文档': ['参考'],
    '07-AI工具与技能': ['AI'],
    '08-参考规范': ['规范'],
    '09-项目资料': ['造价', '项目'],
    '10-索引与导航': ['索引'],
    '11-材料设备价格库': ['造价/材料', '材料'],
    '12-项目案例库': ['案例'],
    '13-工程图纸': ['图纸'],
    '14-标准模板': ['模板'],
    '15-数据资产': ['数据'],
    '16-运营数据': ['运营'],
    '17-知识库引擎': ['AI'],
    '98-原子知识库': ['参考'],
    '99-归档库': ['归档'],
}

DIR_TYPE = {
    '00-工作台': 'index', '01-造价核心': 'reference',
    '02-业务中台': 'reference', '03-合同与法务': 'reference',
    '04-施工方案': 'handbook', '05-投标报价': 'reference',
    '06-参考文档': 'reference', '07-AI工具与技能': 'reference',
    '08-参考规范': 'reference', '09-项目资料': 'reference',
    '10-索引与导航': 'index', '11-材料设备价格库': 'reference',
    '12-项目案例库': 'case', '13-工程图纸': 'reference',
    '14-标准模板': 'template', '15-数据资产': 'reference',
    '16-运营数据': 'reference', '17-知识库引擎': 'reference',
    '98-原子知识库': 'knowledge-card', '99-归档库': 'reference',
}

FILE_KEYWORDS = {
    '合同': '合同', '签证': '造价/变更', '变更': '造价/变更',
    '索赔': '造价/变更', '定额': '造价/定额', '清单': '造价/清单',
    '取费': '造价/取费', '费率': '造价/取费', '人工': '造价/人工',
    '材料': '造价/材料', '机械': '造价/机械', '图纸': '图纸',
    '规范': '规范', '国标': '规范', '案例': '案例', '模板': '模板',
    '结算': '造价/结算', '预算': '造价/预算', '投标': '投标',
    '报价': '投标', '招标': '投标', '施工': '施工/方案',
    '冬施': '施工/方案', '安全': '施工/安全', '进度': '施工/进度',
    '驾驶舱': '索引', '导航': '索引', '总索引': '索引', '速查': '索引',
    '看板': '索引', '入口': '索引', '总览': '索引', '参数': '参考',
    '信息价': '造价/材料', '价格': '造价/材料', '项目': '项目',
    'KC-': 'KC', 'GB': '规范', 'JGJ': '规范', '画像': '模板',
    'Log': '日志', '日志': '日志', '图纸': '图纸', '规范': '规范',
    '提示词': 'AI/文档', 'Skill': 'AI/文档', 'SKILL': 'AI/文档',
    '说明书': '参考', '工作手册': '参考', '手册': '参考',
}


def infer_tags(rel_path, file_text):
    """基于路径+文件名+正文首段推断 tags"""
    top = rel_path.split('/')[0]
    base = os.path.splitext(os.path.basename(rel_path))[0]

    tags = list(DIR_TAGS.get(top, ['参考']))

    # 文件名关键词
    for kw, tag in FILE_KEYWORDS.items():
        if kw in base or kw.lower() in base.lower():
            if tag not in tags:
                tags.append(tag)

    # 正文首段关键词
    body = re.sub(r'^---\n.*?\n---\n', '', file_text, count=1, flags=re.DOTALL)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    first = body.strip()[:500]
    for kw, tag in FILE_KEYWORDS.items():
        if kw in first:
            if tag not in tags:
                tags.append(tag)

    # 去重
    seen = set()
    deduped = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def has_tags(text):
    """检测是否有 frontmatter tags 字段"""
    m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return False
    return bool(re.search(r'^\s*tags:', m.group(1), re.MULTILINE))


def has_body_tags(text):
    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    return bool(re.findall(r'#([\w一-鿿_-]+)', body))


def has_frontmatter(text):
    return text.startswith('---')


def add_tags_to_file(file_path, inferred_tags):
    """为文件添加 frontmatter tags（若无 frontmatter 则新建）"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # 取 mtime 作为 created
    import time
    mtime = date.fromtimestamp(os.path.getmtime(file_path))
    created_str = mtime.isoformat()

    tags_yaml = '[' + ', '.join(f'"{t}"' for t in inferred_tags) + ']'

    if not has_frontmatter(text):
        # 无 frontmatter，新建
        new_text = f'---\ntags: {tags_yaml}\ncreated: {created_str}\ntype: reference\n---\n\n{text}'
    else:
        # 已有 frontmatter 但无 tags 字段，添加
        m = re.match(r'^(---\n)(.*?)(\n---)', text, re.DOTALL)
        if m:
            fm_head, fm_body, fm_tail = m.group(1), m.group(2), m.group(3)
            # 插入 tags 和 type
            new_fm = f'tags: {tags_yaml}\ncreated: {created_str}\ntype: reference\n' + fm_body
            new_text = fm_head + new_fm + fm_tail + text[m.end():]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)


# ========== MAIN ==========
def main():
    print(f'fix_tags.py — 批量补充 frontmatter tags')
    print(f'Vault: {VAULT}')
    mode = '🔍 DRY-RUN' if not APPLY else '✏️  APPLY'
    print(f'模式: {mode}')
    print(f'扫描目录: {len(KNOWLEDGE_DIRS)} 个')
    print()

    files_found = 0
    files_missing = []
    dir_stats = Counter()

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
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        text = fh.read()
                except:
                    continue
                files_found += 1
                rel = os.path.relpath(fp, VAULT).replace('\\', '/')

                hfm = has_tags(text)
                hbt = has_body_tags(text)

                if not hfm and not hbt:
                    inferred = infer_tags(rel, text)
                    files_missing.append((rel, inferred, fp))
                    top = rel.split('/')[0]
                    dir_stats[top] += 1

    print(f'扫描 .md 文件：{files_found}')
    print(f'两轨皆无：{len(files_missing)} ({100*len(files_missing)/files_found:.1f}%)')
    print()

    if not files_missing:
        print('✅ 无两轨皆无页面，任务完成')
        return

    print('=== 按目录分布 ===')
    for d, c in dir_stats.most_common():
        print(f'  {d:30s} {c:4d}')
    print()

    if APPLY:
        # 正式写文件
        ok = 0
        fail = 0
        for rel, inferred, fp in files_missing:
            try:
                add_tags_to_file(fp, inferred)
                ok += 1
            except Exception as e:
                print(f'  ❌ 失败: {rel} → {e}')
                fail += 1
        print(f'\n✅ 写入完成：成功 {ok} / 失败 {fail}')
    else:
        # dry-run：只预览前 30
        print(f'=== 预览（前 30 个，共 {len(files_missing)} 个）===\n')
        for rel, inferred, _ in files_missing[:30]:
            tag_str = ', '.join(inferred[:6])
            print(f'  {rel:70s} → [{tag_str}]')
        if len(files_missing) > 30:
            print(f'\n  ... 共 {len(files_missing)} 个')
        print()
        print('''
  Dry-run 完成。预览无误后执行：
    python D:\\知识库\\.scripts\\fix_tags.py --apply
''')


if __name__ == '__main__':
    main()
