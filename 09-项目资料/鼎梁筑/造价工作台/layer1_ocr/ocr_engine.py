#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 1 — OCR引擎封装
支持: PDF拆页转图片 + OCR识别
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# 动态检测可用OCR引擎
HAS_PADDLEOCR = False
HAS_PDF2IMAGE = False
HAS_PDFPLUMBER = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    logger.warning("pdfplumber 未安装，PDF文本提取功能受限")

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    logger.warning("pdf2image 未安装，PDF转图片功能不可用")

# PaddleOCR 加载较重，延迟导入
OCR_INSTANCE = None


def _get_paddleocr():
    """延迟加载PaddleOCR"""
    global OCR_INSTANCE, HAS_PADDLEOCR
    if OCR_INSTANCE is not None:
        return OCR_INSTANCE
    try:
        from paddleocr import PaddleOCR
        OCR_INSTANCE = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
        HAS_PADDLEOCR = True
        logger.info("PaddleOCR 初始化成功")
    except ImportError:
        HAS_PADDLEOCR = False
        logger.warning("PaddleOCR 未安装，OCR功能不可用。安装: pip install paddlepaddle paddleocr")
        OCR_INSTANCE = None
    return OCR_INSTANCE


class OCREngine:
    """OCR引擎统一接口"""

    def __init__(self, use_paddle: bool = True, use_plumber: bool = True):
        """
        :param use_paddle: 是否使用PaddleOCR(图片型PDF)
        :param use_plumber: 是否使用pdfplumber(文本型PDF优先)
        """
        self.use_paddle = use_paddle
        self.use_plumber = use_plumber

    def extract_text_from_pdf(self, pdf_path: str, dpi: int = 300) -> List[dict]:
        """
        PDF → 文本提取
        策略: pdfplumber优先(文本型), 失败则降级到PaddleOCR(图片型)

        :param pdf_path: PDF文件路径
        :param dpi: 图片转换DPI
        :return: [{page, text, method}, ...]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"文件不存在: {pdf_path}")

        results = []

        # 策略1: pdfplumber (文本型PDF)
        if self.use_plumber and HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and len(text.strip()) > 20:
                            results.append({
                                "page": i + 1,
                                "text": text,
                                "method": "pdfplumber",
                            })
                if results:
                    logger.info(f"pdfplumber提取 {len(results)} 页文本: {pdf_path}")
                    return results
            except Exception as e:
                logger.warning(f"pdfplumber提取失败: {e}")

        # 策略2: PaddleOCR (图片型PDF/扫描件)
        if self.use_paddle and HAS_PDF2IMAGE:
            try:
                ocr = _get_paddleocr()
                if ocr is None:
                    logger.error("PaddleOCR不可用")
                    return results

                images = convert_from_path(pdf_path, dpi=dpi)
                logger.info(f"PDF转图片: {len(images)} 页, DPI={dpi}")

                for i, img in enumerate(images):
                    img_path = f"/tmp/page_{i}.png"
                    img.save(img_path, "PNG")

                    ocr_result = ocr.ocr(img_path, cls=True)
                    lines = []
                    if ocr_result and ocr_result[0]:
                        for line in ocr_result[0]:
                            text = line[1][0]
                            confidence = line[1][1]
                            lines.append(text)

                    full_text = "\n".join(lines)
                    if full_text.strip():
                        results.append({
                            "page": i + 1,
                            "text": full_text,
                            "method": "PaddleOCR",
                        })

                    # 清理临时文件
                    try:
                        os.remove(img_path)
                    except OSError:
                        pass

                logger.info(f"PaddleOCR提取 {len(results)} 页文本: {pdf_path}")
                return results

            except ImportError:
                logger.error("pdf2image 未安装，无法处理图片型PDF")
            except Exception as e:
                logger.error(f"PaddleOCR处理失败: {e}")

        # 策略3: pdfplumber 逐页但无文本
        if not results and HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        results.append({
                            "page": i + 1,
                            "text": text,
                            "method": "pdfplumber(minimal)",
                        })
            except Exception:
                pass

        if not results:
            logger.warning(f"未能提取任何文本: {pdf_path}")

        return results

    def extract_text_from_image(self, image_path: str) -> str:
        """
        单图片OCR识别
        """
        ocr = _get_paddleocr()
        if ocr is None:
            logger.error("PaddleOCR不可用")
            return ""

        try:
            result = ocr.ocr(image_path, cls=True)
            lines = []
            if result and result[0]:
                for line in result[0]:
                    lines.append(line[1][0])
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"图片OCR失败: {e}")
            return ""

    def batch_process(self, directory: str, output_dir: str = None) -> dict:
        """
        批量处理文件夹下所有PDF/图片

        :param directory: 输入目录
        :param output_dir: 输出目录(None=不保存文本)
        :return: {filename: [page_results], ...}
        """
        from shared.utils import batch_files, ensure_dir

        all_results = {}
        pdfs = batch_files(directory, ".pdf")
        pngs = batch_files(directory, ".png")
        jpgs = batch_files(directory, ".jpg") + batch_files(directory, ".jpeg")

        total = len(pdfs) + len(pngs) + len(jpgs)
        logger.info(f"批量处理: {total} 个文件")

        for i, pdf_path in enumerate(pdfs):
            try:
                pages = self.extract_text_from_pdf(pdf_path)
                all_results[os.path.basename(pdf_path)] = pages
                from shared.utils import progress_bar
                progress_bar(i + 1, total, "OCR进度")
            except Exception as e:
                logger.error(f"处理失败 {pdf_path}: {e}")
                all_results[os.path.basename(pdf_path)] = []

        for img_path in pngs + jpgs:
            try:
                text = self.extract_text_from_image(img_path)
                all_results[os.path.basename(img_path)] = [{
                    "page": 1, "text": text, "method": "PaddleOCR"
                }]
            except Exception as e:
                logger.error(f"处理失败 {img_path}: {e}")

        # 保存文本输出
        if output_dir:
            ensure_dir(output_dir)
            for filename, pages in all_results.items():
                txt_path = os.path.join(output_dir, f"{Path(filename).stem}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    for p in pages:
                        f.write(f"--- Page {p['page']} ---\n")
                        f.write(p["text"])
                        f.write("\n\n")

        return all_results


def check_ocr_available() -> dict:
    """检查OCR可用性"""
    return {
        "paddleocr": HAS_PADDLEOCR or _get_paddleocr() is not None,
        "pdfplumber": HAS_PDFPLUMBER,
        "pdf2image": HAS_PDF2IMAGE,
    }
