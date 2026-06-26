---
tags: [AI, 索引]
created: 2026-06-12
type: reference
---

# AI工具与工程量自动计算工作流

> 老高造价工作台 | 基于实际搭建经验

---

## 一、整体架构：6引擎流水线

```
PDF图纸 → [Layer1 OCR] → 结构化文本 → [Layer2 组价] → 定额清单
                                            ↓
         [Engine6 风险分析] ← [Layer3 审核] ←─┘
                                            ↓
         [Search Engine] ←→ [Web UI] → 用户
```

| 引擎 | 功能 | 技术栈 | 状态 |
|------|------|--------|------|
| Layer1 OCR | 图纸识别 | PaddleOCR + PyMuPDF | ✅ 已搭建 |
| Layer2 Pricing | 定额匹配组价 | 正则+tf-idf匹配 | ✅ 已搭建 |
| Layer3 Audit | 清单合规审核 | 规则引擎 | ✅ 已搭建 |
| Engine6 Risk | 造价风险分析 | 偏差检测 | ✅ 已搭建 |
| Search | 全文检索 | SQLite FTS5 | ⚠ 待完善 |
| Web UI | 用户界面 | Streamlit | ✅ 已搭建 |

---

## 二、CAD/AI工具链速查

### 2.1 已配置的工具

| 工具 | 用途 | 配置状态 |
|------|------|---------|
| Claude Code | 代码生成、脚本编写 | ✅ DeepSeek后端 |
| Codex | CAD智能体 | ✅ 已配置 |
| PaddleOCR | PDF图纸文字识别 | ✅ CPU模式 |
| PyMuPDF | PDF解析/渲染 | ✅ 300DPI |

### 2.2 关键工作流

**工作流1：图纸→工程量**
```
1. PDF放入 input/ 目录
2. Layer1 OCR 提取尺寸标注（正则：截面/长度/标高/钢筋）
3. 构件分类（梁/板/柱/墙/基础/钢筋）
4. 输出 → output/工程量清单.xlsx
```

**工作流2：工程量→报价**
```
1. 读取工程量清单
2. 匹配2020版新疆市政定额子目
3. 套用地区人工单价+材料价+机械台班
4. 取费：管理28% + 利润18% + 规费22% + 税9%
5. 输出 → output/投标报价表.xlsx
```

**工作流3：报价审核**
```
1. 对比历史项目单价
2. 检测偏差（±5%绿 / ±15%黄 / >±15%红）
3. 生成审核报告
```

---

## 三、Claude Code / Hermes 配置要点

### 3.1 造价专用技能
| 技能 | 来源 | 用途 |
|------|------|------|
| xinjiang-cost-engineer | 本地 | 老高人设+定额参数 |
| ima-skill | QQ IMA | 知识库读写 |
| xinjiang-drawing-review | D盘 | 审图规则 |

### 3.2 Hermes 启动命令
```bash
# 带造价人设启动
hermes -s xinjiang-cost-engineer

# 带知识和IMA
hermes -s xinjiang-cost-engineer -s ima-skill
```

---

## 四、造价工作台目录结构

```
D:\造价工作台\
├── config/config.yaml       ← 全局参数（定额、费率、人工单价）
├── layer1_ocr/              ← OCR引擎
├── layer2_pricing/          ← 组价引擎
├── layer3_audit/            ← 审核引擎
├── engine6_risk/            ← 风险分析
├── quota_db/                ← 定额PDF+JSON数据
├── price_db/                ← 材料价格爬虫
├── method_library/          ← 施工工法库
├── search_engine/           ← 全文检索
├── input/                   ← 待处理图纸
├── output/                  ← 输出结果
├── test_drawings/           ← 测试图纸
└── utils/                   ← 工具函数
```

### 4.1 已下载的定额PDF
| 文件 | 大小 | 状态 |
|------|------|------|
| 2020版新疆市政定额第一册 | 56.75MB | ✅ 已下载 |
| 第二册（桥涵隧道） | 49.14MB | ✅ |
| 第三册（给水排水） | 51.15MB | ✅ |
| 第四册（燃气供热） | 42.6MB | ✅ |
| 第五册（水处理） | 43.77MB | ✅ |
| 伊犁2022单位估价表 | — | ✅ |
| 费用定额（新建标〔2021〕11号） | 6.57MB | ⚠待下载 |

---

## 五、待办优先清单

| 优先级 | 任务 | 状态 |
|--------|------|------|
| P0 | 下载费用定额PDF（guifanku.com/840926.html） | ❌ |
| P0 | 从费用定额核实管理28%/利润18%/规费22% | ❌ |
| P1 | 完善喀什/和田等南疆地区人工基价数据 | ❌ |
| P1 | PDF→JSON定额解析脚本 | ⚠ 部分完成 |
| P2 | 材料价格爬虫接入新疆交通厅季报 | ⚠ 框架已有 |
| P2 | Web UI完善 | ⚠ 基础可用 |

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
