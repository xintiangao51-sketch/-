#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawl_info_price.py — 新疆各地州信息价自动采集（P2 信息价自动化）

功能：
    1. 扫描 xjzj.com 各地州最新信息价公告
    2. 下载附件（xls/xlsx/docx/pdf）
    3. 归类存储到 D:\信息价 或 D:\知识库\11-材料设备价格库
    4. 更新 KC-283 信息价索引
    5. 输出采集报告

用法：
    python D:\知识库\.scripts\crawl_info_price.py                      # 全地州扫描
    python D:\知识库\.scripts\crawl_info_price.py --region 乌鲁木齐      # 指定地州
    python D:\知识库\.scripts\crawl_info_price.py --list-regions        # 列出支持的地州
    python D:\知识库\.scripts\crawl_info_price.py --since 2026-06-01    # 指定时间范围

依赖：
    pip install requests beautifulsoup4 openpyxl --break-system-packages

配置：
    输出目录：（自动探测）
        D:\信息价\（首选）
        D:\知识库\11-材料设备价格库\（备选）
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime, date
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 配置区
# ═══════════════════════════════════════════════════════════

# xjzj.com 信息价检索页
XJZJ_SEARCH_URL = "https://www.xjzj.com/Home/CheckView"

# 各地州信息价检索参数
REGIONS = {
    "乌鲁本齐": {"keyword": "乌鲁本齐 建设工程价格信息", "id": 6788},
    "伊犁": {"keyword": "伊犁 建设工程价格信息"},
    "塔城": {"keyword": "塔城 建设工程价格信息"},
    "阿勒泰": {"keyword": "阿勒泰 建设工程价格信息"},
    "博乐": {"keyword": "博乐 建设工程价格信息"},
    "克拉玛依": {"keyword": "克拉玛依 建设工程价格信息"},
    "哈密": {"keyword": "哈密 建设工程价格信息"},
    "吐鲁番": {"keyword": "吐鲁番 建设工程价格信息"},
    "喀什": {"keyword": "喀什 建设工程价格信息"},
    "阿克苏": {"keyword": "阿克苏 建设工程价格信息"},
    "库尔勒": {"keyword": "库尔勒 建设工程价格信息"},
    "巴州": {"keyword": "巴州 建设工程价格信息"},
    "昌吉": {"keyword": "昌吉 建设工程价格信息"},
    "克州": {"keyword": "克州 建设工程价格信息"},
    "和田": {"keyword": "和田 建设工程价格信息"},
    "石河子": {"keyword": "石河子 建设工程价格信息"},
    "奎屯": {"keyword": "奎屯 建设工程价格信息"},
    "五家渠": {"keyword": "五家渠 建设工程价格信息"},
}

# 输出目录探测
DEFAULT_OUTPUT_DIRS = [r"D:\信息价", r"D:\知识库\11-材料设备价格库"]


def detect_output_dir():
    for d in DEFAULT_OUTPUT_DIRS:
        if os.path.isdir(d):
            return d
    # 默认取第一个
    os.makedirs(DEFAULT_OUTPUT_DIRS[0], exist_ok=True)
    return DEFAULT_OUTPUT_DIRS[0]


# 索引文件（KC-283 的素材索引）
INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "11-材料设备价格库", "_info_price_index.json")

# ═══════════════════════════════════════════════════════════
# 核心功能
# ═══════════════════════════════════════════════════════════

