#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼎梁筑造价工作台 — 工具函数
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def load_json(filepath: str) -> dict:
    """加载JSON文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: str, data: dict, indent: int = 2):
    """保存JSON文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_yaml_config(filepath: str = "config.yaml") -> dict:
    """加载YAML配置"""
    try:
        import yaml
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        logger.warning("pyyaml 未安装，使用默认配置")
        return {}
    except FileNotFoundError:
        logger.warning(f"配置文件不存在: {filepath}")
        return {}


# ============ 正则提取 ============

DIMENSION_PATTERNS = [
    # 截面尺寸: 200×400, 200x400, 200*400
    (r"(\d{2,4})\s*[×xX\*]\s*(\d{2,4})", "section"),
    # 长度标注: L=5000, 长5000mm, 5000mm
    (r"[L长][=＝]\s*(\d{3,6})\s*(?:mm)?", "length"),
    # 高度标注: H=3000, 高3000
    (r"[H高][=＝]\s*(\d{3,6})\s*(?:mm)?", "height"),
    # 混凝土标号: C30, C35, C40
    (r"(C\d{2})", "concrete_grade"),
    # 钢筋规格: Φ12@150, φ12@150, Φ12
    (r"[Φφ]\s*(\d{1,2})\s*(?:@\s*(\d{2,3}))?", "rebar"),
    # 直径: DN100, DN200
    (r"DN(\d{2,4})", "pipe_diameter"),
    # 壁厚: t=10, 壁厚10mm
    (r"[t壁厚][=＝]\s*(\d{1,3})\s*(?:mm)?", "thickness"),
    # 面积: 100m², 100㎡
    (r"(\d+(?:\.\d+)?)\s*[mM㎡²]", "area"),
    # 体积: 50m³
    (r"(\d+(?:\.\d+)?)\s*[mM³]", "volume"),
    # 楼层层高: F1/F2/1F/2F
    (r"(\d+)\s*[F层]", "floor"),
]


def extract_dimensions(text: str) -> List[dict]:
    """
    从OCR文本提取尺寸标注
    返回: [{type, value, group, original}, ...]
    """
    results = []
    for pattern, dim_type in DIMENSION_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            results.append({
                "type": dim_type,
                "value": match.group(),
                "groups": [g for g in match.groups() if g],
                "span": match.span(),
                "original": text[max(0, match.start()-20):match.end()+20],
            })
    return results


def classify_component(text: str) -> str:
    """
    按关键词分类构件类型
    返回: 梁/板/柱/墙/基础/钢筋/其他
    """
    keywords = {
        "梁": ["梁", "KL", "LL", "XL", "L", "框梁", "连梁", "悬挑梁", "过梁"],
        "板": ["板", "B", "XB", "LB", "WB", "楼板", "屋面板", "底板"],
        "柱": ["柱", "KZ", "Z", "GZ", "AZ", "框柱", "构造柱", "暗柱"],
        "墙": ["墙", "Q", "JQ", "剪力墙", "挡土墙", "砌体墙"],
        "基础": ["基础", "J", "承台", "桩", "筏板", "独立基础", "条基"],
        "钢筋": ["钢筋", "Φ", "φ", "配筋", "箍筋", "纵筋", "拉筋", "HRB"],
    }
    text_upper = text.upper()
    for category, kws in keywords.items():
        if any(kw.upper() in text_upper for kw in kws):
            return category
    return "其他"


def normalize_unit(raw_unit: str) -> str:
    """标准化计量单位"""
    unit_map = {
        "立方米": "m³", "立方": "m³",
        "平方米": "m²", "平方": "m²",
        "米": "m", "毫米": "mm", "厘米": "cm",
        "吨": "t", "千克": "kg", "公斤": "kg",
        "个": "个", "套": "套", "台": "台",
        "工日": "工日", "工": "工日",
    }
    raw = raw_unit.strip().lower()
    return unit_map.get(raw, raw_unit)


def format_number(num: float, decimals: int = 2) -> str:
    """格式化数字为千分位"""
    return f"{num:,.{decimals}f}"


def is_valid_file(filepath: str, valid_exts: tuple = ('.pdf', '.png', '.jpg', '.jpeg')) -> bool:
    """检查是否为有效文件"""
    path = Path(filepath)
    return path.exists() and path.suffix.lower() in valid_exts


def batch_files(directory: str, ext: str = ".pdf") -> List[str]:
    """批量获取文件夹下的文件"""
    path = Path(directory)
    if not path.exists():
        return []
    return sorted([str(f) for f in path.glob(f"*{ext}")])


def ensure_dir(dirpath: str):
    """确保目录存在"""
    Path(dirpath).mkdir(parents=True, exist_ok=True)


def progress_bar(current: int, total: int, prefix: str = "", bar_len: int = 30):
    """控制台进度条"""
    if total == 0:
        return
    percent = current / total
    filled = int(bar_len * percent)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r{prefix} |{bar}| {current}/{total} ({percent*100:.1f}%)", end="")
    if current >= total:
        print()


# ============ 新疆造价参数 ============

XINJIANG_LABOR_RATES = {
    "乌鲁木齐": {"一类": 130, "二类": 155, "三类": 180},
    "伊犁": {"一类": 130, "二类": 148, "三类": None},  # ⚠待核实
    "喀什": {"一类": 147, "二类": 162, "三类": None},   # ⚠待核实, 高海拔×1.10
    "石河子": {"一类": 114, "二类": 148, "三类": 172},
    "阿克苏": {"一类": 125, "二类": None, "三类": None},  # ⚠待核实
    "昌吉": {"一类": 128, "二类": None, "三类": None},    # ⚠待核实
}

XINJIANG_FEE_RATES = {
    "管理费": 0.28,
    "利润": 0.18,
    "规费": 0.22,
    "增值税": 0.09,
    "措施费": 0.045,
    "安全文明": 0.025,
}

KASHI_HIGH_ALTITUDE_FACTOR = 1.10  # 喀什高海拔系数


def get_labor_rate(region: str, category: str = "一类") -> Optional[float]:
    """获取人工基价"""
    region_data = XINJIANG_LABOR_RATES.get(region, {})
    rate = region_data.get(category)
    if rate and region == "喀什":
        rate *= KASHI_HIGH_ALTITUDE_FACTOR
    return rate


def get_fee_rate(fee_name: str) -> float:
    """获取取费费率"""
    return XINJIANG_FEE_RATES.get(fee_name, 0.0)
