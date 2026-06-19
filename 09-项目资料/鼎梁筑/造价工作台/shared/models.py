#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼎梁筑造价工作台 — 数据模型定义
涵盖: BOQ清单项、定额子目、人材机拆分、取费结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# ============ 枚举定义 ============

class CategoryType(Enum):
    """构件类型"""
    BEAM = "梁"
    SLAB = "板"
    COLUMN = "柱"
    WALL = "墙"
    FOUNDATION = "基础"
    REBAR = "钢筋"
    OTHER = "其他"


class CostType(Enum):
    """费用类型（四维拆解）"""
    LABOR = "人工费"
    AUX_MATERIAL = "辅材费"
    MAIN_MATERIAL = "主材费"
    MACHINERY = "机械费"


class RiskLevel(Enum):
    """风险等级"""
    RED = "🔴红线"
    YELLOW = "🟡黄线"
    BLUE = "🔵蓝线"


class Region(Enum):
    """地区"""
    URUMQI = ("乌鲁木齐", 130.0)
    YILI = ("伊犁", 130.0)
    KASHI = ("喀什", 147.0)
    SHIHEZI = ("石河子", 114.0)
    AKESU = ("阿克苏", 125.0)
    CHANGJI = ("昌吉", 128.0)

    @property
    def labor_rate(self) -> float:
        return self.value[1]

    @property
    def name(self) -> str:
        return self.value[0]


# ============ 定额数据模型 ============

@dataclass
class QuotaItem:
    """定额子目"""
    quota_code: str                              # 定额编号 如 "1-1-1"
    quota_name: str                              # 定额名称
    unit: str                                    # 单位
    category: str                                # 分类: 混凝土/钢筋/砌体/模板/装饰
    labor_qty: float = 0.0                       # 人工消耗量(工日/单位)
    labor_cost: float = 0.0                      # 人工费
    main_material_cost: float = 0.0              # 主材费
    aux_material_cost: float = 0.0               # 辅材费
    machinery_cost: float = 0.0                  # 机械费
    base_price: float = 0.0                      # 基价(人+材+机)
    material_list: List[Dict] = field(default_factory=list)  # 材料明细
    machinery_list: List[Dict] = field(default_factory=list)  # 机械明细

    def to_dict(self) -> dict:
        return {
            "quota_code": self.quota_code,
            "quota_name": self.quota_name,
            "unit": self.unit,
            "category": self.category,
            "labor_qty": self.labor_qty,
            "labor_cost": self.labor_cost,
            "main_material_cost": self.main_material_cost,
            "aux_material_cost": self.aux_material_cost,
            "machinery_cost": self.machinery_cost,
            "base_price": self.base_price,
            "material_list": self.material_list,
            "machinery_list": self.machinery_list,
        }


@dataclass
class QuotaDatabase:
    """定额数据库"""
    version: str = "新疆2024"
    region: str = "乌鲁木齐"
    items: List[QuotaItem] = field(default_factory=list)
    by_code: Dict[str, QuotaItem] = field(default_factory=dict)

    def add(self, item: QuotaItem):
        self.items.append(item)
        self.by_code[item.quota_code] = item

    def get(self, code: str) -> Optional[QuotaItem]:
        return self.by_code.get(code)

    def search(self, keyword: str) -> List[QuotaItem]:
        """按关键词模糊搜索定额子目"""
        keyword = keyword.lower()
        return [item for item in self.items
                if keyword in item.quota_name.lower()
                or keyword in item.category.lower()]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "region": self.region,
            "items": [item.to_dict() for item in self.items],
        }


# ============ BOQ清单模型 ============

@dataclass
class BOQItem:
    """工程量清单项 (GB50500-2013)"""
    code: str                                    # 清单编码 12位
    name: str                                    # 项目名称
    feature: str = ""                            # 项目特征描述
    unit: str = ""                               # 计量单位
    quantity: float = 0.0                        # 工程量
    unit_price: float = 0.0                      # 综合单价
    total_price: float = 0.0                     # 合价
    # 人材机拆分
    labor_cost: float = 0.0                      # 人工费
    material_cost: float = 0.0                   # 材料费(含主材+辅材)
    machinery_cost: float = 0.0                  # 机械费
    management_fee: float = 0.0                  # 管理费
    profit: float = 0.0                          # 利润
    # 定额匹配
    matched_quota: Optional[str] = None           # 匹配到的定额编号
    match_confidence: float = 0.0                # 匹配置信度

    def to_row(self) -> list:
        """输出为Excel行"""
        return [
            self.code, self.name, self.feature, self.unit,
            self.quantity, self.unit_price, self.total_price,
            self.labor_cost, self.material_cost, self.machinery_cost,
            self.management_fee, self.profit,
            self.matched_quota or "", self.match_confidence,
        ]

    @property
    def cost_breakdown(self) -> Dict[str, float]:
        """四维成本拆解"""
        return {
            "人工费": self.labor_cost,
            "材料费": self.material_cost,
            "机械费": self.machinery_cost,
            "管理费": self.management_fee,
            "利润": self.profit,
        }

    def check_deviation(self, reference_price: float) -> Optional[tuple]:
        """检查综合单价偏差，返回(偏差率, 风险等级)"""
        if reference_price == 0:
            return None
        deviation = (self.unit_price - reference_price) / reference_price
        abs_dev = abs(deviation)
        if abs_dev <= 0.05:
            level = None  # 正常
        elif abs_dev <= 0.15:
            level = RiskLevel.YELLOW
        else:
            level = RiskLevel.RED
        return (round(deviation * 100, 1), level)


