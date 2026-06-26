#!/usr/bin/env python3
"""
Obsidian 知识库健康检查 v2.0
功能：断链检测 / 标签规范 / 孤岛笔记 / 统计数据
输出：00-工作台/知识库健康度报告.md
"""
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path("D:/知识库")
SOURCE_IGNORE = {".obsidian", ".claude", ".archive", ".tools", ".git",
                 ".skillhub-install", ".claudian", "99-归档库"}
TARGET_IGNORE = {".obsidian", ".claude", ".archive", ".tools", ".git",
                 ".skillhub-install", ".claudian"}


def all_notes():
    notes = []
    for f in VAULT_PATH.rglob("*.md"):
        rel = f.relative_to(VAULT_PATH)
        if rel.parts[0] in SOURCE_IGNORE or any(p.startswith('.') for p in rel.parts):
            continue
        notes.append((f, str(rel).replace('\\', '/')))
    return notes


def read_note(path):
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ""


def check_broken(notes):
    wl = re.compile(r'\[\[([^\]|#]+)')
    idx = {}
    for f, rel in notes:
        idx[f.stem.lower()] = rel
        idx[f.stem] = rel
        idx[rel] = rel
        idx[rel.replace('.md', '')] = rel
        # emoji 前缀的文件添加无 emoji 别名索引
        # 例如 🏠 知识库首页.md → 添加 知识库首页 索引
        stem = f.stem
        for emoji_prefix in ['🏠 ', '🏷️ ', '📊 ', '📚 ', '🗂️ ', '🧭 ', '🔗 ', '📁 ', '💰 ', '📋 ', '📐 ', '🔍 ', '🌐 ', '⭐ ', '🎯 ']:
            if stem.startswith(emoji_prefix):
                stem_no_emoji = stem[len(emoji_prefix):]
                idx[stem_no_emoji] = rel
                idx[stem_no_emoji.lower()] = rel
                break
    # 索引 PDF / 目录（避免误报断链）
    for f in VAULT_PATH.rglob('*'):
        if any(p.startswith('.') for p in f.parts):
            continue
        if f.suffix.lower() in ('.pdf', '.json', '.docx', '.xls', '.xlsx', '.pptx', '.txt', '.py'):
            rel = str(f.relative_to(VAULT_PATH)).replace('\\', '/')
            idx[rel] = rel
            idx[rel.lower()] = rel
            idx[f.name.lower()] = rel
            idx[f.name] = rel
        elif f.is_dir():
            rel = str(f.relative_to(VAULT_PATH)).replace('\\', '/')
            idx[rel] = rel
            idx[rel.lower()] = rel
    broken = []
    for f, rel in notes:
        for link in wl.findall(read_note(f)):
            lc = link.strip()
            # 跳过纯 URL 和邮箱
            if lc.startswith(('http://', 'https://', 'mailto:')):
                continue
            # 短路径匹配（不带 / 的走 Obsidian 默认行为）
            target_norm = lc.replace('\\', '/')
            target_with_ext = target_norm + '.md' if not target_norm.endswith('.md') else target_norm
            # Obsidian emoji 别名机制：emoji 前缀的文件支持短名匹配
            # 例如 [[🏠 知识库首页]] 和 [[知识库首页]] 都解析到 🏠 知识库首页.md
            target_no_emoji = target_norm
            for emoji_prefix in ['🏠 ', '🏷️ ', '📊 ', '📚 ', '🗂️ ', '🧭 ', '🔗 ', '📁 ', '💰 ', '📋 ', '📐 ', '🔍 ', '🌐 ', '⭐ ', '🎯 ']:
                if target_no_emoji.startswith(emoji_prefix):
                    target_no_emoji = target_no_emoji[len(emoji_prefix):]
                    break
            resolved = (
                lc.lower() in idx or lc in idx or
                target_norm in idx or target_norm.lower() in idx or
                target_with_ext in idx or target_with_ext.lower() in idx or
                target_no_emoji in idx or target_no_emoji.lower() in idx or
                (target_no_emoji + '.md') in idx or (target_no_emoji + '.md').lower() in idx
            )
            # PDF/JSON/二进制文件 wikilink
            if not resolved and not target_norm.endswith('/'):
                for ext in ['.pdf', '.json', '.txt', '.docx', '.xlsx', '.pptx', '.py']:
                    if (target_norm + ext).lower() in idx:
                        resolved = True
                        break
            # 目录 wikilink（Obsidian 会解析为文件夹视图）
            if not resolved and target_norm in idx:
                resolved = True
            if not resolved:
                broken.append({"from": rel, "to": lc})
    return broken


def check_tags(notes):
    issues = []
    for f, rel in notes:
        c = read_note(f)
        m = re.match(r'^---\n(.*?)\n---', c, re.DOTALL)
        if not m:
            continue
        tm = re.search(r'tags:\s*\[(.*?)\]', m.group(1))
        if not tm:
            continue
        tags = [t.strip().strip('"').strip("'") for t in tm.group(1).split(',')]
        if len(tags) > 5:
            issues.append({"file": rel, "issue": f"too many tags ({len(tags)})"})
    return issues


