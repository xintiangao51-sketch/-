#!/usr/bin/env python3
"""
自动知识卡片生成器 v2.0 — 从笔记内容中提取结构化知识卡片
- 检测精华标签 / frontmatter type=knowledge-card / 经验总结标题
- 自动分配 KC 编号（按领域分段，避免撞号）
- 提取笔记中的第一段结论作为卡片摘要
用法: python auto_kc_generator.py [--dry] [max_cards]
"""
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path("D:/知识库")
KC_OUTPUT_DIR = VAULT_PATH / "10-索引与导航"

# ---- 领域 -> 编号段（每个领域独立段） ----
DOMAIN_SLOTS = {
    "造价/定额":      (100, 129),
    "造价/清单":      (130, 159),
    "造价/工程量":    (160, 189),
    "造价/组价":      (190, 219),
    "造价/取费":      (220, 249),
    "造价/人工":      (250, 279),
    "造价/材料":      (280, 309),
    "造价/机械":      (310, 339),
    "造价/结算":      (340, 369),
    "造价/变更":      (370, 399),
    "合同/法务":      (400, 449),
    "合同/模板":      (450, 479),
    "施工/安全":      (500, 529),
    "施工/施组":      (530, 559),
    "施工/方案":      (560, 599),
    "投标/策略":      (600, 649),
    "投标/分析":      (650, 699),
    "案例复盘":       (700, 749),
    "方法论":         (900, 949),
}

DEFAULT_SLOT = (950, 999)

# ---- 关键词 -> 领域映射 ----
KEYWORD_DOMAIN = {
    "定额": "造价/定额", "消耗量定额": "造价/定额", "定额子目": "造价/定额",
    "清单": "造价/清单", "清单计价": "造价/清单", "GB50500": "造价/清单",
    "工程量": "造价/工程量", "计算规则": "造价/工程量", "BOQ": "造价/工程量",
    "综合单价": "造价/组价", "组价": "造价/组价",
    "取费": "造价/取费", "管理费": "造价/取费", "利润": "造价/取费",
    "规费": "造价/取费", "税金": "造价/取费", "增值税": "造价/取费",
    "人工单价": "造价/人工", "人工费": "造价/人工", "劳务分包": "造价/人工",
    "信息价": "造价/材料", "材料价格": "造价/材料", "钢筋": "造价/材料",
    "混凝土": "造价/材料",
    "机械台班": "造价/机械", "机械费": "造价/机械",
    "结算": "造价/结算", "竣工结算": "造价/结算",
    "变更": "造价/变更", "签证": "造价/变更", "索赔": "造价/变更",
    "合同": "合同/法务", "FIDIC": "合同/法务",
    "法律": "合同/法务", "法规": "合同/法务",
    "安全": "施工/安全", "红线": "施工/安全",
    "施工组织": "施工/施组", "施组": "施工/施组",
    "施工方案": "施工/方案", "专项方案": "施工/方案",
    "投标": "投标/策略", "报价策略": "投标/策略",
    "不平衡报价": "投标/策略",
    "评标": "投标/分析", "招标分析": "投标/分析",
    "案例": "案例复盘", "复盘": "案例复盘",
}


def existing_kc_numbers():
    """扫描全库已分配的 KC 编号"""
    nums = {}
    for f in VAULT_PATH.rglob("KC-*.md"):
        m = re.search(r'KC-(\d{3})', f.name)
        if m:
            nums[int(m.group(1))] = str(f.relative_to(VAULT_PATH))
    return nums


def classify_domain(content, tags):
    """根据内容 + frontmatter tags 判断主领域"""
    scores = defaultdict(int)
    for kw, domain in KEYWORD_DOMAIN.items():
        if kw in content:
            scores[domain] += 1
    for tag in tags:
        if tag in DOMAIN_SLOTS:
            scores[tag] += 3
    if not scores:
        return None
    return max(scores, key=scores.get)


def assign_kc_number(domain, existing):
    """分配下一个可用编号"""
    lo, hi = DOMAIN_SLOTS.get(domain, DEFAULT_SLOT)
    for n in range(lo, hi + 1):
        if n not in existing:
            return n
    lo, hi = DEFAULT_SLOT
    for n in range(lo, hi + 1):
        if n not in existing:
            return n
    return None


