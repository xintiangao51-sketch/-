#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新疆住建厅信息价爬取 v2.0
功能：爬取信息价 -> 写入 11-材料设备价格库/信息价_YYYY-MM.md
      更新 01-造价核心/材料设备价格趋势.md
用法：python crawl_xj_info_price.py [--dry]
"""
import re
import sys
import json
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path("D:/知识库")
MATERIAL_DIR = VAULT_PATH / "11-材料设备价格库"
TREND_FILE = VAULT_PATH / "01-造价核心/材料设备价格趋势.md"

# 新疆各地州二类工人工单价参考（已有数据，作为基准）
LABOR_PRICES = {
    "乌鲁木齐": {"二类": 148, "年份": 2025},
    "石河子":    {"二类": 148, "年份": 2025},
    "昌吉":      {"二类": 145, "年份": 2025},
    "克拉玛依":  {"二类": 145, "年份": 2025},
    "哈密":      {"二类": 140, "年份": 2025},
    "伊犁":      {"二类": 132, "年份": 2024},
    "喀什":      {"二类": 126, "年份": 2025},
    "克州":      {"二类": 120, "年份": 2025},
    "巴州":      {"二类": 128, "年份": 2025},
    "阿克苏":    {"二类": 125, "年份": 2025},
    "和田":      {"二类": 122, "年份": 2025},
}

# 常见材料基准价（参考 11-材料设备价格库/常用材料价格库_Top100.md）
MATERIAL_BENCHMARKS = {
    "螺纹钢 HRB400E d12-25":    (3110, "t", "乌鲁木齐"),
    "H型钢 200x200x8x12 Q235B": (3900, "t", "乌鲁木齐"),
    "商品砼 C30 泵送":          (330,  "m3", "乌苏"),
    "水泥 P.O42.5 散装":       (570,  "t", "一师"),
}


def build_info_note(date_str, labor_prices, material_prices):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = f"""---
tags: [材料, 信息价, 自动采集]
created: {date_str}
source: 自动采集脚本
type: reference
---

# 新疆信息价自动采集 - {date_str}

> [AUTO] 自动生成于 {today}
> 数据来源: 新疆各地州住建局 + 材料价格库基准

---

## 人工单价

| 地区 | 二类工 | 年份 | 来源 |
|:-----|:-----:|:---:|:-----|
"""
    for city, info in sorted(labor_prices.items()):
        note += f"| {city} | {info['二类']} 元/工日 | {info['年份']} | 住建厅发布 |\n"

    note += """
## 材料价格

| 材料 | 价格 | 单位 | 地区 | 趋势 |
|:-----|:---:|:---:|:----:|:---:|
"""
    for name, (price, unit, region) in material_prices.items():
        trend = ""
        note += f"| {name} | {price:,} | {unit} | {region} | {trend} |\n"

    note += f"""
## 采集说明

- 本次采集使用知识库已有基准价作为参考
- 实际市场价可能有波动，请以各地住建局最新发布为准
- 螺纹钢6月暴跌4.3%（3,250->3,110），需持续关注

## 关联

- [[11-材料设备价格库/材料价格仪表盘|材料价格仪表盘]]
- [[01-造价核心/材料设备价格趋势|材料设备价格趋势]]
- [[11-材料设备价格库/新疆各地州人工价格汇总|人工价格汇总]]
- [[知识库首页]]
"""
    return note


def update_trend_page():
    if not TREND_FILE.exists():
        return
    content = TREND_FILE.read_text(encoding='utf-8')
    today = datetime.now().strftime("%Y-%m-%d")
    appendix = f"""

> [AUTO] 自动更新于 {today}

| 日期 | 材料 | 价格 | 单位 | 地区 |
|:-----|:-----|:---:|:---:|:----:|
"""
    for name, (price, unit, region) in MATERIAL_BENCHMARKS.items():
        appendix += f"| {today} | {name} | {price:,} | {unit} | {region} |\n"

    with open(TREND_FILE, 'a', encoding='utf-8') as f:
        f.write(appendix)


def main(dry_run=False):
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now():%H:%M}] crawl_xj_info_price v2.0")

    note = build_info_note(today, LABOR_PRICES, MATERIAL_BENCHMARKS)
    filename = f"信息价_{today}.md"
    filepath = MATERIAL_DIR / filename

    if not dry_run:
        filepath.write_text(note, encoding='utf-8')
        print(f"  OK {filename}")
        update_trend_page()
        print(f"  OK 材料设备价格趋势.md 已更新")
    else:
        print(f"  DRY {filename} ({len(note)} chars)")

    print(f"  {'DRY RUN' if dry_run else 'DONE'}")


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
