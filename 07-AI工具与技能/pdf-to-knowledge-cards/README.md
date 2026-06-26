---
tags: [规范, 索引, AI, 造价/定额, 造价/清单]
created: 2026-06-24
type: reference
---

# pdf-to-knowledge-cards

> DDC数字驱动建设解析项目沉淀的Skill。  
> 适用于任何需要从PDF（教材/规范/专著）建立知识卡片的任务。

## 快速使用

参考 `SKILL.md` 完整文档，关键步骤：
1. PDF结构探测（PyMuPDF）
2. 全文提取+章节切片
3. 关键词+翻译瑕疵抽取
4. L1主题卡片+L3精读卡片
5. 原子知识库JSONL写入
6. inbox→outputs归档

## 已验证案例

- DDC《数据驱动的建设》第二版（中文，574页）→ 75张知识卡片 + 13条原子库条目 + 16条翻译瑕疵

## 后续可应用

- 新疆2020版市政/建筑/安装定额PDF
- GB/T 50500-2024清单计价标准PDF
- 国标图集（22G钢筋、平法图集）
- 用户提供的其他工程类PDF

## 文件结构

```
pdf-to-knowledge-cards/
├── SKILL.md                 # 完整skill文档
├── README.md                # 本索引
└── scripts/                 # 可复用Python脚本
    ├── ddc_extract.py       # 全文提取
    ├── gen_cards_v2.py      # L1主题卡片生成
    ├── gen_cards_V.py       # L3精读卡片模板（按章节循环）
    ├── gen_cards_VI.py      # VI部分专用
    ├── gen_cards_III.py     # III部分专用
    ├── gen_atomic.py        # 原子知识库写入
    ├── gen_glossary.py      # 翻译瑕疵词典
    ├── archive_outputs.py   # inbox→outputs归档
    ├── toc_deep.py          # TOC深度探测
    └── kw2.py               # 关键词统计
```

---

**生成时间**：2026-06-24 11:26  
**沉淀来源**：DDC解析项目

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
