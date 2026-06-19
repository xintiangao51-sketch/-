#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 2 — 定额自动匹配
功能: 根据项目特征关键词 → 匹配新疆2024定额子目
"""

import os
import json
import re
import logging
from typing import List, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

try:
    from shared.models import QuotaItem, QuotaDatabase, BOQItem
    from shared.utils import load_json
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from shared.models import QuotaItem, QuotaDatabase, BOQItem
    from shared.utils import load_json


class QuotaMatcher:
    """定额子目智能匹配器"""

    # 项目特征 → 定额类别 关键词映射
    FEATURE_TO_CATEGORY = {
        # 混凝土工程
        "垫层": ["混凝土", "垫层"],
        "混凝土": ["混凝土"],
        "现浇": ["混凝土"],
        "C15": ["混凝土"],
        "C20": ["混凝土"],
        "C25": ["混凝土"],
        "C30": ["混凝土"],
        "C35": ["混凝土"],
        "C40": ["混凝土"],
        "楼梯": ["混凝土", "楼梯"],
        # 钢筋工程
        "钢筋": ["钢筋"],
        "HPB": ["钢筋"],
        "HRB": ["钢筋"],
        "Φ": ["钢筋"],
        "箍筋": ["钢筋"],
        # 砌体工程
        "砖": ["砌体"],
        "砌块": ["砌体"],
        "砌体": ["砌体"],
        "加气": ["砌体"],
        # 模板工程
        "模板": ["模板"],
        # 装饰工程
        "抹灰": ["装饰"],
        "瓷砖": ["装饰"],
        "涂料": ["装饰"],
        "贴砖": ["装饰"],
        # 土石方
        "挖土": ["土石方"],
        "回填": ["土石方"],
        "土方": ["土石方"],
        # 防水
        "防水": ["防水"],
        "SBS": ["防水"],
        # 桩基
        "桩": ["桩基"],
        "灌注桩": ["桩基"],
        # 钢结构
        "钢柱": ["金属"],
        "钢梁": ["金属"],
        "钢结构": ["金属"],
    }

    def __init__(self, quota_db_path: str = None):
        """
        :param quota_db_path: 定额数据库JSON路径
        """
        if quota_db_path is None:
            quota_db_path = os.path.join(
                os.path.dirname(__file__), "quota_db", "xinjiang_2024.json"
            )

        self.db_path = quota_db_path
        self.database = QuotaDatabase()
        self._load()

    def _load(self):
        """加载定额数据库"""
        try:
            data = load_json(self.db_path)
            meta = data.get("_meta", {})
            self.database.version = meta.get("version", "未知")
            self.database.region = meta.get("region", "乌鲁木齐")

            for item_data in data.get("items", []):
                item = QuotaItem(
                    quota_code=item_data["quota_code"],
                    quota_name=item_data["quota_name"],
                    unit=item_data["unit"],
                    category=item_data.get("category", ""),
                    labor_qty=item_data.get("labor_qty", 0),
                    labor_cost=item_data.get("labor_cost", 0),
                    main_material_cost=item_data.get("main_material_cost", 0),
                    aux_material_cost=item_data.get("aux_material_cost", 0),
                    machinery_cost=item_data.get("machinery_cost", 0),
                    base_price=item_data.get("base_price", 0),
                )
                # 保存关键词用于后续匹配
                item.material_list = item_data.get("keywords", [])
                self.database.add(item)

            logger.info(f"定额数据库加载完成: {len(self.database.items)} 个子目")
        except FileNotFoundError:
            logger.warning(f"定额数据库不存在: {self.db_path}")
        except Exception as e:
            logger.error(f"加载定额数据库失败: {e}")

    def match_by_features(self, feature_text: str, category_hint: str = "") -> List[Tuple[QuotaItem, float]]:
        """
        根据项目特征描述匹配定额子目

        :param feature_text: 项目特征描述
        :param category_hint: 构件类型提示(梁/板/柱/墙)
        :return: [(QuotaItem, 置信度), ...] 按置信度降序
        """
        results = []
        feature_lower = feature_text.lower()

        # 第一步: 确定目标类别
        target_categories = set()
        for kw, cats in self.FEATURE_TO_CATEGORY.items():
            if kw.lower() in feature_lower:
                target_categories.update(cats)

        # 构件类型 → 明确类别
        if category_hint in ("梁", "板", "柱", "墙", "基础"):
            target_categories.add("混凝土")
            target_categories.add("模板")
        elif category_hint == "钢筋":
            target_categories.add("钢筋")

        if not target_categories:
            target_categories = {"混凝土"}  # 默认

        # 第二步: 在目标类别内匹配
        for item in self.database.items:
            if item.category not in target_categories:
                continue

            score = self._score_match(item, feature_text, category_hint)

            if score > 0.15:
                results.append((item, score))

        # 按置信度降序
        results.sort(key=lambda x: -x[1])
        return results

    def _score_match(self, item: QuotaItem, feature_text: str, category_hint: str = "") -> float:
        """
        计算匹配得分

        :return: 0-1 之间的得分
        """
        score = 0.0
        feature_lower = feature_text.lower()
        name_lower = item.quota_name.lower()

        # 1. 名称关键词直接匹配
        keywords = getattr(item, 'material_list', [])
        for kw in keywords:
            if kw.lower() in feature_lower:
                score += 0.3
                break  # 只加一次

        # 2. 定额名称与项目特征文本相似度
        sim = SequenceMatcher(None, name_lower[:30], feature_lower[:30]).ratio()
        score += sim * 0.3

        # 3. 构件类型匹配加分
        if category_hint:
            hint_lower = category_hint.lower()
            if hint_lower in name_lower:
                score += 0.3
            # 构件具体名称匹配
            if category_hint == "梁" and "梁" in item.quota_name:
                score += 0.15
            elif category_hint == "柱" and "柱" in item.quota_name:
                score += 0.15
            elif category_hint == "板" and "板" in item.quota_name:
                score += 0.15
            elif category_hint == "墙" and "墙" in item.quota_name:
                score += 0.15
            elif category_hint == "基础" and "基础" in item.quota_name:
                score += 0.15

        # 4. 混凝土标号精确匹配
        concrete_match = re.search(r"C(\d{2})", feature_text)
        if concrete_match:
            grade = f"C{concrete_match.group(1)}"
            if grade in item.quota_name:
                score += 0.2

        return min(score, 1.0)

    def match_boq_item(self, boq_item: BOQItem, category_hint: str = "") -> BOQItem:
        """
        为单个BOQ清单项匹配定额

        :param boq_item: 清单项
        :param category_hint: 构件类型提示
        :return: 更新后的BOQItem(含matched_quota和match_confidence)
        """
        # 合并名称+特征作为匹配文本
        match_text = f"{boq_item.name} {boq_item.feature}"

        # 从名称推测构件类型
        if not category_hint:
            from shared.utils import classify_component
            category_hint = classify_component(match_text)

        matches = self.match_by_features(match_text, category_hint)

        if matches:
            best_quota, confidence = matches[0]
            boq_item.matched_quota = best_quota.quota_code
            boq_item.match_confidence = round(confidence, 3)
        else:
            boq_item.matched_quota = None
            boq_item.match_confidence = 0.0

        return boq_item

    def match_batch(self, boq_items: List[BOQItem]) -> List[BOQItem]:
        """
        批量匹配清单项

        :return: 更新后的BOQItem列表
        """
        matched_count = 0
        total = len(boq_items)

        for i, item in enumerate(boq_items):
            self.match_boq_item(item)
            if item.matched_quota:
                matched_count += 1
            from shared.utils import progress_bar
            progress_bar(i + 1, total, "定额匹配")

        logger.info(f"匹配完成: {matched_count}/{total} ({(matched_count/total*100):.1f}%)")
        return boq_items

    def manual_override(self, boq_item: BOQItem, quota_code: str):
        """手动调整匹配结果"""
        quota = self.database.get(quota_code)
        if quota:
            boq_item.matched_quota = quota_code
            boq_item.match_confidence = 1.0  # 手动匹配置信度100%
            logger.info(f"手动调整: {boq_item.code} → {quota_code}")
        else:
            logger.warning(f"定额编号不存在: {quota_code}")

    def get_quota_detail(self, quota_code: str) -> Optional[QuotaItem]:
        """查询定额子目详情"""
        return self.database.get(quota_code)

    def list_categories(self) -> List[str]:
        """列出所有定额类别"""
        cats = set(item.category for item in self.database.items)
        return sorted(cats)

    @property
    def summary(self) -> dict:
        """定额库摘要"""
        cats = {}
        for item in self.database.items:
            cats.setdefault(item.category, 0)
            cats[item.category] += 1
        return {
            "version": self.database.version,
            "total": len(self.database.items),
            "categories": cats,
        }
