#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼎梁筑智能造价工作台 — 主入口
三层架构：图纸OCR → 定额组价 → 清单审核
"""

import os
import sys
import logging
from pathlib import Path

# 确保项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from shared.utils import load_yaml_config, ensure_dir, batch_files
from shared.excel_io import read_boq_from_excel, write_boq_sheet
from shared.models import BOQSheet, create_empty_boq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("鼎梁筑")


def banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════╗
║        鼎梁筑智能造价工作台  v1.0                  ║
║        图纸→OCR→定额→组价→报价  全链路自动化       ║
║        新疆2024定额 │ 乌鲁木齐 │ 130元/工日        ║
╚══════════════════════════════════════════════════╝
    """)


def menu():
    """主菜单"""
    banner()
    while True:
        print("""
┌──────────────────────────────────────────────┐
│ 1. 图纸OCR → 工程量提取                        │
│ 2. 工程量清单 → 定额组价报价                     │
│ 3. 图纸 vs 清单 → 差异核验                      │
│ 4. 一键全流程（图纸 → 报价）                     │
│ 5. 查看定额库摘要                               │
│ 0. 退出                                        │
└──────────────────────────────────────────────┘
        """)
        choice = input("请选择 [0-5]: ").strip()

        if choice == "1":
            cmd_ocr_extract()
        elif choice == "2":
            cmd_pricing()
        elif choice == "3":
            cmd_audit()
        elif choice == "4":
            cmd_full_pipeline()
        elif choice == "5":
            cmd_quota_summary()
        elif choice == "0":
            print("再见。老高，活干完了。")
            break
        else:
            print("无效选择")


def cmd_ocr_extract():
    """命令1: 图纸OCR → 工程量提取"""
    print("\n=== 图纸OCR工程量提取 ===")
    pdf_dir = input("图纸PDF目录 (默认 ./input/): ").strip() or "./input/"
    output = input("输出Excel路径 (默认 ./output/图纸工程量提取.xlsx): ").strip() or "./output/图纸工程量提取.xlsx"

    if not os.path.exists(pdf_dir):
        print(f"目录不存在: {pdf_dir}")
        return

    # 延迟导入，避免加载PaddleOCR
    from layer1_ocr.ocr_engine import OCREngine, check_ocr_available
    from layer1_ocr.dimension_extractor import DimensionExtractor

    avail = check_ocr_available()
    print(f"OCR引擎状态: pdfplumber={avail['pdfplumber']}, PaddleOCR={avail['paddleocr']}")

    if not avail['pdfplumber']:
        print("请安装: pip install pdfplumber --break-system-packages")
        return

    engine = OCREngine(use_paddle=avail['paddleocr'])
    extractor = DimensionExtractor()

    pdfs = batch_files(pdf_dir, ".pdf")
    if not pdfs:
        print(f"目录下无PDF文件: {pdf_dir}")
        return

    print(f"发现 {len(pdfs)} 个PDF文件")

    all_dims = []
    for i, pdf_path in enumerate(pdfs):
        print(f"\n处理 ({i+1}/{len(pdfs)}): {os.path.basename(pdf_path)}")
        pages = engine.extract_text_from_pdf(pdf_path)
        if pages:
            dims = extractor.extract_from_pages(pages)
            all_dims.extend(dims)
            print(f"  提取页面: {len(pages)}, 尺寸: {len(dims)}")

    ensure_dir(os.path.dirname(output))
    extractor.export_excel(output)
    print(f"\n工程量提取完成: {output} ({len(all_dims)} 条)")

    # 打印分类汇总
    groups = extractor.group_by_category()
    print("\n分类汇总:")
    for cat, items in groups.items():
        total_qty = sum(d.quantity for d in items if d.quantity > 0)
        print(f"  {cat}: {len(items)}项, 工程量合计={total_qty:.2f}")


def cmd_pricing():
    """命令2: 工程量清单 → 定额组价报价"""
    print("\n=== 清单定额组价 ===")

    excel_path = input("工程量清单Excel路径: ").strip()
    if not os.path.exists(excel_path):
        print(f"文件不存在: {excel_path}")
        return

    region = input("地区[乌鲁木齐/伊犁/喀什] (默认 乌鲁木齐): ").strip() or "乌鲁木齐"
    output = input("输出报价表路径 (默认 ./output/含单价报价表.xlsx): ").strip() or "./output/含单价报价表.xlsx"

    from layer2_pricing.quota_matcher import QuotaMatcher
    from layer2_pricing.price_calculator import PriceCalculator

    # 读入清单
    items = read_boq_from_excel(excel_path)
    print(f"读入清单: {len(items)} 项")

    # 匹配定额
    matcher = QuotaMatcher()
    matcher.match_batch(items)
    matched = sum(1 for i in items if i.matched_quota)
    print(f"定额匹配: {matched}/{len(items)}")

    # 计算价格
    calc = PriceCalculator(region=region)
    sheet = BOQSheet(
        project_name=os.path.basename(excel_path).replace(".xlsx", ""),
        sheet_name="清单报价",
        items=items,
    )
    calc.calc_sheet(sheet, matcher.database)

    # 输出
    ensure_dir(os.path.dirname(output))
    write_boq_sheet(output, sheet)
    calc.export_cost_summary(
        output.replace(".xlsx", "_汇总.xlsx"), sheet
    )

    # 打印汇总
    result = calc.calc_total_with_fees(sheet)
    print(f"\n{'='*50}")
    print(f"含税总造价: ¥{result['含税总造价']:,.2f}")
    print(f"分部分项: ¥{result['分部分项合计']:,.2f}")
    print(f"人工费: ¥{result['其中人工费']:,.2f}")
    print(f"材料费: ¥{result['其中材料费']:,.2f}")
    print(f"机械费: ¥{result['其中机械费']:,.2f}")
    print(f"{'='*50}")
    print(f"报价表: {output}")


