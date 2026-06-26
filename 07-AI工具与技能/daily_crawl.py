#!/usr/bin/env python3
"""
新疆造价信息每日采集脚本 v1.0
===================================
数据源（已验证 2026-06-24）：
1. 自治区住建厅：https://zjt.xinjiang.gov.cn/xjzjt/c113382/zwgk_list.shtml（带翻页）
2. 交通厅：https://jtyst.xinjiang.gov.cn/xjjtysj/zjxx/nav2_list.shtml
3. xjzj.com（造价信息网）：首页索引 + 月度综合价格信息
4. 兵团：http://www.xjbt.gov.cn

输出：每日 Markdown 日报 + 关键文件下载
存放：D:\知识库\01-造价核心\造价信息日报_YYYY-MM-DD.md
       D:\\知识库\\01-造价核心\\材料价格\\YYYY-MM-{地州}-综合价格信息.{doc,xlsx}

用法：
  python daily_crawl.py                 # 跑全量
  python daily_crawl.py --quick         # 只跑住建厅 + 造价信息网
  python daily_crawl.py --since 2026-06-20  # 自指定日期以来
"""

import os
import sys
import json
import re
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, date, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# ============== 配置 ==============
VAULT_ROOT = r"D:\知识库"
OUTPUT_DIR = Path(VAULT_ROOT) / "01-造价核心"
MATERIAL_DIR = OUTPUT_DIR / "材料价格"
LOG_DIR = OUTPUT_DIR / "采集日志"

# 数据源
SOURCES = {
    "zjt": {
        "name": "自治区住建厅",
        "base_url": "https://zjt.xinjiang.gov.cn",
        "list_paths": ["/xjzjt/c113382/zwgk_list.shtml"]
    },
    "jtyst": {
        "name": "自治区交通运输厅",
        "base_url": "https://jtyst.xinjiang.gov.cn",
        "list_paths": ["/xjjtysj/zjxx/nav2_list.shtml"]
    },
    "xjzj": {
        "name": "新疆工程造价信息网",
        "base_url": "https://www.xjzj.com",
        "list_paths": ["/"]
    },
    "bingtuan": {
        "name": "新疆生产建设兵团",
        "base_url": "http://www.xjbt.gov.cn",
        "list_paths": ["/"]
    }
}

# 关键词
KEYWORDS = {
    "定额": ["定额", "消耗量定额", "计价定额", "补充定额", "预算定额", "试行定额"],
    "勘误": ["勘误", "更正", "调整", "补充通知", "调整说明"],
    "人工单价": ["人工单价", "工日单价"],
    "材料信息价": ["信息价", "综合价格信息", "材料价格"],
    "国标": ["GB/T50500", "GB50500", "工程量清单计价标准"],
    "造价管理办法": ["造价管理办法", "造价管理"],
    "装配式": ["装配式", "PC"],
    "智能建造": ["智能建造", "建筑机器人"],
}

