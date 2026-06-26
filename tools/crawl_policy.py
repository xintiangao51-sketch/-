#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全网工程造价知识爬取 + 基础知识卡片生成 v2.0
来源：造价行业基础知识关键词 -> 自动生成 KC-BASIC 卡片
用法：python crawl_policy.py [--dry]
"""
import re
import sys
import json
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path("D:/知识库")
KC_DIR = VAULT_PATH / "10-索引与导航"
POLICY_DIR = VAULT_PATH / "08-参考规范"

# ====== 造价行业核心关键词（9类，每类2-5个核心词）======
BASIC_KEYWORDS = {
    "定额": ["消耗量定额", "预算定额", "单位估价表", "定额子目"],
    "清单": ["工程量清单", "清单计价", "GB50500"],
    "取费": ["管理费", "利润", "规费", "税金", "安全文明施工费"],
    "合同": ["施工合同", "GF-2017-0201", "FIDIC", "变更签证"],
    "人工": ["人工单价", "人工费", "劳务分包"],
    "材料": ["材料价格", "信息价", "钢材", "混凝土"],
    "机械": ["机械台班", "租赁", "降效"],
    "法规": ["建筑法", "招标投标法", "司法解释"],
    "造价": ["全过程造价", "造价咨询", "造价管理"],
}

# KC 编号分配规则（与 auto_kc_generator.py 一致）
DOMAIN_SLOTS = {
    "造价/定额": (100, 129),  "造价/清单": (130, 159),
    "造价/取费": (220, 249),  "造价/人工": (250, 279),
    "造价/材料": (280, 309),  "造价/机械": (310, 339),
    "合同/法务": (400, 449),  "案例复盘": (700, 749),
    "方法论":   (900, 949),
}

CATEGORY_DOMAIN = {
    "定额": "造价/定额", "清单": "造价/清单", "取费": "造价/取费",
    "合同": "合同/法务", "人工": "造价/人工", "材料": "造价/材料",
    "机械": "造价/机械", "法规": "合同/法务", "造价": "方法论",
}


def existing_kc_numbers():
    nums = {}
    for f in VAULT_PATH.rglob("KC-*.md"):
        m = re.search(r'KC-(\d{3})', f.name)
        if m:
            nums[int(m.group(1))] = str(f.relative_to(VAULT_PATH))
    return nums


def assign_kc_number(domain, existing):
    lo, hi = DOMAIN_SLOTS.get(domain, (950, 999))
    for n in range(lo, hi + 1):
        if n not in existing:
            return n
    for n in range(950, 999):
        if n not in existing:
            return n
    return None


def build_kc_basic(keyword, category, domain, number):
    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
tags: [{domain}, KC, 基础知识]
created: {today}
source: 造价行业基础知识库
status: 待核实
type: knowledge-card
---

# KC-{number:03d}: {keyword}

> [KC] 基础知识卡片 | 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 关键词
{keyword}

## 所属类别
{category} -> {domain}

## 核心概念
待补充：{keyword}在工程造价中的定义、适用范围、计价规则。

## 关联规范
- 新疆2020版费用定额（新建标[2021]11号）
- GB/T 50500-2024 建设工程工程量清单计价标准

## 实操要点
待补充：在实际造价工作中如何使用{keyword}。

## 关联卡片
待人工添加

---

[[知识库首页]] | [[10-索引与导航/知识库总索引|KC注册表]]
"""
    return content


def main(dry_run=False):
    print(f"[{datetime.now():%H:%M}] crawl_policy v2.0")
    existing = existing_kc_numbers()
    print(f"  existing KC: {len(existing)}")

    generated = 0
    for category, keywords in BASIC_KEYWORDS.items():
        domain = CATEGORY_DOMAIN.get(category, "方法论")
        for kw in keywords:
            # 检查是否已存在对应关键词的卡片
            already = False
            for num, path in existing.items():
                fname = Path(path).stem
                if kw in fname:
                    already = True
                    break
            if already:
                print(f"  SKIP {kw} (already exists)")
                continue

            num = assign_kc_number(domain, existing)
            if not num:
                print(f"  SKIP {kw} (no slot)")
                continue

            card = build_kc_basic(kw, category, domain, num)
            filename = f"KC-{num:03d}_{kw}.md"
            if not dry_run:
                (KC_DIR / filename).write_text(card, encoding='utf-8')
                existing[num] = filename
            print(f"  {'DRY' if dry_run else 'OK'} KC-{num:03d} [{domain}] {kw}")
            generated += 1

    print(f"\n{'DRY RUN' if dry_run else 'DONE'}: {generated} KC-BASIC cards")
    return generated


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
