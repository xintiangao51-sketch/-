---
name: pdf-to-knowledge-cards
description: "PDF→知识卡片自动化工作流。从任意中文PDF（教材/规范/专著）一键产出主题卡片+精读卡片+原子知识库条目+翻译瑕疵词典。适用建筑/造价/工程类PDF（100-1000页）。"
version: 1.0.0
author: 昕田 + Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [pdf, knowledge-card, automation, ddc, cost-engineering]
    category: codex共享技能
    related_skills: [xinjiang-cost-engineer, opc-knowledge-architecture]
---

# PDF→知识卡片自动化

## When to Use

- 拿到一本新的PDF教材/规范/专著，需要快速建立可检索的知识卡片集
- 希望把长篇文档沉淀为原子知识库JSONL条目（供Agent调用）
- 需要识别机器翻译瑕疵（外文译著类PDF）
- 想知道某个章节的L3级细节，又不想读完全书

**适用规模**：100-1000页PDF（>1000页建议分章节处理）

## Prerequisites

- Python 3.10+
- `pip install pymupdf pdfplumber`（PyMuPDF中文PDF解析快，pdfplumber表格抽取）
- 工作区有 `00-工作台/inbox/`（脚本暂存）+ `06-参考文档/{主题}/`（产物归档）
- Obsidian知识库（可选，用于浏览）

## How to Run

### Step 1: PDF结构探测（弹线）

```python
import fitz
doc = fitz.open(r"你的PDF路径.pdf")
print(f"页数: {len(doc)}, TOC数: {len(doc.get_toc())}")
for level, title, page, *rest in doc.get_toc(simple=False):
    if level <= 2:
        print(f"L{level} p{page}: {title}")
```

**目的**：确认PDF有TOC、可文本提取（非扫描件）、章节边界清晰。

### Step 2: 全文提取+按章节切片

```python
import re
toc = doc.get_toc(simple=False)
l1_pages = [(t, p-1) for lv, t, p, *r in toc if lv == 1]
# 加哨兵末尾页
splits = l1_pages + [("END", len(doc))]
for idx, (title, start) in enumerate(splits[:-1]):
    end = splits[idx+1][1]
    out_path = f"part{idx+1:02d}_{sanitize(title)}.txt"
    # 提取start到end页内容，保留页码分隔符
```

**注意**：用 `----- PAGE {n} -----` 分隔，便于后续按页定位。

### Step 3: 关键词+翻译瑕疵抽取

```python
import collections
text = open("ddc_fulltext.txt", encoding='utf-8').read()
zh = collections.Counter(re.findall(r'[一-龥]{2,8}', text))
en = collections.Counter(re.findall(r'[A-Z][A-Za-z0-9\-_]{1,15}', text))
# 主题索引：取PDF的"主题索引"章节（如有），按"词, 页, 页"格式解析
```

**机器翻译瑕疵识别**：
- 看主题索引里"看似翻译异常"的词（如"阿帕奇气流"、"友邦保险公司"）
- 用真实英文术语建对照表
- 工具：`translation_glossary.json`

### Step 4: 按L1/L3两层产出卡片

**L1部分主题卡片**（10-15张）：
- 每个部分1张
- 包含：核心概念、开篇/中段/结尾摘要、关键词频次、与其他部分关系

**L3小节精读卡片**（20-50张）：
- 按TOC里的L3章节切片
- 包含：本节核心问题、关键方法、术语对照、与本业务的关联、原文段落

### Step 5: 写入原子知识库JSONL

把核心方法（M）/工具（T）/洞察（I）写入 `98-原子知识库/`，每条带 `card_ref` 字段反向引用具体卡片。

### Step 6: 归档到outputs

按知识库规范，已确认的产物复制到 `outputs/{主题}_知识卡片集/`。

## Pitfalls

1. **PyMuPDF依赖**：中文PDF必须用 `fitz`（PyMuPDF）效果最好，`pdfplumber`对复杂排版更稳。建议两者结合。
2. **TOC索引错位**：L1-L3映射到文件切片时，必须用**两位数**（如 `part04` 而非 `part4`），否则 `part4 in part40_xxx` 会误匹配。
3. **PDF噪声**：页码、分隔符、引用标记需要用正则去掉再做词频统计。
4. **翻译瑕疵词典**：机器翻译的PDF必然有大量错误，必须单独建词典，不要在卡片里反复警告。
5. **卡片的"信号噪声比"**：避免直接复制大段原文（=噪声高），应提炼为"核心问题+关键方法"格式。
6. **原子库升级**：B级条目必须标注 `confidence=B`，升级A级需人工引用具体段落。
7. **保留原始PDF**：永远不修改原PDF，所有提取写到独立的txt/md文件。
8. **三级证据链**：PDF原文件=一级；提炼事实=二级；交叉验证的结论=三级，必须分层。

## 验证清单

- [ ] PDF结构已探测（页数、TOC、章节数确认）
- [ ] 全文已提取（字符数 / 文件大小已记录）
- [ ] 关键词统计已生成（zh/en json）
- [ ] 翻译瑕疵词典已建（至少10条）
- [ ] L1部分主题卡片 ≥ 5张
- [ ] L3精读卡片 ≥ 10张
- [ ] 原子知识库增量条目已写入
- [ ] 总览索引页已生成
- [ ] 知识库首页+参考文档总览已更新
- [ ] inbox半成品 → outputs归档完成

## Performance（实测）

- 574页中文PDF（DDC_2ndEdition_Chinese.pdf）
- 提取全文：约30秒
- TOC解析：<1秒
- 关键词统计：约10秒
- 卡片生成：约60秒（50张）
- **总耗时**：约5分钟（含验证）

## References

- `scripts/ddc_extract.py` — 全文提取模板
- `scripts/gen_cards_v2.py` — L1主题卡片生成
- `scripts/gen_cards_V.py` — V部分L3精读卡片模板
- `scripts/gen_atomic.py` — 原子知识库JSONL写入
- `scripts/archive_outputs.py` — inbox→outputs归档

---

**沉淀来源**：DDC数字驱动建设解析项目（2026-06-24）  
**维护**：Hermes Agent

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
