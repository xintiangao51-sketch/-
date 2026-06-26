---
tags: [AI/文档, 索引]
created: 2026-06-12
type: reference
---

# Cline 执行指令 06：定额PDF全量解析 + 数据库构建

> 执行前提：PDF文件已在 quota_db/ 目录下
> - 伊犁安装工程估价表：2.全统安装工程消耗量定额伊犁地区单位估价汇总表(2022）.pdf（790页，有文本层）
> - 市政定额第一~五册：2020版新疆维吾尔自治区市政工程消耗量定额一~五.pdf（扫描件，需OCR）
> - 还有其他估价表PDF待放入

---

## 一、伊犁安装工程估价表解析（优先级最高）

### 创建文件：`quota_db/parse_yili_pdf.py`

```python
#!/usr/bin/env python3
"""
伊犁地区安装工程单位估价表 PDF → JSON 解析器
数据源：790页文本层PDF，逐行解析定额数据
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger("parse_yili")


class YiliQuotaParser:
    """
    伊犁估价表解析器
    数据格式：每行为 序号 定额编号 项目名称 单位 基价 人工费 材料费 机械费
    """

    # 定额数据行正则：开头是数字序号+空格+定额编码
    DATA_LINE_PATTERN = re.compile(
        r'^(\d+)\s+'           # 序号
        r'(\d+-\d+-\d+)\s+'    # 定额编码 如 1-1-1
        r'(.+?)\s+([一-鿿\w]+)\s+'  # 项目名称 (到单位前)
        r'(\d+\.?\d*)\s+'      # 基价
        r'(\d+\.?\d*)\s+'      # 人工费
        r'(\d+\.?\d*)\s+'      # 材料费
        r'(\d+\.?\d*)\s*$'     # 机械费
    )

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.items: List[Dict] = []
        self.errors: List[str] = []
        self.chapters: List[Dict] = []

    def parse(self) -> List[Dict]:
        """解析全部PDF"""
        logger.info(f"打开PDF: {self.pdf_path.name}")
        with pdfplumber.open(str(self.pdf_path)) as pdf:
            total = len(pdf.pages)
            current_chapter = ""

            for i in range(total):
                page = pdf.pages[i]
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')

                for line in lines:
                    line = line.strip()

                    # 跳过空行和表头
                    if not line or line.startswith('序 号') or line.startswith('序号'):
                        continue

                    # 检测章节标题（短行、含"册"或"章"或"说明"）
                    if self._is_chapter_header(line):
                        current_chapter = line
                        logger.info(f"  第{i+1}页 章节: {current_chapter}")
                        continue

                    # 解析定额数据行
                    item = self._parse_data_line(line, i + 1, current_chapter)
                    if item:
                        self.items.append(item)

        logger.info(f"解析完成: {len(self.items)} 条定额, {len(self.errors)} 行未能解析")
        return self.items

    def _is_chapter_header(self, line: str) -> bool:
        """判断是否为章节标题"""
        keywords = ['册', '章', '说明', '总说明']
        has_keyword = any(kw in line for kw in keywords)
        is_short = len(line) < 40
        has_no_number = not re.search(r'\d+\.\d+', line)  # 不包含金额
        return has_keyword and is_short and has_no_number

    def _parse_data_line(
        self, line: str, page: int, chapter: str
    ) -> Optional[Dict]:
        """解析单行定额数据"""
        try:
            # 策略1：按空格分割数字字段
            # 格式：序号 定额号 名称... 单位 基价 人工费 材料费 机械费
            parts = line.split()
            if len(parts) < 7:
                return None

            seq = parts[0]
            code = parts[1]

            # 定额编码校验：必须包含 -
            if not re.match(r'\d+-\d+-\d+', code):
                return None

            # 最后4个数字是 基价/人工费/材料费/机械费
            numeric_parts = []
            name_parts = []

            for p in parts[2:]:
                try:
                    numeric_parts.append(float(p))
                except ValueError:
                    name_parts.append(p)

            if len(numeric_parts) < 4:
                # 可能名称不含数字或格式异常
                self.errors.append(f"页{page}: 数字字段不足4个 -> {line[:80]}")
                return None

            # 最后一个是机械费，倒数第二个材料费，倒数第三个人工费，倒数第四个基价
            machinery = numeric_parts[-1]
            material = numeric_parts[-2]
            labor = numeric_parts[-3]
            base_price = numeric_parts[-4]

            # 单位在名称后面，numeric_parts前面
            name_and_unit = parts[2:-4] if len(parts) > 6 else []
            unit = name_and_unit[-1] if name_and_unit else ""
            name = " ".join(name_and_unit[:-1]) if len(name_and_unit) > 1 else " ".join(name_and_unit)

            return {
                "seq": int(seq),
                "quota_code": code,
                "name": name.strip(),
                "unit": unit,
                "base_price": base_price,
                "labor_fee": labor,
                "material_fee": material,
                "machinery_fee": machinery,
                "page": page,
                "chapter": chapter,
                "region": "yili_2022",
            }

        except (ValueError, IndexError) as e:
            self.errors.append(f"页{page}: 解析异常 {e} -> {line[:80]}")
            return None

    def save_json(self, output_path: str) -> str:
        """保存为JSON"""
        output_data = {
            "_meta": {
                "name": "通用安装工程及新疆补充消耗量定额 2022年伊犁地区单位估价表",
                "source": "伊犁州住房和城乡建设局",
                "execution_date": "2023年9月1日",
                "labor_rate_class2": "132元/工日",
                "material_rate": "除税预算价 运损0.5% 采保2.5%",
                "item_count": len(self.items),
                "parse_errors": len(self.errors),
            },
            "chapters": self.chapters,
            "quota_items": self.items,
        }

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"已保存: {out} ({len(self.items)}条)")
        return str(out.resolve())


def main():
    pdf_path = Path(__file__).parent / "2.全统安装工程消耗量定额伊犁地区单位估价汇总表(2022）.pdf"

    if not pdf_path.exists():
        logger.error(f"PDF文件不存在: {pdf_path}")
        return

    parser = YiliQuotaParser(str(pdf_path))
    parser.parse()

    output_path = Path(__file__).parent / "yili_2022_install.json"
    parser.save_json(str(output_path))

    # 统计
    units = {}
    for item in parser.items:
        u = item.get("unit", "")
        units[u] = units.get(u, 0) + 1
    logger.info(f"单位统计: {dict(sorted(units.items(), key=lambda x: -x[1])[:10])}")

    if parser.errors:
        logger.warning(f"解析异常行 (前10条):")
        for err in parser.errors[:10]:
            logger.warning(f"  {err}")


if __name__ == "__main__":
    main()
```

### 运行测试

```bash
# 先测试前20页
python3 -c "
import pdfplumber
from pathlib import Path
pdf_path = Path('quota_db/2.全统安装工程消耗量定额伊犁地区单位估价汇总表(2022）.pdf')
with pdfplumber.open(str(pdf_path)) as pdf:
    for i in [8,9,400,600]:
        text = pdf.pages[i].extract_text()
        if text:
            lines = [l for l in text.split(chr(10)) if l.strip() and not l.startswith('序')]
            print(f'第{i+1}页: {len(lines)}行')
            for l in lines[:5]:
                print(f'  {l[:100]}')
"

# 全面解析
python3 quota_db/parse_yili_pdf.py
```

---

## 二、市政定额扫描件OCR解析（第二批）

### 创建文件：`quota_db/parse_municipal_ocr.py`

市政定额5册PDF都是扫描件（无文本层），需要OCR。但PDF 243MB全量OCR非常慢。策略：

```
第一步：先把PDF拆为图片（每本约400页，5本共2000页）
第二步：每页只OCR表格区域（不是整页）
第三步：用正则从OCR结果中提取定额数据

实际处理策略（分阶段）：
阶段A（当前）：拆页 + 只OCR前10页测试格式
阶段B（后续）：全量OCR + 人工抽查校验
阶段C（完善）：错误修正 + 合并入库
```

```python
#!/usr/bin/env python3
"""
市政定额扫描件 OCR + 解析
使用PaddleOCR对扫描PDF进行表格识别
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
from paddleocr import PaddleOCR

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger("parse_municipal")


class MunicipalQuotaOCRParser:
    """
    市政定额PDF OCR解析器
    PDF → 图片 → OCR → 正则提取 → JSON
    """

    # 定额数据行正则（适配OCR识别结果）
    DATA_PATTERNS = [
        # 格式：序号 定额编号 名称 单位 人工费 材料费 机械费
        re.compile(r'(\d+)\s+(\d+-\d+-\d+)\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'),
        # 无序号格式：定额编号 名称 单位 数值
        re.compile(r'(\d+-\d+-\d+)\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'),
    ]

    def __init__(self, pdf_path: str, dpi: int = 200):
        self.pdf_path = Path(pdf_path)
        self.dpi = dpi
        self.ocr = None
        self.items = []
        self.errors = []

    def _init_ocr(self):
        """延迟加载OCR引擎"""
        if self.ocr is None:
            logger.info("初始化PaddleOCR...")
            self.ocr = PaddleOCR(
                lang="ch",
                use_angle_cls=True,
                use_gpu=False,
                show_log=False,
            )
            logger.info("OCR引擎就绪")

    def pdf_to_images(self, output_dir: str, page_range: tuple = None) -> List[str]:
        """PDF拆页为图片"""
        doc = fitz.open(str(self.pdf_path))
        total = len(doc)
        start = page_range[0] - 1 if page_range else 0
        end = page_range[1] if page_range else total
        end = min(end, total)

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        image_paths = []

        logger.info(f"PDF拆页: {self.pdf_path.name} 第{start+1}-{end}页 (DPI={self.dpi})")
        for i in range(start, end):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=matrix)
            img_path = out_dir / f"page_{i+1:04d}.png"
            pix.save(str(img_path))
            image_paths.append(str(img_path))

        doc.close()
        logger.info(f"  生成 {len(image_paths)} 张图片 -> {output_dir}")
        return image_paths

    def ocr_page(self, image_path: str) -> List[str]:
        """OCR单页，返回文本行列表"""
        self._init_ocr()
        result = self.ocr.ocr(image_path, cls=True)

        if not result or not result[0]:
            return []

        # 提取文本并按Y坐标排序
        lines_with_y = []
        for item in result[0]:
            bbox = item[0]
            text = item[1][0]
            y_center = (bbox[0][1] + bbox[2][1]) / 2  # Y坐标中心
            lines_with_y.append((y_center, text))

        # 按Y坐标排序（从上到下）
        lines_with_y.sort(key=lambda x: x[0])
        return [text for _, text in lines_with_y]

    def extract_items_from_text(self, lines: List[str], page_num: int) -> List[Dict]:
        """从OCR文本行中提取定额数据"""
        items = []
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            # 跳过表头
            if any(h in line for h in ['定额编号', '项目名称', '单位', '工程量']):
                continue

            for pattern in self.DATA_PATTERNS:
                match = pattern.search(line)
                if match:
                    groups = match.groups()
                    items.append({
                        "quota_code": groups[0] if '-' in str(groups[0]) else groups[1],
                        "name": groups[1] if '-' in str(groups[0]) else groups[2],
                        "numeric_values": [g for g in groups if re.match(r'^\d+\.?\d*$', str(g))],
                        "page": page_num,
                        "raw_text": line[:150],
                    })
                    break

        return items

    def parse_full(self, temp_dir: str = "temp_ocr") -> List[Dict]:
        """全量解析（仅建议用于小PDF）"""
        import shutil

        temp_path = Path(temp_dir) / self.pdf_path.stem
        images = self.pdf_to_images(str(temp_path))

        all_items = []
        total = len(images)

        for i, img_path in enumerate(images):
            lines = self.ocr_page(img_path)
            items = self.extract_items_from_text(lines, i + 1)
            all_items.extend(items)

            if (i + 1) % 10 == 0:
                logger.info(f"  进度: {i+1}/{total}, 已提取 {len(all_items)} 条")

        # 清理临时图片
        shutil.rmtree(temp_path, ignore_errors=True)

        self.items = all_items
        return all_items

    def parse_sample(self, num_pages: int = 10, start_page: int = 21) -> List[Dict]:
        """解析前N页作为格式验证"""
        import shutil
        temp_path = Path("temp_ocr") / self.pdf_path.stem
        images = self.pdf_to_images(str(temp_path), (start_page, start_page + num_pages - 1))

        all_items = []
        for i, img_path in enumerate(images):
            lines = self.ocr_page(img_path)
            items = self.extract_items_from_text(lines, start_page + i)
            all_items.extend(items)
            logger.info(f"  第{start_page+i}页: {len(items)} 条")

        shutil.rmtree(temp_path, ignore_errors=True)
        return all_items

    def save_json(self, output_path: str):
        """保存为JSON"""
        output_data = {
            "_meta": {
                "name": f"新疆市政工程消耗量定额(2020版) OCR解析",
                "source": str(self.pdf_path.name),
                "item_count": len(self.items),
                "parse_method": "PaddleOCR",
            },
            "quota_items": self.items,
        }
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存: {out}")


def main():
    import sys

    # 市政定额第一册
    quota_dir = Path(__file__).parent
    municipal_pdfs = sorted(quota_dir.glob("2020版新疆维吾尔自治区市政工程消耗量定额*.pdf"))

    if not municipal_pdfs:
        logger.error("未找到市政定额PDF文件")
        return

    for pdf_file in municipal_pdfs:
        logger.info(f"\n{'='*60}")
        logger.info(f"处理: {pdf_file.name}")

        parser = MunicipalQuotaOCRParser(str(pdf_file), dpi=200)

        # 先解析前10页测试格式
        sample = parser.parse_sample(num_pages=10, start_page=21)
        logger.info(f"格式验证: {len(sample)} 条 (前10页)")

        if sample:
            logger.info("样本数据:")
            for item in sample[:5]:
                logger.info(f"  {item}")

        # TODO: 确认格式正确后，改为 parse_full() 全量解析
        # parser.parse_full()


if __name__ == "__main__":
    main()
```

### 运行（分阶段）

```bash
# 阶段A：测试10页OCR格式
python3 quota_db/parse_municipal_ocr.py

# 阶段B：确认格式OK后，改为 parse_full() 全量跑
# 注意：全量OCR约2000页，预计需2-4小时（CPU）

# 阶段C：人工抽查 + 修正
# 随机抽取20条定额，和PDF原文对照，确信率达95%+即可入库
```

---

## 三、定额数据合并入库

### 创建文件：`quota_db/merge_quotas.py`

```python
#!/usr/bin/env python3
"""
定额数据合并工具
将多个来源的JSON定额库合并为统一格式
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("merge_quotas")


def merge_quota_dbs(input_files: List[str], output_path: str) -> Dict:
    """合并多个定额JSON文件"""
    all_items = []
    sources = []

    for fpath in input_files:
        fpath = Path(fpath)
        if not fpath.exists():
            logger.warning(f"跳过: {fpath} (不存在)")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            db = json.load(f)

        items = db.get("quota_items", [])
        meta = db.get("_meta", {})

        # 标注来源
        for item in items:
            item["_source"] = fpath.name

        all_items.extend(items)
        sources.append({
            "file": fpath.name,
            "name": meta.get("name", ""),
            "count": len(items),
        })
        logger.info(f"  {fpath.name}: {len(items)} 条")

    # 去重（按quota_code + name）
    seen = set()
    deduped = []
    for item in all_items:
        key = f"{item.get('quota_code','')}|{item.get('name','')[:30]}"
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    removed = len(all_items) - len(deduped)
    if removed > 0:
        logger.info(f"去重: 移除 {removed} 条")

    output_data = {
        "_meta": {
            "name": "鼎梁筑造价工作台 — 新疆定额数据库(合并版)",
            "version": "1.0.0",
            "item_count": len(deduped),
            "sources": sources,
        },
        "quota_items": deduped,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"合并完成: {out} ({len(deduped)}条)")
    return output_data


if __name__ == "__main__":
    # 合并所有已解析的定额JSON
    quota_db = Path(__file__).parent
    json_files = sorted(quota_db.glob("*.json"))
    # 排除已有合并文件和测试文件
    json_files = [f for f in json_files if "combined" not in f.name]

    if json_files:
        merge_quota_dbs(
            [str(f) for f in json_files],
            str(quota_db / "xinjiang_combined.json"),
        )
    else:
        logger.warning("未找到定额JSON文件，先运行 parse_yili_pdf.py")
```

---

## 四、现有代码适配修改

### 修改 `layer2_pricing/quota_matcher.py` 的默认加载路径

```python
# 在 QuotaMatcher.__init__ 的默认路径部分，改为：

if quota_db_path is None:
    default_path = Path(__file__).parent.parent / "quota_db"
    candidates = [
        default_path / "yili_2022_install.json",    # 伊犁安装工程
        default_path / "xinjiang_combined.json",     # 合并版
        default_path / "xinjiang_2020.json",         # 备用
    ]
    for candidate in candidates:
        if candidate.exists():
            quota_db_path = str(candidate)
            logger.info(f"定额库: {candidate.name}")
            break
```

### 修改定额数据字段适配

伊犁估价表JSON的字段名和原始 `xinjiang_2020.json` 不同，需要统一。

在 `quota_matcher.py` 的 `match()` 方法中，查询字段同时支持新旧命名：

```python
# 兼容性处理
base_price = (
    quota_item.get("base_price_per_unit") or
    quota_item.get("base_price") or
    quota_item.get("labor_fee", 0) + quota_item.get("material_fee", 0)
)
```

---

## 五、验证命令

```bash
# 1. 解析伊犁估价表
python3 quota_db/parse_yili_pdf.py

# 2. 查看解析结果
python3 -c "
import json
with open('quota_db/yili_2022_install.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
print(f'定额总数: {db[\"_meta\"][\"item_count\"]}')
print(f'前5条:')
for item in db['quota_items'][:5]:
    print(f'  {item[\"quota_code\"]} | {item[\"name\"][:40]} | {item[\"unit\"]} | 基价{item[\"base_price\"]}')
"

# 3. 定额匹配器加载测试
python3 -c "
from layer2_pricing.quota_matcher import QuotaMatcher
qm = QuotaMatcher()
print(f'加载定额: {len(qm.quota_items)} 条')
# 测试搜索
result = qm.match('基础', {}, 'C30混凝土独立基础')
for r in result[:3]:
    print(f'  匹配: {r[\"quota_item\"].get(\"name\",\"\")[:50]} (分数:{r[\"score\"]})')
"
```

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