# ============== 工具函数 ==============

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, timeout=30, retries=2):
    """通用 GET，带 UA 和重试"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, verify=False)
            r.raise_for_status()
            if r.apparent_encoding and 'gb' in r.apparent_encoding.lower():
                r.encoding = 'gb2312'
            else:
                r.encoding = r.apparent_encoding or 'utf-8'
            time.sleep(2)  # 尊重服务器
            return r.text
        except Exception as e:
            if attempt == retries:
                raise
            time.sleep(3)

def classify(title):
    """根据标题分类"""
    matched = []
    for cat, kws in KEYWORDS.items():
        for kw in kws:
            if kw in title:
                matched.append(cat)
                break
    return matched

# ============== 住建厅爬虫 ==============

def crawl_zjt():
    """自治区住建厅：zwgk_list + 翻页 zwgk_list_2..5"""
    items = []
    for page in range(1, 6):
        path = f"/xjzjt/c113382/zwgk_list{('_' + str(page)) if page > 1 else ''}.shtml"
        url = SOURCES["zjt"]["base_url"] + path
        try:
            html = fetch(url, timeout=20)
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=re.compile(r"/xjzjt/c113382/\d{6}/")):
                title = a.get_text(strip=True)
                href = a["href"]
                if not title or len(title) < 5: continue
                full_url = urljoin(url, href)
                # 找日期
                parent = a.parent
                date_text = None
                if parent:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', parent.get_text())
                    if date_match: date_text = date_match.group(1)
                items.append({
                    "source": "zjt",
                    "title": title,
                    "url": full_url,
                    "date": date_text,
                    "categories": classify(title)
                })
        except Exception as e:
            log(f"  ⚠ 住建厅分页 {page} 失败: {e}")
    return items

# ============== 交通厅爬虫 ==============

def crawl_jtyst():
    """交通厅：zjxx/nav2_list（一次性）"""
    items = []
    url = SOURCES["jtyst"]["base_url"] + "/xjjtysj/zjxx/nav2_list.shtml"
    try:
        html = fetch(url, timeout=20)
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=re.compile(r"/xjjtysj/zjxx/")):
            title = a.get_text(strip=True)
            href = a["href"]
            if not title or len(title) < 5: continue
            if 'common_list' in href or 'nav2_list' in href: continue
            full_url = urljoin(url, href)
            # 找日期
            parent_text = a.parent.get_text() if a.parent else ''
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', parent_text)
            items.append({
                "source": "jtyst",
                "title": title,
                "url": full_url,
                "date": date_match.group(1) if date_match else None,
                "categories": classify(title)
            })
    except Exception as e:
        log(f"  ⚠ 交通厅失败: {e}")
    return items

# ============== xjzj.com 爬虫 ==============

def crawl_xjzj():
    """xjzj.com 首页 + 索引"""
    items = []
    url = SOURCES["xjzj"]["base_url"] + "/"
    try:
        html = fetch(url, timeout=20)
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=re.compile(r"/Home/PoliciesDetail/")):
            title = a.get_text(strip=True)
            href = a["href"]
            if not title or len(title) < 5: continue
            # 提取 ID
            id_match = re.search(r'/Home/PoliciesDetail/(\d+)', href)
            if id_match:
                items.append({
                    "source": "xjzj",
                    "title": title,
                    "url": SOURCES["xjzj"]["base_url"] + href,
                    "id": id_match.group(1),
                    "categories": classify(title)
                })
    except Exception as e:
        log(f"  ⚠ xjzj.com 失败: {e}")
    return items

# ============== 月度价格信息下载 ==============

def download_xjzj_prices(month_str):
    """下载 xjzj.com 月度综合价格信息 - 按月度"""
    # 已知价格信息 ID（按月+地州）
    # 2026-04: 6773 (全疆汇总) / 6786-6790 (分地州)
    # 2026-03: 6754
    # 2026-02: 待查
    # 2026-01: 6716
    log(f"  跳过月度价格下载（请在采集完成后人工检查 ID 序列）")
    return []

# ============== 日报生成 ==============

def generate_report(all_items, since_date=None):
    """生成 Markdown 日报"""
    today = date.today().strftime("%Y-%m-%d")
    lines = []
    lines.append(f"---")
    lines.append(f"tags: [造价, 造价/材料, 造价/定额, daily-report]")
    lines.append(f"created: {today}")
    lines.append(f"type: daily-report")
    lines.append(f"status: 自动生成")
    lines.append(f"---")
    lines.append("")
    lines.append(f"# 新疆造价信息采集日报 — {today}")
    lines.append("")
    lines.append(f"> **生成方式**：daily_crawl.py 自动采集 | 核实日期 {today}")
    lines.append("")
    lines.append(f"## 采集概况")
    lines.append("")
    lines.append(f"| 数据源 | 发现 | 重要 | ")
    lines.append(f"|--------|:----:|:----:|")
    for src in ["zjt", "jtyst", "xjzj", "bingtuan"]:
        items = [i for i in all_items if i["source"] == src]
        important = [i for i in items if i["categories"]]
        lines.append(f"| {SOURCES[src]['name']} | {len(items)} | {len(important)} |")
    lines.append(f"| **合计** | **{len(all_items)}** | **{sum(1 for i in all_items if i['categories'])}** |")
    lines.append("")

    # 按分类分组
    by_category = {}
    for item in all_items:
        for cat in item.get("categories", []):
            by_category.setdefault(cat, []).append(item)

    if by_category:
        lines.append("## 🔴 按关键词分类的重要信息")
        lines.append("")
        cat_order = ["造价管理办法", "国标", "智能建造", "装配式",
                     "定额", "勘误", "人工单价", "材料信息价"]
        for cat in cat_order:
            if cat not in by_category: continue
            lines.append(f"### {cat}（{len(by_category[cat])} 条）")
            lines.append("")
            for item in by_category[cat][:15]:
                title = item["title"]
                url = item["url"]
                date_str = item.get("date") or ""
                lines.append(f"- [{date_str}] [{title}]({url})")
            lines.append("")

    # 详细列表
    lines.append("## 📋 全部发现（按数据源）")
    lines.append("")
    for src_key in ["zjt", "jtyst", "xjzj", "bingtuan"]:
        items = [i for i in all_items if i["source"] == src_key]
        if not items: continue
        lines.append(f"### {SOURCES[src_key]['name']}（{len(items)} 条）")
        lines.append("")
        lines.append("| 日期 | 标题 | 分类 |")
        lines.append("|------|------|------|")
        for item in items[:50]:
            date_str = item.get("date") or "—"
            cats = "/".join(item.get("categories", []) or ["未分类"])
            title_short = item["title"][:60]
            lines.append(f"| {date_str} | [{title_short}]({item['url']}) | {cats} |")
        if len(items) > 50:
            lines.append(f"| ... | 共 {len(items)} 条，仅显示前 50 条 | |")
        lines.append("")

    # 链接清单
    lines.append("## 🔗 关键链接（人工下载参考）")
    lines.append("")
    for cat in ["造价管理办法", "国标", "智能建造", "装配式"]:
        if cat not in by_category: continue
        for item in by_category[cat][:5]:
            lines.append(f"- {cat}: [{item['title']}]({item['url']})")
    lines.append("")

    lines.append("---")
    lines.append(f"*自动生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 数据源：住建厅+交通厅+xjzj.com*")
    lines.append("")

    report_path = OUTPUT_DIR / f"造价信息日报_{today}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log(f"✅ 日报已生成: {report_path}")
    return report_path

# ============== 主函数 ==============

def main():
    parser = argparse.ArgumentParser(description="新疆造价信息每日采集")
    parser.add_argument("--quick", action="store_true", help="只跑住建厅 + xjzj.com")
    parser.add_argument("--since", help="自指定日期以来的记录", default=None)
    parser.add_argument("--no-report", action="store_true", help="不生成日报")
    args = parser.parse_args()

    # 确保目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MATERIAL_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log(f"新疆造价信息每日采集 · {date.today()}")
    log("=" * 60)

    all_items = []

    # 1. 住建厅
    log("🏛️  自治区住建厅 ...")
    items = crawl_zjt()
    log(f"   发现 {len(items)} 条")
    all_items.extend(items)

    # 2. 交通厅
    if not args.quick:
        log("🛣️  交通运输厅 ...")
        items = crawl_jtyst()
        log(f"   发现 {len(items)} 条")
        all_items.extend(items)

    # 3. xjzj.com
    log("🌐 新疆工程造价信息网 xjzj.com ...")
    items = crawl_xjzj()
    log(f"   发现 {len(items)} 条")
    all_items.extend(items)

    # 4. 兵团（占位）
    if not args.quick:
        log("🏛️  兵团（暂跳过）...")

    # 去重（按 URL）
    seen = set()
    unique_items = []
    for item in all_items:
        if item["url"] in seen: continue
        seen.add(item["url"])
        unique_items.append(item)
    log(f"📊 去重后共 {len(unique_items)} 条")

    # 时间过滤
    if args.since:
        since_date = args.since
        log(f"🔍 过滤自 {since_date} 以来...")
        unique_items = [i for i in unique_items
                        if i.get("date") and i["date"] >= since_date]
        log(f"   过滤后 {len(unique_items)} 条")

    # 写原始数据 JSON
    raw_path = LOG_DIR / f"raw_{date.today().strftime('%Y%m%d')}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    log(f"💾 原始数据已存: {raw_path}")

    # 生成日报
    if not args.no_report:
        generate_report(unique_items, args.since)

    log("✅ 采集完成")
    return unique_items


if __name__ == "__main__":
    try:
        requests.packages.urllib3.disable_warnings()
    except:
        pass
    main()