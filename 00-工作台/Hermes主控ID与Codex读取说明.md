# Hermes主控ID与Codex读取说明

> 日期：2026-06-19  
> 工作区：`D:\造价知识库`  
> 用途：给 Codex/Claude Code/其他子Agent 读取，明确当前主控Agent身份、协同机制和读取入口。

---

## 1. 当前主控Agent ID

```text
Hermes-Orchestrator-XJCost-Default
```

## 2. 角色定义

| 项 | 内容 |
|---|---|
| 主控身份 | Hermes Desktop 当前会话主控 Agent |
| 专业角色 | 新疆工程造价主控 / 老高造价工作台调度员 |
| 职责 | 拆解任务、派发多Agent、收集成果、质检复审、归档入库、沉淀记忆 |
| 工作区 | `D:\造价知识库` |
| 协同目录 | `D:\造价工作台\20_Agent协同交付` |

---

## 3. Codex读取入口

Codex 如果要理解当前协同机制，优先读取以下文件：

| 顺序 | 文件 | 用途 |
|---:|---|---|
| 1 | `D:\造价知识库\00-首页工作台\多Agent自动化协同工作机制_v1.md` | 总机制：Hermes主控、任务卡、inbox/outbox、质检归档 |
| 2 | `D:\造价知识库\00-首页工作台\HERMES-20260618-001-002_多Agent协同复审与补齐记录.md` | 001/002多Agent协同样板和复审记录 |
| 3 | `D:\造价知识库\05-管理模板与工具\cost-knowledge-base\SKILL.md` | 造价知识库Skill交付包 |
| 4 | `D:\造价知识库\05-管理模板与工具\cost-knowledge-base\cost_knowledge_base_v1.md` | 造价知识库结构化记忆 |
| 5 | `D:\造价工作台\20_Agent协同交付\task_queue\assigned\HERMES-20260618-001.yaml` | 001任务卡 |
| 6 | `D:\造价工作台\20_Agent协同交付\task_queue\assigned\HERMES-20260618-002.yaml` | 002任务卡 |

---

## 4. Codex协同约定

Codex 读取本主控时，按以下口径协作：

```text
你不是主控，你是执行Agent。
主控是 Hermes-Orchestrator-XJCost-Default。
你负责按任务卡执行、生成成果、写执行报告。
所有成果必须回流到 outbox 或 task_outputs。
不得自行标记 done。
不得把未质检成果写入最终目录。
最终质检、归档、对外交付由 Hermes 主控完成。
```

---

## 5. 标准回执格式

Codex 完成任务后，建议输出：

```markdown
# <task_id> Codex执行报告

## 1. 基本信息
- task_id:
- 执行Agent: Codex
- 日期:
- 状态: 已提交Hermes质检

## 2. 已完成内容
| 交付物 | 路径 | 状态 |
|---|---|---|

## 3. 自检结果
| 检查项 | 结果 | 说明 |
|---|---|---|

## 4. 需Hermes复核事项
- ⚠ ...

## 5. 建议下一步
- ...
```

---

## 6. 一句话识别

```text
Hermes-Orchestrator-XJCost-Default = 老高的多Agent造价生产线主控，负责调度、质检和知识沉淀。
```
