---
tags: [Hindsight, 结构化记忆, Hermes, 老高]
type: memory-engine-index
created: 2026-06-14 19:00:14
---

# Hindsight 结构化记忆引擎索引

- 记忆库：`laogao-structured-memory`
- 工作区：`D:\知识库`
- 来源：`C:\Users\20752\AppData\Roaming\cn.org.hermesagent.desktop\runtime\hermes-home\memories\MEMORY.md`、`C:\Users\20752\AppData\Roaming\cn.org.hermesagent.desktop\runtime\hermes-home\memories\USER.md`
- 结构化记录数：**13**

## 记忆分层

|层级|用途|Hindsight标签|
|---|---|---|
|身份/偏好|稳定身份、输出风格、禁用话术|`user`, `output_preferences`|
|造价核心|定额、人工、费率、核验红线|`cost_parameters`|
|项目经验|鄯善启创、直接费表、人材机拆分等|`project_case`, `workflow_experience`|
|环境路径|D盘工作区、知识库、工具安装位置|`workspace_assets`, `workspace_root`|
|工具约束|execute_code沙箱、Claude/Codex代理系统|`tooling`, `tooling_quirks`, `agent_system`|

## 结构化记录

|ID|类别|标题|优先级|标签|
|---|---|---|---:|---|
|memory-001|cost_parameters|新疆造价核心参数|100|laogao, structured-memory, cost_parameters, 新疆造价, 定额, 费率, 人工单价|
|memory-002|output_preferences|输出风格与沟通偏好|95|laogao, structured-memory, output_preferences, 输出偏好, 沟通风格|
|memory-003|workspace_assets|本地资料与工作区|90|laogao, structured-memory, workspace_assets, D盘, 知识库, 造价工作台|
|memory-004|tooling|Claude Code与技能系统|80|laogao, structured-memory, tooling, Claude Code, 技能|
|memory-005|tooling_quirks|执行环境与工具注意事项|85|laogao, structured-memory, tooling_quirks, execute_code, Python, 工具约束|
|memory-006|project_case|新疆启创/鄯善启创项目经验|88|laogao, structured-memory, project_case, 项目案例, 鄯善启创, 人材机|
|memory-007|tooling|Claude Code与技能系统|80|laogao, structured-memory, tooling, Claude Code, 技能|
|memory-008|general_memory|通用记忆|60|laogao, structured-memory, general_memory, 记忆|
|memory-009|general_memory|通用记忆|60|laogao, structured-memory, general_memory, 记忆|
|memory-010|workspace_assets|本地资料与工作区|90|laogao, structured-memory, workspace_assets, D盘, 知识库, 造价工作台|
|memory-011|workspace_assets|本地资料与工作区|90|laogao, structured-memory, workspace_assets, D盘, 知识库, 造价工作台|
|user-001|general_memory|通用记忆|60|laogao, structured-memory, general_memory, 记忆|
|user-002|cost_parameters|新疆造价核心参数|100|laogao, structured-memory, cost_parameters, 新疆造价, 定额, 费率, 人工单价|

## 接入方式

1. Hermes 配置 `memory.provider=hindsight`。
2. Hindsight 配置文件：`C:/Users/20752/AppData/Roaming/cn.org.hermesagent.desktop/runtime/hermes-home/hindsight/config.json`。
3. 批量导入源：`memory_hindsight_ingest.json`。每条记录带 `retain_context` 与 `hindsight_tags`，可用 `hindsight_retain` 写入。
