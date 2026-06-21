# DEPLOYMENT.md
版本：1.0 候选版

## 目标

说明五件套文件如何被 Hermes Agent、Claude Code、Codex 使用。此文件记录部署和挂载方式，不写入角色规则。

## 主目录

```md
D:\知识库\10-索引与导航\AI-Agent五件套\
```

## 文件清单

```md
SOUL.md
AGENTS.md
HERMES_PROFILE.md
CLAUDE_CODE_PROFILE.md
CODEX_PROFILE.md
CHANGELOG.md
DEPLOYMENT.md
```

## L2 记忆文件

```md
D:\知识库\10-索引与导航\MEMORY-AGENT.md
```

`MEMORY-AGENT.md` 是记忆载体，不属于五件套规则文件。

## 推荐加载方式

### Hermes Agent

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `HERMES_PROFILE.md`
4. `MEMORY-AGENT.md`

Hermes 是调度者，负责维护状态卡、交接卡、记忆草案和分层落盘。

### Claude Code

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `CLAUDE_CODE_PROFILE.md`

可通过项目级 `CLAUDE.md` 或启动提示词引用本目录。Claude Code 只主责判断，不主责文件成品化和调度。

### Codex

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `CODEX_PROFILE.md`

可通过项目级 `AGENTS.md` 或启动提示词引用本目录。Codex 主责执行交付、文件生成、数据转换和验证评分。

## 旧目录处理

旧目录：

```md
D:\知识库\07-AI工具与技能\AI协作体系\
```

处理原则：

1. 定稿阶段不删除旧目录。
2. 旧目录文件已备份到五件套 `_archive`。
3. 确认无引用后，可将旧目录文件改为跳转说明或归档。

## 挂载校验清单

- Hermes 能读取五件套主目录。
- Claude Code 能收到 `CLAUDE_CODE_PROFILE.md`。
- Codex 能收到 `CODEX_PROFILE.md`。
- 三 Agent 均能看到 `SOUL.md` 和 `AGENTS.md`。
- `MEMORY-AGENT.md` 与五件套规则文件分离。
- 冲突优先级以 `AGENTS.md` 为准。
