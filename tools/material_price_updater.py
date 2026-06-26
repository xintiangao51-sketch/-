#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材料价格趋势更新器 v2.0
功能：扫描 11-材料设备价格库/ 中的最新价格数据
      更新 01-造价核心/材料设备价格趋势.md
用法：python material_price_updater.py [--dry]
"""
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path("D:/知识库")
MATERIAL_DIR = VAULT_PATH / "11-材料设备价格库"
TREND_FILE = VAULT_PATH / "01-造价核心/材料设备价格趋势.md"


def extract_prices():
    prices = {}
    for f in MATERIAL_DIR.rglob("*.md"):
        try:
            content = f.read_text(encoding='utf-8')
        except Exception:
            continue
        for line in content.split('\n'):
            m = re.match(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*([\d,]+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', line)
            if m:
                name, spec, price_str, unit, region = m.groups()
                try:
                    price = int(price_str.replace(',', ''))
                except ValueError:
                    continue
                key = f"{name.strip()} {spec.strip()}"
                if key not in prices:
                    prices[key] = []
                prices[key].append({
                    "price": price,
                    "unit": unit.strip(),
                    "region": region.strip(),
                    "source": str(f.relative_to(VAULT_PATH)),
                })
    return prices


def update_trend(prices, dry_run=False):
    if not TREND_FILE.exists():
        return 0
    today = datetime.now().strftime("%Y-%m-%d")
    key_materials = ["螺纹钢 HRB400E", "商品砼 C30", "水泥 P.O42.5"]
    updates = []
    for kw in key_materials:
        for key, entries in prices.items():
            if kw in key and entries:
                latest = sorted(entries, key=lambda x: x.get('date', ''), reverse=True)[0]
                updates.append(f"| {today} | {key} | {latest['price']:,} | {latest['unit']} | {latest['region']} |")

    if not updates:
        return 0

    appendix = f"\n> [AUTO] 更新于 {today}\n| 日期 | 材料 | 价格 | 单位 | 地区 |\n|:-----|:-----|:---:|:---:|:----:|\n"
    appendix += '\n'.join(updates)

    if not dry_run:
        with open(TREND_FILE, 'a', encoding='utf-8') as f:
            f.write(appendix)
    return len(updates)


def main(dry_run=False):
    print(f"[{datetime.now():%H:%M}] material_price_updater v2.0")
    prices = extract_prices()
    total = sum(len(v) for v in prices.values())
    print(f"  {total} price records ({len(prices)} materials)")
    updated = update_trend(prices, dry_run=dry_run)
    print(f"  {'DRY' if dry_run else 'UPDATED'} {updated} entries in trend page")
    print(f"  {'DRY RUN' if dry_run else 'DONE'}")


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