@dataclass
class BOQSheet:
    """工程量清单表"""
    project_name: str
    sheet_name: str
    items: List[BOQItem] = field(default_factory=list)
    # 汇总
    total_labor: float = 0.0
    total_material: float = 0.0
    total_machinery: float = 0.0
    total_management: float = 0.0
    total_profit: float = 0.0
    total_amount: float = 0.0

    def recalc(self):
        """重新计算汇总"""
        self.total_labor = sum(i.labor_cost for i in self.items)
        self.total_material = sum(i.material_cost for i in self.items)
        self.total_machinery = sum(i.machinery_cost for i in self.items)
        self.total_management = sum(i.management_fee for i in self.items)
        self.total_profit = sum(i.profit for i in self.items)
        self.total_amount = sum(i.total_price for i in self.items)


# ============ 取费配置 ============

@dataclass
class FeeConfig:
    """取费费率配置"""
    management_rate: float = 0.28      # 管理费 28%
    profit_rate: float = 0.18          # 利润 18%
    regulation_rate: float = 0.22      # 规费 22%
    vat_rate: float = 0.09             # 增值税 9%
    measure_rate: float = 0.045        # 措施费 ≈4.5%
    safety_rate: float = 0.025         # 安全文明施工费 ≈2.5%

    # 取费基数
    management_base: str = "人工+机械"  # 管理费取费基数
    profit_base: str = "人工+机械"      # 利润取费基数
    regulation_base: str = "人工费"     # 规费取费基数

    def calc_management(self, labor: float, machinery: float) -> float:
        return (labor + machinery) * self.management_rate

    def calc_profit(self, labor: float, machinery: float) -> float:
        return (labor + machinery) * self.profit_rate

    def calc_regulation(self, labor: float) -> float:
        return labor * self.regulation_rate

    def calc_vat(self, pre_tax: float) -> float:
        return pre_tax * self.vat_rate


# ============ OCR结果模型 ============

@dataclass
class DimensionResult:
    """尺寸识别结果"""
    text: str                                    # 原始文本
    width: float = 0.0                           # 宽(mm)
    height: float = 0.0                          # 高(mm)
    length: float = 0.0                          # 长(mm)
    concrete_grade: str = ""                     # 混凝土标号 C30/C35
    rebar_spec: str = ""                         # 钢筋规格 Φ12@150
    category: CategoryType = CategoryType.OTHER  # 构件类型
    unit: str = ""                               # 单位
    quantity: float = 0.0                        # 工程量
    page: int = 0                                # 所在页码
    confidence: float = 0.0                      # OCR置信度


@dataclass
class DrawingParseResult:
    """图纸解析结果"""
    file_name: str
    total_pages: int = 0
    dimensions: List[DimensionResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ============ 差异核验模型 ============

@dataclass
class DiffRecord:
    """差异记录"""
    code: str
    name: str
    drawing_qty: float       # 图纸量
    boq_qty: float           # 清单量
    deviation: float         # 偏差率 (%)
    deviation_type: str      # 漏项/多算/偏差
    risk_level: RiskLevel    # 风险等级
    remark: str = ""


# ============ 采集数据模型 ============

@dataclass
class CrawlResult:
    """爬虫采集结果"""
    source: str
    found: int
    saved: int
    status: str   # success/fail/partial
    error_msg: str = ""
    items: List[Dict] = field(default_factory=list)


# ============ 工厂函数 ============

def create_fee_config(region: Region = Region.URUMQI) -> FeeConfig:
    """创建取费配置"""
    config = FeeConfig()
    # 喀什高海拔特殊调整
    if region == Region.KASHI:
        config.management_rate = 0.30   # 高海拔+2%
    return config


def create_empty_boq(project_name: str, sheet_name: str = "清单") -> BOQSheet:
    """创建空工程量清单"""
    return BOQSheet(project_name=project_name, sheet_name=sheet_name)
