#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 3 — 图纸量与清单量比对
功能: OCR识别图纸工程量 → 与已有BOQ清单逐项比对 → 标记偏差
"""

import os
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from shared.models import BOQItem, DiffRecord, RiskLevel
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from shared.models import BOQItem, DiffRecord, RiskLevel


class BOQChecker:
    """
    图纸量 vs 清单量 核验器

    比对逻辑:
    - 编码相同 → 比对数量偏差
    - 图纸有、清单无 → 漏项
    - 清单有、图纸无 → 多算
    - 偏差率 ≤5% → 正常
    - 偏差率 5-15% → 黄线
    - 偏差率 >15% → 红线
    """

    def __init__(self, deviation_green: float = 5.0,
                 deviation_yellow: float = 15.0):
        """
        :param deviation_green: 绿色阈值(%)
        :param deviation_yellow: 黄色阈值(%)
        """
        self.green_threshold = deviation_green
        self.yellow_threshold = deviation_yellow

    def compare(self, drawing_items: List[dict], boq_items: List[BOQItem]) -> List[DiffRecord]:
        """
        逐项比对

        :param drawing_items: 图纸提取的工程量 [{code, name, quantity}, ...]
        :param boq_items: 清单项列表
        :return: DiffRecord列表
        """
        # 索引化
        drawing_map = {}
        for d in drawing_items:
            code = d.get("code", d.get("name", "")).strip()
            if code:
                drawing_map[code] = d

        boq_map = {item.code: item for item in boq_items if item.code}

        results = []

        # 1. 比对共有的编码
        common_codes = set(drawing_map.keys()) & set(boq_map.keys())
        for code in sorted(common_codes):
            draw_qty = float(drawing_map[code].get("quantity", 0) or 0)
            boq_qty = boq_map[code].quantity

            if draw_qty == 0 and boq_qty == 0:
                continue

            if draw_qty == 0:
                deviation = 100.0
            else:
                deviation = (boq_qty - draw_qty) / draw_qty * 100

            # 风险等级
            abs_dev = abs(deviation)
            if abs_dev <= self.green_threshold:
                risk = RiskLevel.BLUE
                dev_type = "正常"
            elif abs_dev <= self.yellow_threshold:
                risk = RiskLevel.YELLOW
                dev_type = "偏差"
            else:
                risk = RiskLevel.RED
                dev_type = "偏差"

            name = (drawing_map[code].get("name", "") or
                   boq_map[code].name)

            results.append(DiffRecord(
                code=code,
                name=name,
                drawing_qty=round(draw_qty, 2),
                boq_qty=round(boq_qty, 2),
                deviation=round(deviation, 1),
                deviation_type=dev_type,
                risk_level=risk,
            ))

        # 2. 图纸有、清单无 → 漏项
        missing_codes = set(drawing_map.keys()) - set(boq_map.keys())
        for code in sorted(missing_codes):
            d = drawing_map[code]
            qty = float(d.get("quantity", 0) or 0)
            results.append(DiffRecord(
                code=code,
                name=d.get("name", code),
                drawing_qty=round(qty, 2),
                boq_qty=0,
                deviation=-100.0,
                deviation_type="漏项",
                risk_level=RiskLevel.RED,
                remark="图纸有此项目但清单缺失",
            ))

        # 3. 清单有、图纸无 → 多算
        extra_codes = set(boq_map.keys()) - set(drawing_map.keys())
        for code in sorted(extra_codes):
            item = boq_map[code]
            results.append(DiffRecord(
                code=code,
                name=item.name,
                drawing_qty=0,
                boq_qty=round(item.quantity, 2),
                deviation=100.0,
                deviation_type="多算",
                risk_level=RiskLevel.YELLOW,
                remark="清单有此项目但图纸未识别到(可能OCR遗漏)",
            ))

        logger.info(f"比对完成: 正常{sum(1 for r in results if r.risk_level==RiskLevel.BLUE)}项, "
                    f"偏差{sum(1 for r in results if r.risk_level==RiskLevel.YELLOW)}项, "
                    f"红线{sum(1 for r in results if r.risk_level==RiskLevel.RED)}项, "
                    f"漏项{len(missing_codes)}项, 多算{len(extra_codes)}项")

        return results

    def generate_summary(self, results: List[DiffRecord]) -> dict:
        """生成比对摘要"""
        summary = {
            "总比对项": len(results),
            "正常(≤5%)": 0,
            "偏差(5-15%)": 0,
            "红线(>15%)": 0,
            "漏项": 0,
            "多算": 0,
        }
        for r in results:
            if r.deviation_type == "漏项":
                summary["漏项"] += 1
            elif r.deviation_type == "多算":
                summary["多算"] += 1
            elif r.risk_level == RiskLevel.BLUE:
                summary["正常(≤5%)"] += 1
            elif r.risk_level == RiskLevel.YELLOW:
                summary["偏差(5-15%)"] += 1
            elif r.risk_level == RiskLevel.RED:
                summary["红线(>15%)"] += 1
        return summary

    def filter_high_risk(self, results: List[DiffRecord]) -> List[DiffRecord]:
        """筛选高风险项(黄线+红线)"""
        return [r for r in results if r.risk_level in (RiskLevel.YELLOW, RiskLevel.RED)]
