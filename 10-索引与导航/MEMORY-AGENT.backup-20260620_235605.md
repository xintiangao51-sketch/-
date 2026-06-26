---
tags: [参考]
created: 2026-06-22
type: reference
---

# MEMORY-AGENT.md
版本：1.0 候选版  
定位：鼎梁筑 AI Agent 协作体系 L2 温记忆载体

## 说明

本文件用于存放完整项目经验、全量坑点库、交接记录、历史经验和多 Agent 协作复盘。

L1 热记忆只保留高频偏好、当前项目、强规则。  
L2 温记忆记录完整过程和可复用经验。  
L3 冷记忆存放原始资料、规范、模板、案例。

## 写入原则

必须先生成记忆草案，经鼎梁筑确认后再写入。

应写入：

- 长期偏好
- 稳定规则
- 项目事实
- 已验证工具配置
- 反复出现的坑点
- 可复用模板和流程
- 多 Agent 协作经验

不写入：

- 未确认猜测
- 临时参数
- 过期价格
- 密钥、账号、密码
- 涉密原文
- 情绪化表达
- 未验证模型判断

## 记录模板

```md
## YYYY-MM-DD · 任务名称

任务来源：
参与 Agent：
项目 / 场景：

### 已确认事实
- 

### 新增规则
- 

### 工具坑点
- 

### 可复用流程
- 

### 交接记录
- 

### 后续待办
- 
```

## 初始记录

### 2026-06-20 · AI Agent 五件套建立

已建立五件套主目录：`D:\知识库\10-索引与导航\AI-Agent五件套\`

五件套文件：

- `SOUL.md`
- `AGENTS.md`
- `HERMES_PROFILE.md`
- `CLAUDE_CODE_PROFILE.md`
- `CODEX_PROFILE.md`

辅助文件：

- `CHANGELOG.md`
- `DEPLOYMENT.md`

关键规则：Hermes 调明白，Claude Code 想明白，Codex 做明白。长期记忆优先级高于对应 Agent Profile。


---
## L1->L2 down-sink [20260620_234745]

### D盘资料总量：13,396个文件（4,705 PDF / 1,561 DWG /
D盘资料总量：13,396个文件（4,705 PDF / 1,561 DWG / 1,588 Excel / 810 Word）。项目覆盖2022-2026年约20+个新疆工程：G0711乌尉高速、G217图木舒克、昌吉地质灾害、喀什体校、米兰道路、博乐护坡、米东煤矿、鄯善启创、特克斯安装、通衢隧道、青河G331等。造价工作台位于D:\造价工作台，含6引擎架构（OCR→组价→审核→风险→搜索→UI）。D盘知识库备份位于D:\造价知识库\。

### Agent本机盘点（2026-06-19）：Claude Code v2.1.1
Agent本机盘点（2026-06-19）：Claude Code v2.1.181，路径 C:\Users\20752\AppData\Roaming\npm\claude.CMD；~/.claude/skills 当前0个用户技能，~/.claude/plugins/marketplaces 缓存29个Claude官方/插件技能，Claude MCP无配置、plugin无已安装。Codex CLI 0.139.0，路径 C:\Users\20752\AppData\Roaming\npm\codex.CMD；~/.codex/skills 有102个用户技能，~/.codex全量SKILL.md约888个；Codex MCP启用 codegraph、codex-security、node_repl，插件启用 browser/chrome/computer-use/latex。tmux未安装/未发现。

### 新疆启创项目Excel分析结果：
新疆启创项目Excel分析结果：
- 文件1（土建工程量清单及报价表.xlsx）：13个Sheet，清单结构=序号|项目编码|项目名称|项目特征描述|计量单位|工程量|综合单价|合价
- 文件2（直接费人材机报价表.xlsx）：3个Sheet（土建直接费表/安装直接费表/人材机汇总）
- 土建直接费表列结构(14列)：序号|建/构筑物|分部工程|项目编码|项目名称|项目特征描述|单位|工程量|综合单价|合价|直接费|人工费|材料费|机械费
- 关键公式：K=IF(J>0,ROUND(J/1.46,2),"")【直接费=合价/1.46】；L=IF(K>0,ROUND(K*0.3,2),"")【人工费=直接费*0.3】；M=IF(K>0,ROUND(K*0.55,2),"")【材料费=直接费*0.55】；N=IF(K>0,ROUND(K*0.15,2),"")【机械费=直接费*0.15】
- 固定30:55:15比例估算人材机，需要替换为按专业分类的合理比例
- 措施项目编码特征：含011707/031301/031302/B99等前缀，名称含"措施""临时""夜间""二次搬运""冬雨季""已完工程""定位复测""检验试验""特殊地区""档案编制"等

### 直接费表重构经验（已存入xinjiang-cost-engineer技能）：
直接费表重构经验（已存入xinjiang-cost-engineer技能）：
- 土建直接费表+安装直接费表的重构处理已标准化：读取→过滤措施项/零报价→按专业比例拆分人材机→保留公式→验证
- 人材机比例不再用固定30:55:15，改为按分部工程关键词匹配（土石方20:5:75，混凝土20:60:20，钢筋15:75:10等）
- 关键技术细节：用first_data_row变量记录首个数据行实际行号（因分组标题行穿插，不能用total+2估算）；直接费=合价/1.46为原表公式逻辑；汇总行动态SUM；跨表引用用实际汇总行号
- 验证必做：合价交叉计算、措施项残留检查、零报价残留检查、人材机比例归零检查、汇总公式范围核对

### D盘工作区：D:\Hermes Agent中文端\workspace 已创建，用
D盘工作区：D:\Hermes Agent中文端\workspace 已创建，用于存放工作文件。C盘可用空间103GB（200G总盘），满足>=90GB要求。

### 桌面 Hermes 源码已从 C:\Users\20752\Desktop\he
桌面 Hermes 源码已从 C:\Users\20752\Desktop\hermes-agent\hermes-agent-main 迁移至 D:\Hermes Agent中文端\workspace\hermes-agent-main

### agency-agents 仓库位于 C:\Users\20752\Docume
agency-agents 仓库位于 C:\Users\20752\Documents\Codex\2026-06-14\gh-repo-clone-msitarzewski-agency-agents\agency-agents；已为 Codex 安装工程行业代理人到 C:\Users\20752\.codex\agents，并在 D:\知识库\soul.md 建立身份系统，角色模板库位于 D:\知识库\agent-role-templates。

### Camofox Browser CLI 可通过 `npx --yes camof
Camofox Browser CLI 可通过 `npx --yes camofox-browser@2.4.5` 使用；常用命令含 navigate/screenshot/fill/scroll/extract-structured/get-text/get-links/eval/search/session/cookie/download/auth/server/annotate/health/run/console/errors/trace。

