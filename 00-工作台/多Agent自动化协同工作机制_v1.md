---
tags: [参考]
created: 2026-06-22
type: reference
---

# 多Agent自动化协同工作机制 v1

> 工作区：`D:\造价知识库`  
> 协同目录：`D:\造价工作台\20_Agent协同交付`  
> 主控：Hermes  
> 子Agent：Claude Code、Codex、其他可接入Agent  
> 目标：把临时调用子Agent，升级为“任务卡驱动、自动分派、成果回流、Hermes质检、知识库沉淀”的可复用工作机制。

---

## 1. 核心结论

多Agent协同不是“我临时喊几个Agent帮忙”，而是一套固定流水线：

```text
用户提出目标
  ↓
Hermes拆解任务
  ↓
生成标准任务卡
  ↓
投递到不同Agent inbox
  ↓
子Agent执行并产出成果
  ↓
成果进入 outbox / task_outputs
  ↓
Hermes质检、补缺、复审
  ↓
合格成果进入知识库/项目交付目录
  ↓
沉淀模板、规则、记忆、案例
```

---

## 2. 角色分工

| 角色 | 定位 | 主要职责 | 适合任务 |
|---|---|---|---|
| Hermes 主控 | 总调度/总质检 | 拆任务、定标准、派发、复核、归档、记忆沉淀 | 任务拆解、造价判断、质量控制、最终交付 |
| Claude Code | 深度执行/文档与代码能力强 | 读写文件、开发脚本、整理复杂文档、生成报告 | Python工具、Markdown体系、Excel处理、文档重构 |
| Codex | 功能构建/批量处理 | 代码实现、批量改造、规则表结构化 | 自动化脚本、数据表、规则引擎、CLI工具 |
| 其他Agent | 专项能力补充 | OCR、搜索、浏览器、知识库检索、视觉识图 | 图纸识别、网页采集、PDF/OCR、资料检索 |
| 老高人工复核 | 专业把关 | 新疆定额、合同、费率、造价逻辑最终判断 | 关键金额、定额依据、合同风险、对外交付 |

---

## 3. 标准目录协议

```text
D:\造价工作台\20_Agent协同交付\
├─ task_queue\
│  ├─ pending\       # Hermes待拆解/待派发任务
│  ├─ assigned\      # 已分派任务
│  ├─ running\       # 执行中任务
│  ├─ review\        # 待Hermes质检
│  ├─ done\          # 已完成归档
│  ├─ blocked\       # 缺资料/阻塞
│  └─ failed\        # 执行失败
├─ inbox\
│  ├─ ClaudeCode\
│  ├─ Codex\
│  └─ 其他Agent\
├─ outbox\
│  ├─ ClaudeCode\
│  ├─ Codex\
│  └─ 其他Agent\
├─ task_outputs\     # 按task_id归集成果
├─ agent_status\     # Agent在线/能力状态
├─ logs\             # 调度/执行/归档日志
└─ archive\          # 历史归档
```

---

## 4. 任务卡标准

每个任务必须有唯一 `task_id`。推荐 YAML：

```yaml
task_id: HERMES-YYYYMMDD-001
project_name: 项目名称
task_date: YYYY-MM-DD
task_type: 知识库 / 预算 / 合同 / 变更 / 提量 / 自动化 / 采集 / 其他
priority: P0 / P1 / P2
owner_agent: ClaudeCode / Codex / Hermes / 其他Agent
reviewer: Hermes
status: 待分派

task_goal: >
  明确写清要做什么，不写空泛目标。

input_files:
  - D:\路径\文件.xlsx

deliverables:
  - D:\路径\成果.md
  - D:\路径\成果.xlsx

acceptance_criteria:
  - 文件必须真实存在
  - 表格字段齐全
  - 不确定处标⚠
  - 需Hermes质检后才能进入done

constraints:
  - 禁止删除原始文件
  - 禁止虚构定额编号/价格/政策文号
  - 费率按项目依据动态确认
```

---

## 5. 自动化工作流

### 5.1 派发流程

