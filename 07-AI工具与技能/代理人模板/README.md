# 工程行业代理人角色模板库

> 位置：`D:\知识库\agent-role-templates\construction-industry`  
> 来源：已写入 agency-agents 仓库 `specialized/`，并生成 Codex/OpenCode 集成文件。  
> Codex 安装目录：`C:\Users\20752\.codex\agents`

## 推荐装配结论

| 层级 | 代理人 | 文件 | 用途 |
|---|---|---|---|
| 身份锚点 | soul.md | `D:\知识库\soul.md` | 老高/昕田长期身份系统 |
| 核心 | ZK Steward | `zk-steward.toml` | 知识库整理、项目经验沉淀 |
| 核心 | Document Generator | `document-generator.toml` | Word/Excel/PDF/PPT 输出 |
| 核心 | Executive Summary Generator | `executive-summary-generator.toml` | 领导摘要、会议纪要、决策建议 |
| 核心 | UI Designer | `ui-designer.toml` | 工程管理看板视觉 |
| 核心 | UX Architect | `ux-architect.toml` | 工作台信息架构/交互流程 |
| 核心 | Frontend Developer | `frontend-developer.toml` | 前端实现 |
| 工程主力 | Xinjiang Construction Cost Estimator | `construction-cost-estimator-xinjiang.toml` | 新疆造价、清单定额、签证结算 |
| 工程主力 | Construction Budget Specialist | `construction-budget-specialist.toml` | 投标报价、商务标、成本底线 |
| 工程主力 | Construction Finance Controller | `construction-finance-controller.toml` | 工程财务、现金流、成本台账 |
| 工程主力 | Construction Legal Contract Reviewer | `construction-legal-contract-reviewer.toml` | 工程合同审查、索赔结算争议 |
| 工程主力 | Construction Civil Engineer CN | `construction-civil-engineer-cn.toml` | 土木/结构、抗震、施工技术 |
| 工程主力 | Construction Site Manager | `construction-site-manager.toml` | 现场进度、质量、安全、签证证据 |
| 工程主力 | Construction Quantity Surveyor | `construction-quantity-surveyor.toml` | 提量、对量、签证工程量、结算量差 |
| 扩展 | Workflow Architect | `workflow-architect.toml` | 审批流/业务流 |
| 扩展 | BIM/GIS Specialist | `bim-gis-specialist.toml` | BIM/GIS/IFC/数字孪生 |
| 扩展 | Supply Chain Strategist | `supply-chain-strategist.toml` | 材料采购、询价比价 |
| 扩展 | Legal Compliance Checker | `legal-compliance-checker.toml` | 通用合规检查 |
| 扩展 | Analytics Reporter | `analytics-reporter.toml` | 数据报表/经营看板 |
| 扩展 | Business Strategist | `business-strategist.toml` | 公司经营和业务策略 |
| 扩展 | Operations Manager | `operations-manager.toml` | 内部运营、制度流程 |

## 任务调用建议

| 任务 | 首选代理人 | 联动代理人 |
|---|---|---|
| 清单组价/签证结算 | Xinjiang Construction Cost Estimator | Quantity Surveyor / Legal Reviewer |
| 投标报价 | Construction Budget Specialist | Finance Controller / Cost Estimator |
| 合同审查 | Construction Legal Contract Reviewer | Finance Controller / Cost Estimator |
| 现金流和利润测算 | Construction Finance Controller | Budget Specialist / Site Manager |
| 图纸提量/对量 | Construction Quantity Surveyor | Civil Engineer / Cost Estimator |
| 施工组织/进度质量安全 | Construction Site Manager | Civil Engineer / Quantity Surveyor |
| 知识库整理 | ZK Steward | Document Generator / Executive Summary Generator |
