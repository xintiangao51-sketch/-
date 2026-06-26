---
tags: [AI, 索引]
created: 2026-06-12
type: reference
---

# IMA 知识库集成

## 概述
老高使用 IMA (ima.qq.com) 作为知识库后端，管理造价相关文档、标准、案例。

## 技能加载顺序
```bash
# 同时加载老高人设 + IMA 技能
hermes -s xinjiang-cost-engineer -s ima-skill
```

## 凭证配置
- 获取地址：https://ima.qq.com/agent-interface
- 存储位置：`~/.config/ima/client_id` + `~/.config/ima/api_key`
- 或环境变量：`IMA_OPENAPI_CLIENTID` + `IMA_OPENAPI_APIKEY`

## 知识库规划（待搭建）
| 知识库 | 用途 | 内容类型 |
|--------|------|---------|
| 新疆造价定额库 | 定额标准、取费文件 | PDF/网页 |
| 项目案例库 | 历史项目造价数据 | 笔记/Excel |
| 合同范本库 | 施工合同、索赔模板 | Word/PDF |
| 地方政策库 | 自治区住建厅发文 | 网页/PDF |

## IMA 技能目录结构
```
~/.hermes/skills/productivity/ima-skill/
├── SKILL.md              # 主入口（笔记+知识库路由）
├── ima_api.cjs           # API 调用脚本
├── meta.json             # 依赖声明（Node.js ≥18）
├── notes/
│   ├── SKILL.md          # 笔记模块
│   └── references/api.md
└── knowledge-base/
    ├── SKILL.md          # 知识库模块
    ├── references/api.md
    └── scripts/
        ├── preflight-check.cjs  # 文件类型校验
        └── cos-upload.cjs       # COS 上传
```

## 安装备忘
从 zip 安装外部技能时，需检查 `SKILL.md` 中的硬编码路径（如 `.claude/skills/`）并替换为 `$SKILL_DIR/`。

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
