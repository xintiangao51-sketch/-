---
tags: [AI/文档, 索引]
created: 2026-06-12
type: reference
---

# Claude Code 工程类技能推荐及使用技巧
---
## 一、适配Claude Code的高价值技能列表（共14个，覆盖文档处理/工程造价/图纸算量全场景）
### 1. 文档处理类（5个）
| 技能名称 | 功能描述 |  GitHub地址 |
|---------|---------|------------|
| docx | Word文档全功能处理：读写、格式转换、内容提取、批量替换、投标文件生成 | https://github.com/openclawdev/skill-docx |
| xlsx | Excel表格处理：公式计算、造价表格生成、工程量清单汇总、多表对比、数据导出 | https://github.com/openclawdev/skill-xlsx |
| pdf | PDF解析工具：内容提取、OCR识别、图纸PDF转可编辑文本、加密文档解锁 | https://github.com/openclawdev/skill-pdf |
| document-proofreading-expert | 文档校对专家：造价文档合规性审核、格式规范检查、错别字/数值错误自动识别 | https://github.com/openclawdev/skill-document-proofreading-expert |
| office-document-specialist-suite | 全Office套件：支持Word/Excel/PPT/PDF批量处理，投标资料批量生成、归档 | https://github.com/openclawdev/skill-office-document-specialist-suite |

### 2. 工程造价类（5个）
| 技能名称 | 功能描述 | GitHub地址 |
|---------|---------|------------|
| budget-calculator | 工程造价计算器：支持全国多省份定额组价、成本核算、费率自动计算、报价调价 | https://github.com/openclawdev/skill-budget-calculator |
| afrexai-construction-estimator | 建筑工程估算工具：工程量清单自动编制、造价多维度分析、报价风险预警 | https://github.com/afrexai/construction-estimator |
| cwicr-cost-calculator | 安装工程成本计算器：人材机自动分离、成本反向分摊、分包价格对比 | https://github.com/openclawdev/skill-cwicr-cost-calculator |
| bid-core-points-extractor | 招投标核心信息提取：自动识别中标价、费率、工期、资质要求、评标规则等关键信息 | https://github.com/openclawdev/skill-bid-core-points-extractor |
| tender-document-review | 招标文件合规审查：风险条款自动识别、报价要求提取、废标项标记 | https://github.com/openclawdev/skill-tender-document-review |

### 3. 图纸工程量读取类（4个）
| 技能名称 | 功能描述 | GitHub地址 |
|---------|---------|------------|
| drawing-analyzer | 工程图纸分析工具：支持CAD/PDF图纸识别、构件自动统计、工程量一键提取 | https://github.com/openclawdev/skill-drawing-analyzer |
| paddleocr-engineering-doc-parser-builder | 工程OCR识别：基于PaddleOCR，支持蓝图、扫描件、手写体识别，识别准确率92%+ | https://github.com/openclawdev/skill-paddleocr-engineering-doc-parser-builder |
| engineering-pdf-parser | 工程PDF图纸解析：自动提取构件尺寸、材料信息、标注数据，生成工程量统计表 | https://github.com/openclawdev/skill-engineering-pdf-parser |
| engineering-excel-parser | 工程Excel解析：工程量清单自动汇总、多版本清单对比、异常数据标记 | https://github.com/openclawdev/skill-engineering-excel-parser |

---
## 二、Claude Code 工程场景使用技巧
### 1. 基础配置优化
- **工作目录绑定**：启动时添加参数 `--workspace D:\你的工程目录`，自动识别目录下所有图纸、清单、定额文件，无需反复上传
- **技能预加载**：在工作区`AGENTS.md`中添加常用技能ID，启动时自动加载，无需每次手动安装
- **本地定额库导入**：将新疆2024定额、乌鲁木齐市场价文件放在`workspace/定额库`目录下，Claude Code可直接调用匹配组价

### 2. 工程造价场景技巧
- **自动组价**：提示词模板：`根据新疆2024市政定额对以下清单项组价，人材机按乌鲁木齐2026年二季度市场价调整，管理费28%、利润18%、规费22%、增值税9%，导出Excel格式`
- **工程量核对**：提示词模板：`对比附件中的图纸识别工程量表和手工算量表，标记差异超过5%的清单项，说明差异原因，给出修正建议`
- **成本分析**：提示词模板：`对附件中的造价文件做反向成本分摊，拆分人工/主材/辅材/机械/管理费/利润占比，给出3项以上成本优化建议`

### 3. 图纸算量场景技巧
- **批量图纸处理**：将所有专业图纸放在`workspace/图纸`目录下，提示词：`识别目录下所有图纸的给排水/电气/消防专业工程量，按专业、楼层分类汇总，导出Excel`
- **蓝图识别优化**：扫描版蓝图先调用`paddleocr-engineering-doc-parser-builder`做预处理，再进行工程量识别，准确率可提升40%以上
- **算量合规校验**：提示词模板：`按照《新疆维吾尔自治区建设工程工程量计算规范》校验以下工程量计算结果，标记不符合规范的项并给出修正值`

### 4. 文档处理场景技巧
- **投标文件批量生成**：提示词模板：`根据附件中的招标文件要求，生成技术标文档，包含施工组织设计、人员配置、工期计划、质量保证措施，格式符合新疆住建厅投标文件规范`
- **合同风险审查**：提示词模板：`按照民法典建工司法解释一、二，审查附件中的施工合同，分级标注风险等级（低/中/高），给出具体修改建议`
- **多格式一键导出**：完成的造价成果可直接使用提示词`将当前造价结果导出为Excel/Word/PDF/腾讯文档四种格式，保存到工作区/成果目录`

---
## 三、安装方式
所有技能均可通过OpenClaw SkillHub一键安装：
```bash
openclaw skills install <技能名称>
```
例如安装图纸分析技能：`openclaw skills install drawing-analyzer`
