---
tags: [项目, 索引]
created: 2026-06-12
type: reference
---

# 鼎梁筑智能造价工作台 v1.0

> 图纸 → OCR识别 → 工程量提取 → 定额匹配 → 组价 → 报价表输出  
> 新疆2024市政定额 │ 乌鲁木齐130元/工日 │ 管理28%│利润18%│规费22%│税9%

---

## 快速开始

```bash
cd D:\知识库\造价工作台
pip install -r requirements.txt --break-system-packages
python main.py
```

## 目录结构

```
造价工作台/
├── main.py                    # 主入口(命令行菜单)
├── config.yaml                # 配置文件
├── requirements.txt
├── layer1_ocr/                # 图层1: 图纸OCR识别
│   ├── ocr_engine.py          # PaddleOCR/pdfplumber封装
│   ├── drawing_parser.py      # 图纸结构识别(梁板柱墙)
│   └── dimension_extractor.py # 尺寸标注提取+工程量计算
├── layer2_pricing/            # 图层2: 定额组价
│   ├── quota_matcher.py       # 定额智能匹配
│   ├── price_calculator.py    # 综合单价+取费计算
│   └── quota_db/
│       └── xinjiang_2024.json # 新疆2024定额库(34子目/8大类)
├── layer3_audit/              # 图层3: 清单审核
│   ├── boq_checker.py         # 图纸量vs清单量比对
│   └── diff_report.py         # 差异报告生成(Excel+MD)
├── shared/                    # 公共模块
│   ├── models.py              # 数据模型(BOQItem/QuotaItem/FeeConfig)
│   ├── excel_io.py            # Excel读写
│   └── utils.py               # 工具函数
└── xj_cost_crawler/           # 爬虫子工程(新疆造价信息自动采集)
    ├── main.py                # 爬虫主入口
    ├── config.yaml            # 爬虫配置
    ├── crawler/               # 4个站点爬虫
    ├── storage/db.py          # SQLite数据库(5张表)
    └── notify/change_alert.py # 变更告警
```

## 五大操作命令

| 命令 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 1. 图纸OCR | PDF图纸→工程量提取 | PDF/图片 | 图纸工程量提取.xlsx |
| 2. 清单组价 | 工程量→定额匹配→报价 | Excel清单 | 含单价报价表.xlsx |
| 3. 差异核验 | 图纸量vs清单量比对 | OCR结果+清单 | 差异核验报告.xlsx |
| 4. 一键全流程 | OCR→组价→核验(全自动) | PDF目录 | 完整报价表 |
| 5. 定额库摘要 | 查看已加载定额 | - | 分类统计 |

## 计价参数

| 项目 | 参数 |
|------|------|
| 定额 | 新疆2024市政消耗量定额 |
| 乌鲁木齐 | 一类130元/工日 |
| 伊犁 | 一类130元/工日 |
| 喀什 | 一类147元/工日 (高海拔×1.10) |
| 管理费 | 28% (基数:人工+机械) |
| 利润 | 18% (基数:人工+机械) |
| 规费 | 22% (基数:人工费) |
| 增值税 | 9% |

## 爬虫系统

```bash
cd xj_cost_crawler
pip install -r requirements.txt --break-system-packages
python main.py
```

定时运行建议配置Windows任务计划或Cowork scheduled task，每日08:00执行。

## 已知限制

1. **OCR依赖PaddleOCR**: 安装体积较大(约500MB)，不安装时仅支持文本型PDF
2. **定额库不完整**: 当前34个常用子目，完整版需从PDF提取更多子目
3. **单位换算**: 定额单位(10m³/100m²)与清单单位(m³/m²)需进一步细化换算表
4. **爬虫网络限制**: VM环境可能无法访问部分政府网站

## 技术栈

Python 3.10+ │ openpyxl │ PaddleOCR │ pdfplumber │ requests │ BeautifulSoup │ SQLite

---

*鼎梁筑 · 老高 · 2026-06-10*
