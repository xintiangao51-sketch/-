#!/usr/bin/env python3
"""
新疆建设工程综合价格信息自动下载脚本 v1.0
=============================================
数据源：xjzj.com
用途：自动下载指定月份+地州的 doc+xlsx，存入"近期材料价"目录
更新于：2026-06-24

用法：
  python price_downloader.py                       # 下载最新一期（自动探查）
  python price_downloader.py --month 2026-04       # 下载指定月份
  python price_downloader.py --month 2026-04 --region 乌鲁木齐
  python price_downloader.py --all                # 下载最近 3 个月
  python price_downloader.py --discover            # 仅探查 xjzj.com 不下载
"""

import os
import sys
import re
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, date
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup

# ============== 配置 ==============
VAULT_ROOT = Path(r"D:\知识库")
OUTPUT_DIR = VAULT_ROOT / "01-造价核心" / "定额与计价" / "近期材料价"
RAW_DIR = VAULT_ROOT / "01-造价核心" / "采集日志"

XJZJ_BASE = "https://www.xjzj.com"

# 已知的 xjzj.com 月度价格信息 ID 映射（按月份→地州→ID）
# 数据来源：2026-06-24 实测
KNOWN_IDS = {
    "2026-04": {
        "全疆汇总": 6773,
        "克州": 6784,
        "石河子": 6785,
        "塔城地区": 6786,
        "吐鲁番": 6787,
        "乌鲁木齐市": 6788,
        "五家渠市": 6789,
        "伊犁州直各县市": 6790,
    },
    "2026-03": {
        "全疆汇总": 6754,
    },
    "2026-01": {
        "全疆汇总": 6716,
    },
    "2025-12": {
        "全疆汇总": 6696,
    },
    # 后续月份通过 --discover 自动发现
}

# ============== 工具 ==============

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, timeout=30, retries=2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, verify=False)
            r.raise_for_status()
            if r.apparent_encoding and 'gb' in r.apparent_encoding.lower():
                r.encoding = 'gb2312'
            else:
                r.encoding = r.apparent_encoding or 'utf-8'
            time.sleep(1.5)
            return r.text
        except Exception as e:
            if attempt == retries:
                raise
            time.sleep(3)