### Camofox Browser CLI 裸运行 `npx --yes camof
Camofox Browser CLI 裸运行 `npx --yes camofox-browser@2.4.5` 会启动服务进程；若长期无导航/无浏览器连接，会因 `IDLE_TIMEOUT` 退出，常见退出码 3840。实际使用应调用子命令如 `navigate`、`get-text`、`screenshot`、`health`，或用 `server` 管理服务。

### 哈密国源综合服务中心项目知识库路径：D:\知识库\09-项目资料\哈密国源综合服
哈密国源综合服务中心项目知识库路径：D:\知识库\09-项目资料\哈密国源综合服务中心，综合梳理文件为“项目梳理-图纸清单招投标体系.md”。项目全称=国源电力哈密煤电公司综合能源集控服务中心工程施工，招标编号CEZB260002551，招标人国网能源哈密煤电有限公司，招标代理国家能源集团国际工程咨询有限公司，国内资格后审公开招标，综合评估法（商务10%/技术40%/价格50%），固定总价合同，工期22个月且含冬休期。

### 哈密国源综合服务中心关键造价数据：建筑面积19300㎡（新能源集控中心12920
哈密国源综合服务中心关键造价数据：建筑面积19300㎡（新能源集控中心12920㎡、明珠供热调度中心6380㎡），最高限价86784237.02元，中标单位广西建工集团第四建筑工程有限责任公司，中标价74808671.53元（约限价86.2%、下浮13.8%、单方约3876元/㎡）。投标报价：新能源54277559.69元（单方4201元/㎡）、明珠20531111.84元（单方3217元/㎡）。暂列金额400万元，专业工程暂估价480万元（迁改290万、泛光50万、智能会务30万、室内弱电50万、抗震支架30万、净水30万），其他费用92.8万元包干。

### 哈密国源综合服务中心图纸/清单要点：招标图纸清单共17张DWG（建筑5、结构3、
哈密国源综合服务中心图纸/清单要点：招标图纸清单共17张DWG（建筑5、结构3、暖通4、电气2、给排水3），版本为2026.03.19~20预审版；当前工作区未定位到原始DWG，仅有图纸清单笔记，精提量需补齐原始图纸。清单为GB50500-2013体系，新能源含建筑/装饰/电气/暖通/消防报警/弱电监控/给排水/消防水/太阳能/设备/室外工程；设备费393.42万元，其中新能源357.12万元，空气源热泵12台×18万=216万元为大头。

### 鼎梁筑项目现有资产：工作区约54个文件，含12个Markdown、8个Excel
鼎梁筑项目现有资产：工作区约54个文件，含12个Markdown、8个Excel、8个Word、9个Python、静态HTML看板。已具备服务目录/报价规则、客户问题收集表、追问清单、免费样品模板、服务确认单、客户线索台账、客户问题/任务处理/收款复购3合1看板；validate_mvp.py验证显示MVP关键文件齐全，市场验证表含80条需求信号（签证变更57、现场报价快算23）。招标公告采集和Freelancer任务筛选脚本作为副线备用。