def cmd_audit():
    """命令3: 图纸vs清单 → 差异核验"""
    print("\n=== 图纸工程量 vs 清单量 核验 ===")

    drawing_excel = input("图纸工程量Excel路径: ").strip()
    boq_excel = input("清单Excel路径: ").strip()
    output = input("输出差异报告路径 (默认 ./output/差异核验报告.xlsx): ").strip() or "./output/差异核验报告.xlsx"

    if not os.path.exists(drawing_excel) or not os.path.exists(boq_excel):
        print("文件不存在")
        return

    from shared.excel_io import read_excel
    from layer3_audit.boq_checker import BOQChecker
    from layer3_audit.diff_report import generate_diff_report, generate_markdown_report

    # 读入数据
    drawing_data = read_excel(drawing_excel)
    boq_items = read_boq_from_excel(boq_excel)

    print(f"图纸工程量: {len(drawing_data)} 项")
    print(f"清单项: {len(boq_items)} 项")

    # 比对
    checker = BOQChecker()
    diffs = checker.compare(drawing_data, boq_items)

    # 摘要
    summary = checker.generate_summary(diffs)
    print(f"\n比对结果:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # 输出
    ensure_dir(os.path.dirname(output))
    generate_diff_report(diffs, "图纸vs清单核验", output)
    generate_markdown_report(diffs, "图纸vs清单核验",
                            output.replace(".xlsx", ".md"))
    print(f"\n差异报告: {output}")


def cmd_full_pipeline():
    """命令4: 一键全流程"""
    print("\n=== 一键全流程（图纸 → 报价）===")
    print("⚠ 此功能需PaddleOCR支持，将依次执行:")
    print("  1. OCR提取工程量")
    print("  2. 定额匹配组价")
    print("  3. 输出报价表")

    pdf_dir = input("图纸PDF目录: ").strip()
    output_dir = input("输出目录 (默认 ./output/): ").strip() or "./output/"
    project_name = input("项目名称: ").strip() or "未命名项目"
    region = input("地区[乌鲁木齐/伊犁/喀什] (默认 乌鲁木齐): ").strip() or "乌鲁木齐"

    ensure_dir(output_dir)

    # Step 1: OCR
    print("\n[1/3] OCR工程量提取...")
    from layer1_ocr.ocr_engine import OCREngine, check_ocr_available
    from layer1_ocr.dimension_extractor import DimensionExtractor

    avail = check_ocr_available()
    engine = OCREngine(use_paddle=avail['paddleocr'])
    extractor = DimensionExtractor()

    pdfs = batch_files(pdf_dir, ".pdf")
    if not pdfs:
        print("目录下无PDF文件")
        return

    for pdf_path in pdfs:
        pages = engine.extract_text_from_pdf(pdf_path)
        if pages:
            extractor.extract_from_pages(pages)

    ocr_excel = os.path.join(output_dir, "图纸工程量提取.xlsx")
    extractor.export_excel(ocr_excel)
    print(f"OCR提取: {len(extractor.results)} 项 → {ocr_excel}")

    # Step 2: 组价（需要清单Excel）
    print("\n[2/3] 定额组价...")
    boq_excel = input("请输入清单Excel路径（组价用）: ").strip()
    if not os.path.exists(boq_excel):
        print("跳过组价（无清单文件）")
        return

    from layer2_pricing.quota_matcher import QuotaMatcher
    from layer2_pricing.price_calculator import PriceCalculator

    items = read_boq_from_excel(boq_excel)
    matcher = QuotaMatcher()
    matcher.match_batch(items)

    calc = PriceCalculator(region=region)
    sheet = BOQSheet(project_name=project_name, items=items)
    calc.calc_sheet(sheet, matcher.database)

    quote_excel = os.path.join(output_dir, "含单价报价表.xlsx")
    write_boq_sheet(quote_excel, sheet)
    calc.export_cost_summary(
        os.path.join(output_dir, "造价汇总.xlsx"), sheet
    )

    # Step 3: 核验（可选）
    print("\n[3/3] 差异核验...")
    print(f"核验需对比OCR结果与清单，可稍后手动执行命令3")

    result = calc.calc_total_with_fees(sheet)
    print(f"\n{'='*50}")
    print(f"全流程完成!")
    print(f"含税总造价: ¥{result['含税总造价']:,.2f}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*50}")


def cmd_quota_summary():
    """命令5: 查看定额库摘要"""
    from layer2_pricing.quota_matcher import QuotaMatcher
    matcher = QuotaMatcher()
    summary = matcher.summary
    print(f"\n定额库版本: {summary['version']}")
    print(f"总子目数: {summary['total']}")
    print("\n分类统计:")
    for cat, count in sorted(summary['categories'].items()):
        print(f"  {cat}: {count} 条")


if __name__ == "__main__":
    menu()