def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        kv = re.match(r'(\w+):\s*(.+)', line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm


def extract_first_conclusion(content, max_chars=300):
    """从笔记中提取第一段实质性结论"""
    lines = content.split('\n')
    captured = []
    started = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('>') or stripped.startswith('---'):
            if captured:
                break
            continue
        if stripped.startswith('[') and ']:' in stripped:
            continue
        if not stripped:
            if captured:
                break
            continue
        if len(stripped) > 10:
            started = True
            captured.append(stripped)
        if started and sum(len(c) for c in captured) > max_chars:
            break
    return ' '.join(captured) if captured else "..."

def scan_candidates():
    """扫描候选笔记"""
    candidates = []
    scan_dirs = ["01-造价核心", "03-合同与法务", "04-施工方案",
                 "05-投标报价", "09-项目资料"]

    for d in scan_dirs:
        full = VAULT_PATH / d
        if not full.exists():
            continue
        for f in full.rglob("*.md"):
            if "99-归档库" in str(f) or f.name.startswith("KC-"):
                continue
            if f.stat().st_size < 200:
                continue
            try:
                content = f.read_text(encoding='utf-8')
            except Exception:
                continue

            fm = extract_frontmatter(content)
            tags_raw = fm.get('tags', '')
            if isinstance(tags_raw, str):
                tags = [t.strip().strip('"').strip("'")
                        for t in tags_raw.strip('[]').split(',')]
            else:
                tags = []

            is_essence = "精华" in tags or any(
                kw in f.stem for kw in ["经验", "策略", "指南", "方法", "总结"]
            )
            is_knowledge = fm.get('type') == 'knowledge-card'

            if is_essence or is_knowledge:
                domain = classify_domain(
                    content[:2000], [t for t in tags if t in DOMAIN_SLOTS]
                )
                candidates.append({
                    "file": str(f.relative_to(VAULT_PATH)),
                    "title": f.stem,
                    "tags": tags,
                    "domain": domain,
                    "size": f.stat().st_size,
                })

    return candidates


def generate_card(candidate, existing, dry_run=False):
    """生成知识卡片"""
    source = candidate["file"]
    domain = candidate["domain"]
    if not domain:
        return None

    num = assign_kc_number(domain, existing)
    if not num:
        return None

    full_path = VAULT_PATH / source
    content = full_path.read_text(encoding='utf-8')
    conclusion = extract_first_conclusion(content)

    tags_out = [domain, "KC"]
    if "精华" in candidate.get("tags", []):
        tags_out.append("精华")

    card = f"""---
tags: {json.dumps(tags_out, ensure_ascii=False)}
created: {datetime.now().strftime('%Y-%m-%d')}
source: {source}
status:
type: knowledge-card
---

# KC-{num:03d}: {candidate['title']}

>  自动提取 - 来源：[[{source.replace('.md', '')}]]

## 问题场景
待人工补充

## 核心结论
{conclusion}

## 依据/来源
- [[{source.replace('.md', '')}]]

## 实操指引
待人工补充

---

[[知识库首页]] | [[10-索引与导航/知识库总索引|KC注册表]]
"""
    if dry_run:
        return {"num": num, "domain": domain, "source": source,
                "preview": conclusion[:80]}

    filename = f"KC-{num:03d}_{candidate['title']}.md"
    filepath = KC_OUTPUT_DIR / filename
    filepath.write_text(card, encoding='utf-8')
    existing[num] = str(filepath.relative_to(VAULT_PATH))

    return {"num": num, "domain": domain, "source": source,
            "path": str(filepath.relative_to(VAULT_PATH))}


def main(dry_run=False, max_cards=5):
    print(f"[{datetime.now():%H:%M:%S}] auto_kc_generator v2.0")
    existing = existing_kc_numbers()
    print(f"  existing KC: {len(existing)}")

    candidates = scan_candidates()
    print(f"  candidates: {len(candidates)}")

    results = []
    for c in candidates[:max_cards]:
        if not c["domain"]:
            print(f"  SKIP {c['title']} (no domain)")
            continue
        try:
            r = generate_card(c, existing, dry_run=dry_run)
            if r:
                results.append(r)
                tag = "DRY" if dry_run else "OK"
                print(f"  [{tag}] KC-{r['num']:03d} [{r['domain']}] <- {c['title']}")
        except Exception as e:
            print(f"  ERR {c['title']}: {e}")

    print(f"\n{'DRY RUN' if dry_run else 'DONE'}: {len(results)} cards")
    return results


if __name__ == "__main__":
    import sys
    dry = "--dry" in sys.argv
    limit = 5
    for a in sys.argv[1:]:
        if a.isdigit():
            limit = int(a)
            break
    main(dry_run=dry, max_cards=limit)
