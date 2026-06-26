---
tags: [索引, 工具, 脚本]
created: 2026-06-22
updated: 2026-06-24
type: index
---

# 🔧 tools/ 脚本工具箱

> 知识库自动化脚本集中管理。每个脚本独立运行，可配合定时任务触发。

---

## 📐 命名规范

| 类型 | 前缀 | 示例 |
|------|------|------|
| 采集类 | `crawl_` | `crawl_xj_info_price.py` |
| 回流类 | `backflow_` | `backflow_prices.py` |
| 同步类 | `sync_` | `sync_config.py` |
| 生成类 | `auto_` / `generate_` | `auto_kc_generator.py` |
| 检查类 | `check_` / `scan_` | `obsidian_optimizer.py` |
| 导入类 | `import_` / `ingest_` | `import_from_knowledge_base.py` |
| 临时类 | `_tmp_` | → 归档到 `_archive/` |

规则：
- Python文件用 `snake_case.py`
- PowerShell文件用 `PascalCase.ps1`
- 临时调试文件以 `_tmp_` 开头，用完移入 `_archive/`
- 每个脚本头部必须有docstring说明用途和用法

---

## 📦 活跃脚本清单

### 根目录（tools/）

| # | 脚本 | 用途 | 方向 | 输出 |
|:--|:-----|:-----|:---:|:-----|
| 1 | `crawl_xj_info_price.py` | 爬取新疆住建厅信息价 | 采集→知识库 | `11-材料设备价格库/` |
| 2 | `crawl_policy.py` | 全网造价知识爬取+KC生成 | 采集→知识库 | `08-参考规范/` |
| 3 | `auto_kc_generator.py` | 从笔记提取知识卡片 | 内部处理 | `10-索引与导航/KC-NNN.md` |
| 4 | `material_price_updater.py` | 材料价格更新到趋势页 | 内部处理 | `01-造价核心/` |
| 5 | `obsidian_optimizer.py` | 知识库健康度检查 | 检查 | `00-工作台/` |
| 6 | `sync_config.py` | 三区参数一致性检查+同步 | 知识库↔工作台 | `logs/sync_log.json` |
| 7 | `backflow_prices.py` | 价格数据回流（工作台→知识库） | 工作台→知识库 | MD追加回流日志 |
| 8 | `backflow_leads.py` | 采集成果回流（工作站→知识库） | 工作站→知识库 | `16-运营数据/` |
| 9 | `batch_fix_links.py` | 批量修复Obsidian内部链接 | 内部处理 | 原地修改 |
| 10 | `auto_bid_analyzer.py` | 投标文件自动分析 | 分析 | `05-投标报价/` |
| 11 | `auto_claim_timeline.py` | 索赔时间线自动生成 | 分析 | `03-合同与法务/` |
| 12 | `auto_project_review.py` | 项目复盘报告生成 | 分析 | `12-项目案例库/` |
| 13 | `definitive_fix.py` | 知识库结构修复工具 | 内部处理 | 原地修改 |

### scripts/ 子目录

| # | 脚本 | 用途 |
|:--|:-----|:-----|
| 1 | `build_labor_knowledge_cards.py` | 劳务知识卡片批量生成 |
| 2 | `extract_decrypted_xls.py` | 加密Excel解密提取 |
| 3 | `generate_excel.py` | Excel模板生成工具 |
| 4 | `ingest_labor_docs.py` | 劳务文档导入处理 |
| 5 | `install_missing_existing_agents.py` | Agent安装工具 |
| 6 | `s08_rename.py` | 08系列目录重命名工具 |
| 7 | `setup_construction_agents.py` | 施工Agent批量配置 |
| 8 | `verify_construction_agents.py` | Agent配置验证 |

### web-stack/ 子目录

| # | 脚本 | 用途 |
|:--|:-----|:-----|
| 1 | `smoke_web_stack.py` | Web技术栈冒烟测试 |
| 2 | `INSTALL_AND_SMOKE_REPORT.md` | 安装与测试报告 |

### _archive/ 子目录（已归档）

| 类型 | 文件 | 归档原因 |
|------|------|----------|
| 临时调试 | `_tmp_hami_*.py` (4个) | 哈密项目一次性脚本，已完成 |
| 一次性清理 | `codex_cleanup/` (21个) | Codex清理调试，已完成 |

---

## 🔄 三区数据流脚本

```
D:\知识库（母版）
  │
  ├──→ import_from_knowledge_base.py（在工作台price_db/中）
  │    知识库MD → 工作台JSON
  │
  ├──→ sync_config.py
  │    检查知识库↔工作台参数一致性
  │
  ├──← backflow_prices.py
  │    工作台JSON → 知识库MD（追加回流日志）
  │
  └──← backflow_leads.py
       工作站采集数据 → 知识库16-运营数据
```

---

## 🕐 定时任务

| 任务 | 脚本 | 频率 | 状态 |
|:-----|:-----|:---:|:---:|
| 信息价月度采集 | `crawl_xj_info_price.py` | 每月1日 | ✅ |
| 材料价格周更 | `material_price_updater.py` | 每周一 | ✅ |
| 三区参数同步 | `sync_config.py` | 每周一 | 🔲 待注册 |
| 价格回流 | `backflow_prices.py` | 每周五 | 🔲 待注册 |
| 采集成果回流 | `backflow_leads.py` | 每日 | 🔲 待注册 |
| 健康度检查 | `obsidian_optimizer.py` | 每周五 | 🔲 待注册 |

---

## 🚀 手动运行

```bash
# 三区参数同步检查
python D:/知识库/tools/sync_config.py

# 价格回流（工作台→知识库）
python D:/知识库/tools/backflow_prices.py --apply

# 采集成果回流（工作站→知识库）
python D:/知识库/tools/backflow_leads.py --apply

# 信息价采集
cd D:/知识库/tools && python crawl_xj_info_price.py

# 健康度检查
cd D:/知识库/tools && python obsidian_optimizer.py
```

---

返回 [[🏠 知识库首页]]

---

🔗 **自动化工具箱**：[[tools/自动化脚本工具箱]]