def fetch_xjzj_list(keyword: str) -> list:
    """
    从 xjzj.com 检索最新信息价公告
    返回 [{title, url, date, attachments}]
    """
    print(f"  🔍 检索: {keyword}")
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("  ❌ 缺少依赖: pip install requests beautifulsoup4 --break-system-packages")
        return []

    try:
        resp = requests.get(
            XJZJ_SEARCH_URL,
            params={"content": keyword},
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            print(f"  ⚠ HTTP {resp.status_code}")
            return []

        # 解析列表
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for link in soup.select("a[href*='PoliciesDetail']"):
            title = link.get_text(strip=True)
            url = link.get("href")
            if not url.startswith("http"):
                url = "https://www.xjzj.com" + url
            items.append({"title": title, "url": url})

        return items

    except Exception as e:
        print(f"  ⚠ 检索失败: {e}")
        return []


def fetch_attachments(url: str, output_dir: str, region: str) -> list:
    """
    下载附件到 output_dir/{region}/
    返回下载文件列表
    """
    import requests
    from bs4 import BeautifulSoup

    save_dir = os.path.join(output_dir, region)
    os.makedirs(save_dir, exist_ok=True)

    downloaded = []

    try:
        resp = requests.get(url, timeout=15,
                            headers={"User-Agent": "Mozilla/5.0"})
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return downloaded

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            # 过滤附件链接
            if any(ext in href.lower() for ext in ['.xls', '.xlsx', '.doc', '.docx', '.pdf']):
                if not href.startswith("http"):
                    href = "https://www.xjzj.com" + href if href.startswith("/") else href

                filename = os.path.basename(href).split("?")[0]
                if not filename:
                    filename = a.get_text(strip=True)[:30] + ".xls"

                filepath = os.path.join(save_dir, filename)
                try:
                    file_resp = requests.get(href, timeout=30,
                                             headers={"User-Agent": "Mozilla/5.0"})
                    if file_resp.status_code == 200:
                        with open(filepath, "wb") as f:
                            f.write(file_resp.content)
                        downloaded.append(filepath)
                        print(f"    📥 {filename} ({len(file_resp.content)//1024}KB)")
                except Exception as e:
                    print(f"    ⚠ 下载失败 {filename}: {e}")

        return downloaded

    except Exception as e:
        print(f"  ⚠ 附件解析失败: {e}")
        return []


def update_index(region: str, downloaded: list):
    """更新信息价索引 JSON"""
    if not downloaded:
        return

    index = {}
    if os.path.isfile(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                index = json.load(f)
        except:
            index = {}

    today = date.today().isoformat()
    if region not in index:
        index[region] = []

    for fp in downloaded:
        entry = {
            "file": os.path.basename(fp),
            "path": os.path.relpath(fp, os.path.dirname(INDEX_FILE)),
            "date": today,
            "source": "xjzj.com",
        }
        index[region].append(entry)

    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"  📋 索引已更新: {INDEX_FILE}")


def list_regions():
    print(f"支持的地州（{len(REGIONS)} 个）：")
    for i, (name, info) in enumerate(sorted(REGIONS.items()), 1):
        print(f"  {i:2d}. {name}")
        if "id" in info:
            print(f"       xjzj.com ID={info['id']}")


def scan_region(region: str, output_dir: str):
    """扫描单个地州的信息价"""
    info = REGIONS.get(region)
    if not info:
        print(f"❌ 未知地州: {region}，使用 --list-regions 查看")
        return

    keyword = info["keyword"]
    items = fetch_xjzj_list(keyword)

    if not items:
        print(f"  💡 未检索到公告，可能是网络问题或站点改版")
        return

    print(f"  检索到 {len(items)} 条结果")
    for item in items[:5]:
        print(f"    📄 {item['title'][:60]}")
        if "PoliciesDetail" in item["url"]:
            downloaded = fetch_attachments(item["url"], output_dir, region)
            update_index(region, downloaded)


def scan_all(output_dir: str):
    """全地州扫描"""
    print(f"\n{'='*60}")
    print(f"新疆各地州信息价自动采集")
    print(f"输出目录: {output_dir}")
    print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    for region in sorted(REGIONS.keys()):
        print(f"\n--- {region} ---")
        scan_region(region, output_dir)


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="新疆各地州信息价自动采集")
    parser.add_argument("--region", type=str, default=None, help="指定地州名称")
    parser.add_argument("--list-regions", action="store_true", help="列出支持的地州")
    parser.add_argument("--since", type=str, default=None, help="时间范围（YYYY-MM-DD）")
    args = parser.parse_args()

    output_dir = detect_output_dir()

    if args.list_regions:
        list_regions()
        return

    if args.region:
        scan_region(args.region, output_dir)
    else:
        scan_all(output_dir)

    print(f"\n✅ 采集完成")


if __name__ == "__main__":
    main()
