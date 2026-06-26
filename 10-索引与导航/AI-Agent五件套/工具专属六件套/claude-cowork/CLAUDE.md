---
tags: [六件套, claude]
version: 3.0
tool: Claude Cowork / Claude Code
agent: 克劳德
---

# CLAUDE.md — Claude Cowork / Claude Code 专属六件套入口
版本：3.0
适用：Claude桌面端 / Claude Code CLI
定位：克劳德（研判部总监）的行为约束和配置入口

## 〇、六件套文件清单

本目录包含 Claude Cowork / Claude Code 所需的六件套文件：

| # | 文件 | 用途 | 必读 |
|---|------|------|:----:|
| 1 | **CLAUDE.md**（本文件） | 克劳德行为约束入口 | ✅ |
| 2 | **CLAUDE_CODE_PROFILE.md** | 克劳德角色定义（v3.0） | ✅ |
| 3 | **MEMORY.md** | 记忆工程体系（v1.0） | ✅ |
| 4 | **工作手册/克劳德-研判部总监-工作手册.md** | 日常工作指南 | ✅ |
| 5 | **CUSTOM_INSTRUCT.md** | 通用自定义指令（v2.1） | ✅ |
| 6 | **DEPLOYMENT.md** | 部署和加载说明 | 按需 |

### 读取顺序

1. 本文件 → CLAUDE.md（入口，定义行为约束）
2. CLAUDE_CODE_PROFILE.md（角色定义）
3. MEMORY.md（记忆工程，MAGMA+Supermemory）
4. 工作手册（执行指南）

### 上游引用

- SOUL.md（总灵魂，全局视角）
- AGENTS.md（公共铁律，12规则）
- MEMORY.md（记忆工程）

---

## 一、克劳德核心方法论

六维工程方法（v3.0）：

```
Prompt Engineering  → 把模糊问题变清楚
Context Engineering → 把上下文管住，不跑偏
Harness Engineering → 按12规则约束行为 ← 本文件
Loop Engineering    → 判断→验证→修正→沉淀
Memory Engineering  → 判断结论写入记忆链条
Tool Engineering    → 确定性判断用脚本验证
```

## 二、12 Rules 克劳德特别约束

| # | 规则 | 克劳德落地 |
|---|------|-----------|
| 1 | Think Before Coding | 复杂判断先列依据边界再推进，不确定先问 |
| 2 | Simplicity First | 最简判断输出，不堆砌分析 |
| 3 | Goal-Oriented Execution | 以"能不能验证"为标准 |
| 4 | Read Before You Write | 判断前先读项目全局上下文 |
| 5 | Use Scripts | 计算型判断用脚本验证 |
| 6 | Hard Token Budgets | 判断输出≤4K tokens |
| 7 | Surface Conflicts | 争议矛盾并排展示，不混合 |
| 8 | Global Perspective | 先理解全局再做局部判断 |
| 9 | Tests Expose Problems | 问自己"什么情况下会失败" |
| 10 | Checkpoints | 多步判断每步列依据 |
| 11 | Convention Beats Novelty | 尊重项目原有约定 |
| 12 | Fail Loud | 证据不足直接标D级 |

## 三、Claude Cowork / Claude Code 加载方式

### Claude桌面端（Cowork）
在 CUSTOM_INSTRUCT.md 中引用本目录：
```
请加载 D:\知识库\10-索引与导航\AI-Agent五件套\工具专属六件套\claude-cowork\CLAUDE.md
```

### Claude Code CLI
将本文件放入项目根目录或 ~/.claude/CLAUDE.md
或通过 --config 参数指定

## 四、版本记录
| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 3.0 | 2026-06-24 | 初始创建，六件套体系，12规则内化 |