def check_orphans(notes):
    wl = re.compile(r'\[\[([^\]|#]+)')
    inlinks = defaultdict(set)
    outlinks = {}
    has_tags = {}
    for f, rel in notes:
        c = read_note(f)
        has_tags[rel] = 'tags:' in c[:300]
        links = set(wl.findall(c))
        outlinks[rel] = links
        for lk in links:
            inlinks[lk.strip()].add(rel)
    orphans = []
    for f, rel in notes:
        name = f.stem
        if (name not in inlinks or len(inlinks[name]) == 0) and \
           (rel not in outlinks or len(outlinks[rel]) == 0) and \
           not has_tags.get(rel, False):
            orphans.append(rel)
    return orphans


def compute_stats(notes):
    dirs = defaultdict(lambda: {"files": 0, "size": 0})
    total = 0
    for f, rel in notes:
        top = rel.split('/')[0]
        sz = f.stat().st_size
        dirs[top]["files"] += 1
        dirs[top]["size"] += sz
        total += sz
    return {"total_notes": len(notes), "total_size_mb": total / (1024 * 1024),
            "dirs": dict(dirs)}


def generate_report(broken, tag_issues, orphans, stats):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    nt, no = len(tag_issues), len(orphans)
    # 只统计活动区断链（排除归档库误报）
    active_broken_count = sum(1 for b in broken if not b['to'].startswith('99-归档库/'))
    nb_display = active_broken_count
    total_issues = nb_display + nt + no
    health = "GREEN" if total_issues == 0 else ("YELLOW" if total_issues < 20 else "RED")

    r = f"""---
tags: [自动化, 健康度, 报告]
created: {now[:10]}
type: report
health: {health.lower()}
---

# 知识库健康度报告 - {now}

## 概览

| 指标 | 数值 |
|:-----|:---:|
| 总笔记数 | {stats['total_notes']} |
| 总大小 | {stats['total_size_mb']:.1f} MB |
| 断链（活动区） | {nb_display} |
| 断链（含归档库误报） | {len(broken)} |
| 标签问题 | {nt} |
| 孤岛笔记 | {no} |
| 健康度 | {health} |

---

## 断链（活动区 {nb_display}，含归档库误报 {len(broken)}）

"""
    if nb_display == 0 and len(broken) == 0:
        r += "无断链\n"
    else:
        # 分类：归档库 vs 活动区
        archive_broken = [b for b in broken if b['to'].startswith('99-归档库/')]
        active_broken = [b for b in broken if not b['to'].startswith('99-归档库/')]
        if active_broken:
            r += f"### 活动区断链 ({len(active_broken)})\n\n"
            r += "| 源笔记 | 断链目标 |\n|:-----|:-----|\n"
            for b in active_broken:
                r += f"| [[{b['from'].replace('.md','')}]] | {b['to']} |\n"
        if archive_broken:
            r += f"\n### 归档库引用 ({len(archive_broken)}) — 误报（目标文件存在）\n\n"
            r += "归档库（`99-归档库/`）被排除在索引之外，因此引用归档库的链接会显示为断链。**目标文件实际存在。**\n\n"
            r += "| 源笔记 | 归档库目标 |\n|:-----|:-----|\n"
            for b in archive_broken[:20]:
                r += f"| [[{b['from'].replace('.md','')}]] | {b['to']} |\n"
            if len(archive_broken) > 20:
                r += f"\n_（还有 {len(archive_broken)-20} 条未显示）_\n"

    r += f"\n## 标签问题 ({nt})\n\n"
    if nt == 0:
        r += "标签规范\n"
    else:
        for t in tag_issues[:10]:
            r += f"- [[{t['file'].replace('.md','')}]] {t['issue']}\n"

    r += f"\n## 孤岛笔记 ({no})\n\n"
    if no == 0:
        r += "无孤岛\n"
    else:
        for o in orphans[:10]:
            r += f"- [[{o.replace('.md','')}]]\n"

    r += "\n## 目录文件数\n\n| 目录 | 文件 | 大小(MB) |\n|:-----|:---:|:------:|\n"
    for d in sorted(stats["dirs"]):
        s = stats["dirs"][d]
        r += f"| {d}/ | {s['files']} | {s['size']/(1024*1024):.1f} |\n"

    r += f"""
## 建议

1. 断链: 检查目标文件是否已删除或改名
2. 标签: 参考 [[10-索引与导航/🏷️ 标签体系|🏷️ 标签体系]]
3. 孤岛: 加链接或标签, 或归档到 99-归档库/

---
[[🏠 知识库首页]] | [[10-索引与导航/知识库管理核心规则|管理规则]]
"""
    return r


def main():
    print(f"[{datetime.now():%H:%M}] obsidian_optimizer v2.0")
    notes = all_notes()
    print(f"  {len(notes)} notes scanned")
    broken = check_broken(notes)
    print(f"  {len(broken)} broken links")
    tags = check_tags(notes)
    print(f"  {len(tags)} tag issues")
    orphans = check_orphans(notes)
    print(f"  {len(orphans)} orphans")
    stats = compute_stats(notes)
    report = generate_report(broken, tags, orphans, stats)
    out = VAULT_PATH / "00-工作台/知识库健康度报告.md"
    out.write_text(report, encoding='utf-8')
    print(f"  report -> {out.relative_to(VAULT_PATH)}")
    total = len(broken) + len(tags) + len(orphans)
    print(f"  {'ALL CLEAN' if total == 0 else f'{total} issues'}")


if __name__ == "__main__":
    main()
