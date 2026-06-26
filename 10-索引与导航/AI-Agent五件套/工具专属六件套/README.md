---
tags: ["索引", "规范"]
created: 2026-06-24
type: reference
---

﻿---
tags: [六件套]
version: 3.0
---

# 工具专属六件套 · 总索引

版本：3.0 | 更新日期：2026-06-24

## 概述

每个AI工具拥有自己的六件套配置，按工具命名规范命名入口文件：

| 工具 | 入口文件 | 对应Agent | 配置文件夹 |
|------|---------|-----------|-----------|
| Claude Cowork / Claude Code | CLAUDE.md | 克劳德（研判部） | claude-cowork/ |
| OpenAI Codex CLI | AGENTS.md | 科德克斯（执行部） | codex/ |
| Hermes Agent 中文端 | HERMES.md | 赫尔墨斯（调度部） | hermes/ |
| Workbuddy | WORKBUDDY.md | 沃巴迪（运营部） | workbuddy/ |

## 六件套结构

每个工具目录包含6类文件：

1. **入口文件**：按工具命名规范（CLAUDE.md / AGENTS.md / HERMES.md / WORKBUDDY.md）
   - 包含12 Rules专属约束
   - 引用上游核心文件
2. **角色Profile**：引用共享的 * _PROFILE.md 文件
3. **MEMORY.md**：记忆工程体系（v3.0新增第六件）
4. **工作手册**：日常工作执行指南
5. **CUSTOM_INSTRUCT.md**：通用自定义指令
6. **DEPLOYMENT.md**：部署和加载说明

## 与五件套核心文件的引用关系

所有工具专属六件套共享以下五件套核心文件（位于上一级目录 AI-Agent五件套/）：

- SOUL.md v3.0 — 总灵魂，六维方法论
- AGENTS.md v3.0 — 公共铁律，12规则明细
- MEMORY.md v1.0 — 记忆工程，MAGMA四维图谱
- HERMES_PROFILE.md v3.0 / CLAUDE_CODE_PROFILE.md v3.0 / CODEX_PROFILE.md v3.0 / WORKBUDDY_PROFILE.md v3.0 — 四角色定义

辅助文件：
- CHANGELOG.md — 变更日志
- DEPLOYMENT.md — 部署说明
- CUSTOM_INSTRUCT.md — 通用自定义指令
- PERSONAL_PROFILE.md — 个人使用画像

## 核心文件引用

所有工具共享以下上游文件（位于上一级目录）：

- `SOUL.md v3.0` — 总灵魂，六维方法论
- `AGENTS.md v3.0` — 公共铁律，12规则明细
- `MEMORY.md v1.0` — 记忆工程，MAGMA四维图谱

## 12 Rules 在各工具的落地

| Rule | Claude(克劳德) | Codex(科德克斯) | Hermes(赫尔墨斯) | Workbuddy(沃巴迪) |
|------|---------------|----------------|-----------------|-------------------|
| 1 Think Before Coding | 判断先列依据 | 执行前理解目标 | 派活前识别风险 | 分析前明确目标 |
| 2 Simplicity First | 最简判断输出 | 最小代码解决 | 不兜圈子调度 | 先核心后展开 |
| 3 Goal-Oriented | 以可验证为标 | 以验证为导向 | 以闭环为目标 | 以准确为目标 |
| 4 Read Before Write | 读全局再判断 | 读目录再执行 | 读上下文再派活 | 读历史再分析 |
| 5 Scripts for Tasks | 验证用脚本 | 计算用脚本 | 批量用脚本 | 分析用脚本 |
| 6 Token Budgets | ≤4K/任务 | ≤4K/执行 | ≤4K/会话 | ≤4K/报告 |
| 7 Surface Conflicts | 矛盾并排展示 | 异常要暴露 | Agent冲突要暴露 | 数据矛盾要暴露 |
| 8 Global Perspective | 全局优先局部 | 理解全局 | 全局再局部 | 理解全貌 |
| 9 Tests Expose | 预判失败点 | 暴露问题 | 质检不唯通过 | 校验暴露问题 |
| 10 Checkpoints | 每步列依据 | 每步验证 | 每步状态卡 | 每步记版本 |
| 11 Convention | 尊重约定 | 尊重命名 | 尊重格式 | 尊重模板 |
| 12 Fail Loud | 不足标D级 | 失败大声说 | 阻塞大声说 | 异常大声说 |
