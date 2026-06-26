---
tags: [参考]
created: 2026-06-22
updated: 2026-06-24
type: reference
version: 3.0
---

# DEPLOYMENT.md
版本：3.0

## 目标

说明六件套文件（v3.0升级）如何被四个Agent使用。此文件记录部署和挂载方式，不写入角色规则。

## 主目录

```md
D:\知识库\10-索引与导航\AI-Agent五件套\
```

## 文件清单（v3.0）

### 核心规则文件（六件套）

```md
SOUL.md                   # 总灵魂，v3.0，六维方法论 + 12规则
AGENTS.md                 # 公共铁律，v3.0，12规则明细
MEMORY.md                 # 记忆工程，v1.0（v3.0新增第六件）
HERMES_PROFILE.md         # 赫尔墨斯-调度部，v3.0
CLAUDE_CODE_PROFILE.md    # 克劳德-研判部，v3.0
CODEX_PROFILE.md          # 科德克斯-执行部，v3.0
WORKBUDDY_PROFILE.md      # 沃巴迪-运营部，v3.0
```

### 工作手册（各Agent执行指南）

```md
工作手册\README.md                       # 总索引
工作手册\赫尔墨斯-调度部总监-工作手册.md
工作手册\克劳德-研判部总监-工作手册.md
工作手册\科德克斯-执行部总监-工作手册.md
工作手册\沃巴迪-运营部总监-工作手册.md
```

### 辅助文件

```md
CHANGELOG.md              # 变更日志
DEPLOYMENT.md             # 本文件，部署说明
CUSTOM_INSTRUCT.md        # 通用自定义指令（所有AI工具适用），v2.1
PERSONAL_PROFILE.md       # 个人使用画像，v2.0
协同协议复盘报告_v2.md      # 三→四Agent升级复盘报告
```

## L2 记忆文件

```md
D:\知识库\10-索引与导航\MEMORY-AGENT.md     # L2温记忆
D:\知识库\16-运营数据\                        # L2运营层（沃巴迪专属）
```

`MEMORY-AGENT.md` 是记忆载体，不属于六件套规则文件。

## 推荐加载方式

### Hermes Agent（赫尔墨斯）

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `HERMES_PROFILE.md`
5. `MEMORY-AGENT.md`

Hermes 是调度者，负责维护状态卡、交接卡、记忆草案和分层落盘。多Agent交接时，Hermes是中枢，协调避免文件冲突。

### Claude Code（克劳德）

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `CLAUDE_CODE_PROFILE.md`

可通过项目级 `CLAUDE.md` 或启动提示词引用本目录。Claude Code 只主责判断，不主责文件成品化和调度。

### Codex（科德克斯）

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `CODEX_PROFILE.md`

可通过项目级 `AGENTS.md` 或启动提示词引用本目录。Codex 主责执行交付、文件生成、数据转换和验证评分。

### Workbuddy（沃巴迪）—— v2.0新增

应加载：

1. `SOUL.md`
2. `AGENTS.md`
3. `MEMORY.md`
4. `WORKBUDDY_PROFILE.md`

Workbuddy 主责项目运营、财务收支、数据分析、经验沉淀、迭代规划，同时主责 MEMORY.md 记忆工程体系的维护。挂载知识库后可读取 `D:\知识库\16-运营数据\` 专属目录。

实际挂载路径：`D:\知识库\10-索引与导航\MEMORY-AGENT.md`（L2温记忆），工作目录优先指向 `D:\知识库\16-运营数据\`。

### 通用自定义指令（所有AI工具）

所有AI工具（含第三方工具如Claude桌面端、Qclaw等）应在系统提示词中加载：

```md
CUSTOM_INSTRUCT.md        # 个人指令，v2.1，覆盖全部AI工具通用场景
```

## 旧目录处理

旧目录：

```md
D:\知识库\07-AI工具与技能\AI协作体系\
```

处理原则：

1. 旧目录文件已备份到五件套 `_archive`。
2. 确认无引用后，可将旧目录文件改为跳转说明或归档。

## 挂载校验清单（v3.0）

- [ ] Hermes 能读取六件套主目录
- [ ] Claude Code 能收到 `CLAUDE_CODE_PROFILE.md`
- [ ] Codex 能收到 `CODEX_PROFILE.md`
- [ ] **Workbuddy 能收到 `WORKBUDDY_PROFILE.md`**
- [ ] 四 Agent 均能看到 `SOUL.md`、`AGENTS.md`、`MEMORY.md`
- [ ] `MEMORY-AGENT.md` 与六件套规则文件分离
- [ ] 冲突优先级以 `AGENTS.md` 为准
- [ ] **Workbuddy 工作目录已挂载 `D:\知识库\16-运营数据\`**
- [ ] **Supermemory / Dory 记忆引擎已安装（按需）**（v3.0新增）

## 版本记录

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 1.0 | 2026-06-22 | 三Agent初始部署说明 |
| 2.0 | 2026-06-24 | 四Agent升级：新增Workbuddy加载节，补全文件清单，更新挂载校验 |
| 3.0 | 2026-06-24 | 六件套升级：新增MEMORY.md加载，四Agent加载方式补入MEMORY.md，校验清单更新 |
