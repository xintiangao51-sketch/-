---
tags: ["AI", "规范", "索引"]
created: 2026-06-24
type: reference
---

# 三件套知识库引擎 · 总入口

> 老高的工程造价 + 工程 AI 自动化知识中枢。  
> 位置：D:\知识库\17-知识库引擎\  
> 创建：2026-06-23 由 Hermes（鼎梁筑）协助部署

---

## 一、三件套定位

| 引擎 | 角色 | 核心能力 | 部署难度 | 启动后访问 |
|---|---|---|---|---|
| **AnythingLLM** | 桌面工作台 / 文档对话 | 直接拖文件、PDF/Word/Excel/MD，自带向量库，开箱即用 | 🟢 极易（桌面安装包） | 启动桌面应用即可 |
| **RAGFlow** | 重型文档解析 / OCR / 表格抽取 | PDF/扫描件 OCR、规范图集、复杂表格、引用追溯 | 🟡 中（需 Docker Desktop） | http://localhost (Docker 启动后) |
| **Khoj** | 第二大脑 / Obsidian 联动 / 对话式检索 | 直接索引 D:\知识库\ 全部 markdown，Obsidian 插件无缝集成 | 🟢 易（pip / 桌面包） | http://localhost:42110 |

---

## 二、推荐分工（不要把三件套当冗余）

| 场景 | 用哪个 |
|---|---|
| 平时打开就用、拖个 PDF 问问题 | AnythingLLM |
| 工程规范 / 图集 / 扫描件、要 OCR 和表格抽取 | RAGFlow |
| D:\知识库 全文检索 + Obsidian 笔记联动 | Khoj |
| 网页文献抓取 → 入库 | crawl4ai（已是 Hermes 技能）+ omnivore（可选） |

---

## 三、目录结构

```
D:\知识库\17-知识库引擎\
├── README.md                      ← 你正在看的总入口
├── 01-AnythingLLM\
│   └── SETUP.md                   ← 安装步骤、API key 配置
├── 02-RAGFlow\
│   └── SETUP.md                   ← Docker 部署、知识库创建
├── 03-Khoj\
│   └── SETUP.md                   ← pip / 桌面端、Obsidian 联动
└── 99-统一检索脚本\
    ├── README.md
    ├── search.js                  ← Node 版统一检索（推荐）
    ├── search.py                  ← Python 版（备用）
    ├── config\
    │   └── engines.json           ← 三件套地址 / API key 配置
    └── output\                    ← 检索结果落盘（markdown）
```

---

## 四、部署顺序建议

| 步 | 干啥 | 耗时 | 是否阻塞 |
|---|---|---|---|
| 1 | 装 Khoj（pip 装） | ~10 min | 不依赖 Docker，先跑通 |
| 2 | 装 AnythingLLM 桌面版 | ~10 min | 下载 → 安装 |
| 3 | 装 Docker Desktop | ~15 min | RAGFlow 前置 |
| 4 | 跑 RAGFlow | ~20 min | Docker 装完后 |
| 5 | 配统一检索脚本（填 API） | ~5 min | 三件套至少装一个就能用 |

详见各 SETUP.md。

---

## 五、检索脚本一句话用法

```powershell
cd D:\知识库\17-知识库引擎\99-统一检索脚本
node search.js "新疆 市政 沥青砼 定额 单价"
# 或
python search.py "新疆 市政 沥青砼 定额 单价"
```

脚本会同时查 Khoj / AnythingLLM / RAGFlow / D:\知识库本地全文，结果合并、去重、按相关度排序，输出到 `output\` 目录的 markdown 文件。

---

## 六、变更记录

- 2026-06-23 初版（鼎梁筑创建）

---

🔗 **知识库首页**：[[🏠 知识库首页]]
