# CHANGELOG.md

## 2026-06-20 · V1.0 候选版

### 新增

- 建立鼎梁筑 AI 工程协作体系五件套：
  - `SOUL.md`
  - `AGENTS.md`
  - `HERMES_PROFILE.md`
  - `CLAUDE_CODE_PROFILE.md`
  - `CODEX_PROFILE.md`
- 建立三 Agent 分工：Hermes 调明白，Claude Code 想明白，Codex 做明白。
- 写入三大工程方法：Prompt Engineering、Context Engineering、Loop Engineering。
- 写入 90 分质量门槛和验证评分机制。
- 写入动态费率规则：缺合同、招标、政策、项目策略依据时标 `⚠费率待确认`。
- 写入 L1/L2/L3 记忆分层机制。

### 修订

- `AGENTS.md` 从全量手册瘦身为公共铁律，不重复三个 Profile 的执行细节。
- 冲突优先级按鼎梁筑最新决策调整：长期记忆高于对应 Agent Profile。
- `HERMES_PROFILE.md` 消化 B-11 至 B-16：
  - 收敛“做完即忘”表述。
  - 将运行时配置改为附录 A。
  - 记忆草案增加过滤条件。
  - 压缩阈值保留各角色标准，但交接前强制压缩。
  - 调度评分表调整为任务分对、状态清楚、交接完整、上下文压缩、风险控制、闭环推进。
  - Codex 回流验收补接 `扣分原因`。

### 迁移

- 五件套主目录确定为：`D:\知识库\10-索引与导航\AI-Agent五件套\`
- `MEMORY-AGENT.md` 独立放置于：`D:\知识库\10-索引与导航\MEMORY-AGENT.md`
- 旧 Hermes Profile 原址保留，不删除：`D:\知识库\07-AI工具与技能\AI协作体系\`

### 待办

- 各 Agent 实际挂载路径需按真实运行环境继续验证。
- 旧目录确认无引用后再清理或改为跳转说明。