def discover_xjzj_prices():
    """
    从 xjzj.com 首页抓取所有月度价格信息条目
    返回 list[dict] = [{month, region, id, url}]
    """
    log(f"🌐 探查 {XJZJ_BASE}/ ...")
    items = []
    try:
        html = fetch(XJZJ_BASE + "/")
    except Exception as e:
        log(f"❌ 首页抓取失败: {e}")
        return items

    soup = BeautifulSoup(html, "html.parser")

    # 匹配 "X 地州 YYYY 年 M 月份建设工程综合价格信息"
    price_pattern = re.compile(
        r'(自治[区州]|.*?(?:市|地区|州|县))(20\d{2})年(\d{1,2})月(?:份)?建设工程综合价格信息'
    )
    summary_pattern = re.compile(r'(自治区各地[、，]?州[、，]?市)(20\d{2})年(\d{1,2})月(?:份)?建设工程综合价格信息')

    for a in soup.find_all("a", href=re.compile(r"/Home/PoliciesDetail/\d+")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        id_match = re.search(r'/Home/PoliciesDetail/(\d+)', href)
        if not id_match:
            continue
        item_id = int(id_match.group(1))

        # 提取月份+地州
        m = price_pattern.search(title) or summary_pattern.search(title)
        if m:
            region = m.group(1).strip()
            year = m.group(2)
            month = m.group(3).zfill(2)
            month_str = f"{year}-{month}"
            items.append({
                "month": month_str,
                "region": region,
                "id": item_id,
                "title": title,
                "url": XJZJ_BASE + href,
            })

    log(f"   发现 {len(items)} 条月度价格信息")
    return items


def fetch_xjzj_detail(item_id):
    """获取详情页，提取 doc/xlsx 下载链接"""
    url = f"{XJZJ_BASE}/Home/PoliciesDetail/{item_id}"
    try:
        html = fetch(url)
    except Exception as e:
        log(f"   ⚠ 详情页失败: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    links = {}
    for a in soup.find_all("a", href=re.compile(r"javascript:LookFile")):
        href = a.get("href", "")
        # javascript:LookFile('/Upload/File/.../filename.ext')
        file_match = re.search(r"LookFile\('([^']+)'\)", href)
        if not file_match:
            continue
        path = file_match.group(1)
        # 提取文件名
        name_match = re.search(r'/([^/]+)$', path)
        if not name_match:
            continue
        filename = name_match.group(1)
        ext = filename.split('.')[-1].lower()
        if ext in ('doc', 'docx', 'xls', 'xlsx'):
            links[ext] = path

    return links


def download_file(path_on_server, save_path):
    """从 xjzj.com 下载文件（路径形如 /Upload/File/UUID/filename.ext）"""
    full_url = XJZJ_BASE + path_on_server
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if save_path.exists():
        log(f"   ⏭️ 已存在: {save_path.name}")
        return True

    try:
        r = requests.get(full_url, timeout=60, verify=False, stream=True,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        r.raise_for_status()

        # 处理 URL 编码的文件名
        # path 形如 /Upload/File/UUID/中文文件名.doc
        # 服务器路径部分可能含 URL 编码的 %xx
        from urllib.parse import unquote
        save_path = save_path.parent / unquote(save_path.name)

        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        size_kb = save_path.stat().st_size / 1024
        log(f"   ✅ 已下载: {save_path.name} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        log(f"   ❌ 下载失败: {e}")
        return False


def download_one(item):
    """下载一条价格信息"""
    month = item["month"]
    region = item["region"]
    item_id = item["id"]
    safe_region = re.sub(r'[\\/:*?"<>|]', '_', region)

    log(f"📥 {month} | {region} (ID={item_id})")
    links = fetch_xjzj_detail(item_id)
    if not links:
        log(f"   ⚠ 未发现附件链接")
        return 0

    saved = 0
    month_dir = OUTPUT_DIR / month
    month_dir.mkdir(parents=True, exist_ok=True)

    # doc / docx
    for ext in ('doc', 'docx'):
        if ext in links:
            save_path = month_dir / f"{month}-{safe_region}-综合价格信息.{ext}"
            if download_file(links[ext], save_path):
                saved += 1

    # xls / xlsx
    for ext in ('xls', 'xlsx'):
        if ext in links:
            save_path = month_dir / f"{month}-{safe_region}-综合价格信息.{ext}"
            if download_file(links[ext], save_path):
                saved += 1

    return saved


def update_known_ids(discovered_items):
    """把发现结果合并到 KNOWN_IDS"""
    for item in discovered_items:
        m = item["month"]
        r = item["region"]
        KNOWN_IDS.setdefault(m, {})[r] = item["id"]


# ============== 主函数 ==============

def main():
    parser = argparse.ArgumentParser(description="新疆月度综合价格信息下载")
    parser.add_argument("--month", help="指定月份 (YYYY-MM)，如 2026-04")
    parser.add_argument("--region", help="指定地州，如 乌鲁木齐/伊犁/塔城")
    parser.add_argument("--all", action="store_true", help="下载最近 3 个月")
    parser.add_argument("--discover", action="store_true", help="仅探查，不下载")
    parser.add_argument("--list-known", action="store_true", help="列出已知 ID 映射")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log(f"新疆月度综合价格信息下载 · {date.today()}")
    log("=" * 60)

    # 0. 列出已知
    if args.list_known:
        log("\n📋 已知 xjzj.com 月度价格信息 ID 映射：")
        for month, regions in sorted(KNOWN_IDS.items(), reverse=True):
            log(f"\n  [{month}]")
            for region, id_ in regions.items():
                log(f"    ID {id_} | {region}")
        return

    # 1. 探查 xjzj.com
    discovered = discover_xjzj_prices()

    if args.discover:
        # 写发现结果
        raw_path = RAW_DIR / f"price_discover_{date.today().strftime('%Y%m%d')}.json"
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(discovered, f, ensure_ascii=False, indent=2)
        log(f"💾 探查结果: {raw_path}")
        return

    # 合并到 KNOWN_IDS
    update_known_ids(discovered)
    log(f"📊 已知 + 发现 共 {sum(len(r) for r in KNOWN_IDS.values())} 个 ID")

    # 2. 选择要下载的条目
    todo = []

    if args.all:
        # 最近 3 个月（包含发现的最新 + 已知）
        all_months = sorted(set(list(KNOWN_IDS.keys()) + [i["month"] for i in discovered]), reverse=True)
        target_months = all_months[:3]
        for month in target_months:
            for region, id_ in KNOWN_IDS.get(month, {}).items():
                todo.append({"month": month, "region": region, "id": id_})

    elif args.month:
        target_month = args.month
        if target_month not in KNOWN_IDS:
            log(f"⚠ {target_month} 在已知/探查中无 ID，尝试指定 region...")
        for region, id_ in KNOWN_IDS.get(target_month, {}).items():
            if args.region and args.region not in region:
                continue
            todo.append({"month": target_month, "region": region, "id": id_})

    else:
        # 默认：下载最新一期全部地州
        latest_month = max(KNOWN_IDS.keys(), key=lambda m: m)
        log(f"🎯 最新一期: {latest_month}")
        for region, id_ in KNOWN_IDS[latest_month].items():
            todo.append({"month": latest_month, "region": region, "id": id_})

    log(f"📦 待下载: {len(todo)} 个条目")

    # 3. 执行下载
    total_saved = 0
    success = 0
    for item in todo:
        if download_one(item):
            success += 1
        total_saved += 1

    log("")
    log("=" * 60)
    log(f"✅ 完成：{success}/{total_saved} 成功")
    log(f"📂 输出目录：{OUTPUT_DIR}")
    log("=" * 60)


if __name__ == "__main__":
    try:
        requests.packages.urllib3.disable_warnings()
    except:
        pass
    main()