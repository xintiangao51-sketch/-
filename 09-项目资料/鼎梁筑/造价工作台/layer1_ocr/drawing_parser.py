#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1 — 图纸结构识别
功能: 从OCR文本按构件类型分类(梁/板/柱/墙/基础/钢筋)
"""

import re
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class DrawingParser:
    """施工图纸结构识别器"""

    # 构件识别关键词
    COMPONENT_PATTERNS = {
        "梁": {
            "keywords": ["梁", "KL", "LL", "XL", "L", "框梁", "连梁", "悬挑梁", "过梁",
                        "WKL", "JZL", "TL", "LZ"],
            "section_pattern": r"[梁Ll]\s*(\d+)\s*[×xX*]\s*(\d+)",  # 梁截面 L1 200×400
            "length_pattern": r"(?:跨度|净跨|梁长)[=＝:：]?\s*(\d+)",
        },
        "板": {
            "keywords": ["板", "B", "XB", "LB", "WB", "楼板", "屋面板", "底板",
                        "PB", "MB"],
            "thickness_pattern": r"[板hH][厚=＝]\s*(\d+)\s*(?:mm)?",  # 板厚100mm
            "area_pattern": r"(?:板面积)[=＝:：]?\s*(\d+(?:\.\d+)?)",
        },
        "柱": {
            "keywords": ["柱", "KZ", "Z", "GZ", "AZ", "框柱", "构造柱", "暗柱",
                        "LZ", "YZ", "QZ", "XZ"],
            "section_pattern": r"[柱KZzZ]\s*(\d+)\s*[×xX*]\s*(\d+)",  # KZ1 400×400
        },
        "墙": {
            "keywords": ["墙", "Q", "JQ", "剪力墙", "挡土墙", "砌体墙",
                        "JLQ", "YQ"],
            "thickness_pattern": r"(?:墙厚|墙体厚度)[=＝:：]?\s*(\d+)\s*(?:mm)?",
        },
        "基础": {
            "keywords": ["基础", "J", "承台", "桩", "筏板", "独立基础", "条基",
                        "CT", "FB", "DJ", "TJ", "ZH"],
            "dimension_pattern": r"(?:基础|承台)\s*(\d+)\s*[×xX*]\s*(\d+)(?:[×xX*]\s*(\d+))?",
        },
        "钢筋": {
            "keywords": ["钢筋", "Φ", "φ", "配筋", "箍筋", "纵筋", "拉筋",
                        "HRB", "HPB", "CRB"],
            "rebar_pattern": r"[Φφ]\s*(\d{1,2})\s*(?:@\s*(\d{2,3}))?",
        },
    }

    def __init__(self):
        self.components = defaultdict(list)

    def parse_page(self, text: str, page_num: int = 0) -> List[dict]:
        """
        解析单页OCR文本，按构件分类

        :param text: OCR识别的文本
        :param page_num: 页码
        :return: [{type, name, dimensions, page, raw_text}, ...]
        """
        results = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if len(line) < 3:
                continue

            component_type = self._classify_line(line)
            if not component_type:
                continue

            # 提取尺寸信息
            dims = self._extract_dimensions(line, component_type)

            results.append({
                "type": component_type,
                "name": self._extract_name(line, component_type),
                "dimensions": dims,
                "page": page_num,
                "raw_text": line,
            })

            self.components[component_type].append(results[-1])

        return results

    def _classify_line(self, text: str) -> Optional[str]:
        """根据关键词识别构件类型"""
        text_upper = text.upper()

        # 按优先级匹配（钢筋容易误匹配，降低优先级）
        priority_order = ["梁", "板", "柱", "墙", "基础", "钢筋"]

        for comp_type in priority_order:
            patterns = self.COMPONENT_PATTERNS[comp_type]
            for kw in patterns["keywords"]:
                if kw.upper() in text_upper:
                    # 排除常见误匹配
                    if self._is_false_match(text, comp_type, kw):
                        continue
                    return comp_type

        return None

    def _is_false_match(self, text: str, comp_type: str, keyword: str) -> bool:
        """排除常见误匹配"""
        # 钢筋符号Φ/φ 容易在混凝土构件名中被识别，但钢筋行以Φ开头
        if comp_type == "钢筋" and len(keyword) <= 2:
            # 查看是否更像是混凝土构件
            for concrete_kw in ["梁", "板", "柱", "墙", "基础"]:
                if concrete_kw in text:
                    return True
        return False

    def _extract_name(self, text: str, comp_type: str) -> str:
        """提取构件名称/编号"""
        patterns = self.COMPONENT_PATTERNS[comp_type]

        # 尝试匹配: KL1, KZ2, Q3 等编号格式
        for kw in patterns["keywords"]:
            if len(kw) >= 2 and kw.upper() in text.upper():
                name_match = re.search(rf"{re.escape(kw)}\s*(\d+)", text, re.IGNORECASE)
                if name_match:
                    return f"{kw}{name_match.group(1)}"

        # 返回前20字符作为名称
        return text[:20]

    def _extract_dimensions(self, text: str, comp_type: str) -> dict:
        """提取构件尺寸"""
        dims = {}
        patterns = self.COMPONENT_PATTERNS[comp_type]

        if comp_type in ("梁", "柱") and "section_pattern" in patterns:
            sec_match = re.search(patterns["section_pattern"], text)
            if sec_match:
                dims["width"] = int(sec_match.group(1))
                dims["height"] = int(sec_match.group(2))

        if comp_type in ("板", "墙") and "thickness_pattern" in patterns:
            thick_match = re.search(patterns["thickness_pattern"], text)
            if thick_match:
                dims["thickness"] = int(thick_match.group(1))

        if comp_type == "钢筋" and "rebar_pattern" in patterns:
            rebar_match = re.search(patterns["rebar_pattern"], text)
            if rebar_match:
                dims["diameter"] = int(rebar_match.group(1))
                if rebar_match.group(2):
                    dims["spacing"] = int(rebar_match.group(2))

        # 通用截面尺寸
        if not dims:
            dim_match = re.search(r"(\d{2,4})\s*[×xX*]\s*(\d{2,4})", text)
            if dim_match:
                dims["width"] = int(dim_match.group(1))
                dims["height"] = int(dim_match.group(2))

        # 长度
        len_match = re.search(r"[L长][=＝:：]\s*(\d{3,6})", text)
        if len_match:
            dims["length"] = int(len_match.group(1))

        return dims

    def parse_all_pages(self, pages: List[dict]) -> dict:
        """
        解析多页结果

        :param pages: OCREngine.extract_text_from_pdf 的输出
        :return: {component_type: [items]}
        """
        self.components.clear()
        for page_data in pages:
            self.parse_page(page_data["text"], page_data.get("page", 0))
        return dict(self.components)

    def summary(self) -> dict:
        """生成分类汇总"""
        return {
            comp_type: {
                "count": len(items),
                "items": items,
            }
            for comp_type, items in self.components.items()
        }

    def get_by_type(self, comp_type: str) -> List[dict]:
        """获取指定类型的构件"""
        return self.components.get(comp_type, [])
