#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 3 — 差异报告生成
功能: 输出差异核验报告Excel
"""

import os
import logging
from typing import List

logger = logging.getLogger(__name__)

try:
    from shared.models import DiffRecord
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from shared.models import DiffRecord


def generate_diff_report(diff_records: List[DiffRecord],
                         project_name: str,
                         output_path: str) -> str:
    """
    生成差异核验报告Excel

    :param diff_records: 差异记录列表
    :param project_name: 项目名称
    :param output_path: 输出路径
    :return: 文件路径
    """
    from shared.excel_io import write_diff_report
    return write_diff_report(output_path, diff_records, project_name)


def generate_markdown_report(diff_records: List[DiffRecord],
                             project_name: str,
                             output_path: str = None) -> str:
    """
    生成Markdown格式差异报告

    :return: Markdown文本
    """
    from collections import Counter

    now = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")

    # 统计
    risk_counts = Counter(r.risk_level.value for r in diff_records)
    type_counts = Counter(r.deviation_type for r in diff_records)

    lines = [
        f"# {project_name} — 图纸vs清单差异核验报告",
        f"",
        f"> 生成时间: {now}",
        f"> 比对项数: {len(diff_records)}",
        f"",
        f"---",
        f"",
        f"## 统计摘要",
        f"",
        f"| 指标 | 数量 |",
        f"|------|------|",
    ]

    for level, count in sorted(risk_counts.items()):
        lines.append(f"| {level} | {count} |")

    lines.append(f"")
    lines.append(f"## 偏差类型分布")
    lines.append(f"")
    for dtype, count in sorted(type_counts.items()):
        lines.append(f"| {dtype} | {count} |")

    # 红线列表
    red_items = [r for r in diff_records if "红线" in r.risk_level.value]
    if red_items:
        lines.append(f"")
        lines.append(f"## 🔴 红线项 (需立即处理)")
        lines.append(f"")
        lines.append(f"| 编码 | 名称 | 图纸量 | 清单量 | 偏差率 | 类型 |")
        lines.append(f"|------|------|--------|--------|--------|------|")
        for r in red_items:
            lines.append(f"| {r.code} | {r.name} | {r.drawing_qty} | {r.boq_qty} | {r.deviation}% | {r.deviation_type} |")

    # 黄线列表
    yellow_items = [r for r in diff_records if "黄线" in r.risk_level.value]
    if yellow_items:
        lines.append(f"")
        lines.append(f"## 🟡 黄线项 (建议复核)")
        lines.append(f"")
        lines.append(f"| 编码 | 名称 | 图纸量 | 清单量 | 偏差率 | 类型 |")
        lines.append(f"|------|------|--------|--------|--------|------|")
        for r in yellow_items:
            lines.append(f"| {r.code} | {r.name} | {r.drawing_qty} | {r.boq_qty} | {r.deviation}% | {r.deviation_type} |")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*报告自动生成 · {now}*")

    report = "\n".join(lines)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"差异报告已保存: {output_path}")

    return report