| 步骤 | 动作 | 责任方 | 产物 |
|---|---|---|---|
| 1 | 用户提出目标 | 用户 | 原始需求 |
| 2 | Hermes拆解任务 | Hermes | 任务拆解表 |
| 3 | 生成任务卡 | Hermes | `task_id.yaml` |
| 4 | 投递Agent inbox | 调度器/Hermes | inbox任务文件 |
| 5 | 子Agent执行 | Claude/Codex | 初稿成果 |
| 6 | 成果回流outbox | 子Agent | 报告/代码/表格 |
| 7 | Hermes质检 | Hermes | 复审记录 |
| 8 | 合格入库 | Hermes | 知识库/交付物 |

### 5.2 质检流程

```text
成果文件存在性检查
  ↓
字段完整性检查
  ↓
造价逻辑检查
  ↓
新疆本地化口径检查
  ↓
风险/不确定项标注
  ↓
复审记录
  ↓
done 或 blocked/needs_fix
```

---

## 6. 任务类型与Agent分派规则

| 任务类型 | 推荐主Agent | Hermes质检重点 |
|---|---|---|
| 知识库整理 | Claude Code + Codex | 目录、索引、来源、可检索性 |
| Excel批处理 | Claude Code | 公式、字段、汇总、交叉验证 |
| 自动化脚本 | Codex / Claude Code | 可运行、错误处理、日志、样例测试 |
| 定额/组价规则 | Hermes主控 + Claude整理 | 定额依据、费率依据、四维拆解 |
| 合同审查 | Hermes主控 | 法条编号、风险等级、条款定位 |
| 图纸提量 | OCR/视觉Agent + Hermes | 尺寸来源、扣减规则、工程量计算式 |
| 市场线索采集 | 浏览器/搜索Agent + Codex | 来源、联系方式、需求信号、去重 |

---

## 7. 状态机

| 状态 | 含义 | 下一步 |
|---|---|---|
| pending | 任务已提出，未分派 | Hermes拆解/派发 |
| assigned | 已分派到Agent | Agent执行 |
| running | Agent执行中 | 等待成果 |
| review | 成果已回流，待质检 | Hermes复审 |
| needs_fix | 有缺口，需返工 | 重新派发 |
| blocked | 缺资料或外部条件 | 补资料 |
| done | 已通过质检 | 入库/交付 |
| failed | 执行失败 | 记录原因，重建任务 |

---

## 8. 质量红线

| 红线 | 处理 |
|---|---|
| 文件不存在却声称完成 | 直接退回 |
| 没有真实运行结果 | 不得标done |
| 缺定额编号却输出确定结论 | 标⚠并退回补依据 |
| 缺市场价却编价格 | 标🔴，禁止入库 |
| 未质检成果进入最终目录 | 退回 review |
| 子Agent报告与实际文件不一致 | 以实际文件为准，报告修正 |

---

## 9. 当前落地到001/002的样板

| 任务 | 实际机制样板 |
|---|---|
| 001 造价基础知识库建设 | Claude/Cowork生成知识库、Prompt、报告；Hermes复审发现Skill/记忆证据不足；补交Skill包和结构化记忆 |
| 002 分类与规则库 | Codex生成分类、Tag、定额、取费规则；Hermes复审发现工程量规则缺失；补入工程量计算规则并形成复审记录 |

这说明机制已经跑通雏形：**子Agent能产出，Hermes能质检，缺口能补齐，成果能入库。**

---

## 10. 下一阶段建设目标

| 阶段 | 目标 | 交付物 |
|---|---|---|
| V1 文件协议 | 任务卡、inbox/outbox、task_outputs、复审记录跑通 | 调度器+任务卡模板+复审模板 |
| V2 半自动调度 | 自动发现任务、提示确认、自动归档成果 | `scheduler_core.py`、`poll_tasks.py`、`collect_results.py` |
| V3 Agent自动调用 | Claude Code/Codex CLI可用时自动执行低风险任务 | Agent执行器、状态监控、日志 |
| V4 造价流水线 | 报价/变更/提量/结算形成标准流水线 | 业务任务模板、验收规则、案例库 |

---

## 11. 一句话定位

这是老高自己的“工程造价AI生产线”：

```text
Hermes管脑子和质检，Claude/Codex管执行和批处理，知识库管沉淀，老高管专业判断和对外交付。
```
