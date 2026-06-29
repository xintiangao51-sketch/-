---
tags: ["AI", "RAG", "知识库引擎", "方案"]
created: 2026-06-27
type: plan
status: 待执行
---

# KC-RAG-001 昕田个人造价知识库RAG构建全案

> 基于 DDC 数据驱动建设 III-3.3.5 RAG 理论 + 知识库引擎三件套现状，输出可落地的 API-RAG 实施方案。
> 版本：v1.0 | 状态：方案待审 | 优先级：P0

---

## 一、现状诊断

### 1.1 知识库资产盘点

| 资产 | 规模 | 格式 | 说明 |
|------|------|------|------|
| D:\知识库\（Obsidian Vault） | ~1,200+ Markdown 文件 | .md | 核心工作知识库，含造价核心/业务中台/合同/投标等 |
| D:\造价知识库\ | 5.6GB，1,172 文件 | PDF/Word/Excel/MD | 历史造价知识归档，含定额/政策/项目资料/图纸 |
| D:\造价工作台\ | — | Excel/Word | 日常造价工作产出 |
| D:\定额库\ | — | 专业格式 | 新疆定额电子版 |
| D:\项目数据\ | — | 混合 | 各项目数据 |
| Obsidian 笔记总量 | ~3 万字 markdown | .md | 持续增长中 |

### 1.2 RAG 引擎部署状况

| 引擎 | 角色 | 当前状态 | 原因 |
|------|------|----------|------|
| **Khoj** | 第二大脑 / Obsidian 联动 | ❌ 未运行 | 端口 42110 无响应 |
| **AnythingLLM** | 桌面工作台 / 文档对话 | ❌ 未运行 | 端口 3001 无响应 |
| **RAGFlow** | 重型文档解析 / OCR/表格抽取 | ❌ 未运行 | 需 Docker，暂未部署 |
| **统一检索脚本** | 跨引擎聚合检索 | 🟡 可运行 | 仅 local_md 模式可用 |
| **Obsidian REST API** | Obsidian 本地接口 | ❌ 未运行 | 端口 27124 无响应 |
| **Obsidian Claudin 插件** | Claude 直接检索 | ⚠️ 可用但非 API | 需手动操作 |

**结论：RAG 三件套目前处于"已规划、未部署"状态。Q3 目标明确要求 7 月底前完成 RAG 引擎部署上线。**

### 1.3 已整理的知识库 RAG 理论文章

知识库中有一篇专门论述 RAG 的文章：

> **《精卡 III-3.3.5：RAG：Intelligent LLM - 可访问公司数据的助理》**
> 位置：`D:\知识库\06-参考文档\DDC数字驱动建设\cards\card_III_3_3_5_RAG_Intelligent_LLM-可访问公司数据的助理.md`
> 来源：《DDC数字驱动建设》第二版（中文版）III 部分 / 章 3.3.5，p145-148
> 证据等级：B 级（机器抽取 + 人工复核）

该文章的核心观点：
- RAG 将 LLM 与企业实时数据结合，无需重新训练模型即可保持高准确性
- 预期出现专门用于工程计算、建筑估算或 CAD 格式数据的专业化模型
- 专业化模型使用起来更快、更准确、更安全，尤其适合造价等对高可靠性和主题深度要求高的专业环境
- RAG 技术由两大核心部分组成：**索引（Indexing）** 和 **检索（Retrieval）**

此外，`D:\知识库\07-AI工具与技能\自动化脚本改进方案.md` 中也详细规划了 RAG 技术选型：
- 向量化方案：bge-small-zh + FAISS/Chroma
- 混合检索策略：关键词 + 语义 + Rerank + 上下文压缩
- 生成策略：LLM + 引用 + 置信度评分

---

## 二、需求定义：怎样的 RAG 才算"能用"？

### 2.1 核心需求（P0）

| 需求 | 说明 | 验收标准 |
|------|------|----------|
| **API 可调用** | 检索和问答必须通过 HTTP API 暴露 | curl/代码可调，返回 JSON |
| **覆盖全知识库** | 能检索 D:\知识库\ + D:\造价知识库\ 全部内容 | 问任何一个项目或定额能出结果 |
| **语义检索** | 支持自然语言提问，不要精确关键词匹配 | "去年特克斯项目的变更签证有哪些" 能搜到 |
| **引用溯源** | 答案必须附原文来源路径 | 每条结果可追溯到具体 .md 文件行或 PDF 页码 |
| **国产 LLM 对接** | 底层 LLM 用火山方舟（ark-code-latest） | 统一 API 地址和 key |

### 2.2 扩展需求（P1）

| 需求 | 说明 | 优先级 |
|------|------|---------|
| 多知识库隔离 | 造价/投标/合同分开的工作区 | P1 |
| OCR 能力 | 扫描件规范/图集可检索 | P1 |
| 增量更新 | 知识库文件变更后自动重索引 | P1 |
| Obsidian 联动 | 在 Obsidian 中直接搜索 | P1 |
| 统一检索聚合 | 同时查询多个引擎，结果合并去重 | P2 |

### 2.3 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 单次检索响应时间 | ≤ 2 秒 | ~3 秒（无 RAG 时） |
| 向量索引首次构建 | ≤ 30 分钟 | 未建 |
| 索引增量更新 | ≤ 30 秒 | 未建 |
| API 可用率 | 99%+（本地服务） | 0% |

---

## 三、方案对比分析

### 3.1 技术路线对比

| 方案 | 核心组件 | 部署难度 | API 能力 | OCR | 适合场景 | 评价 |
|------|----------|----------|----------|-----|----------|------|
| **A: Khoj** | Khoj Server + sentence-transformers | 🟢 极易（pip/msi） | ✅ 原生 REST API | ❌ 无 | Markdown 笔记全文检索 + Obsidian 联动 | ⭐ **首选，第一个装** |
| **B: AnythingLLM** | AnythingLLM Desktop + LanceDB | 🟢 极易（.exe） | ✅ 原生 HTTP API | ❌ 弱 | 文档对话、多工作区 | ⭐ **必装，桌面入口** |
| **C: RAGFlow** | Docker + Elasticsearch + DeepDoc | 🟡 中（需 Docker） | ✅ 原生 REST API | ✅ 强 | 扫描规范、复杂表格、图集 | 🟡 **按需，第三个装** |
| **D: Python 自建** | Chroma/FAISS + FastAPI + bge | 🔴 难（全手动） | ✅ 自建 | ❌ 无 | 深度定制 | ❌ **不推荐，维护成本高** |
| **E: Obsidian REST API + Claudin** | Obsidian + local-rest-api 插件 | 🟢 极易 | ✅ 有 API | ❌ 无 | Obsidian 内快速检索 | ⚠️ **辅助方案** |

### 3.2 推荐组合：三件套分层架构

本方案采用三件套分层策略，不把三个引擎当冗余，而是**分层分工**：

```
                    ┌─────────────────────────────────────┐
                    │       统一检索层 (search.js)         │
                    │    HTTP API 聚合 / 结果合并去重      │
                    └──────┬──────────────┬───────────────┘
                           │              │
              ┌────────────┴────┐  ┌──────┴─────────────┐
              │                 │  │                    │
        ┌─────┴─────┐   ┌──────┴──┴──┐   ┌───────────┴──┐
        │  Khoj     │   │AnythingLLM │   │  RAGFlow     │
        │  Markdown │   │ 文档对话   │   │  OCR/图集   │
        │  向量检索  │   │ 多工作区   │   │  表格抽取    │
        └─────┬─────┘   └──────┬─────┘   └───────────┬──┘
              │               │                      │
              └───────────────┼──────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │    火山方舟 API     │
                    │ ark-code-latest     │
                    │ doubao-embedding    │
                    └────────────────────┘
```

| 层 | 组件 | 职责 | API 暴露 |
|----|------|------|----------|
| **数据接入层** | 文件系统 + Obsidian | 原始 markdown/PDF/Word/Excel | 文件 API |
| **向量索引层** | Khoj（本地）+ AnythingLLM（本地）+ RAGFlow（可选） | 文档分块 → 向量化 → 索引 | 各引擎 HTTP API |
| **统一检索层** | search.js / search.py（已有） | 并行查询 / 聚合 / 去重 / 排序 | 可包装为统一 API |
| **LLM 推理层** | 火山方舟 ark-code-latest | 基于检索片段生成答案 | HTTP API |
| **应用层** | Claude / Obsidian / 浏览器 / 自定义脚本 | 用户交互 | — |

---

## 四、详细实施方案

### 4.1 第一阶段：Khoj 部署（P0，首要任务，预计 30 分钟）

Khoj 是**最适合老高**的引擎——直接索引 D:\知识库\ 全部 markdown，Obsidian 插件双向打通，纯本地运行。

#### 步骤 1.1：安装 Khoj Desktop

```powershell
# 方式 A：桌面应用（推荐，零命令行）
# 下载 https://khoj.dev/downloads → Khoj for Windows (.msi)
# 双击安装 → 启动
# 访问 http://localhost:42110

# 方式 B：pip 安装（备用）
cd D:\知识库\17-知识库引擎\03-Khoj
pip install khoj -i https://pypi.tuna.tsinghua.edu.cn/simple
khoj --anonymous-mode
```

#### 步骤 1.2：配置 LLM 后端（火山方舟）

浏览器打开 http://localhost:42110/server/admin → Chat Models → Add：

| 字段 | 值 |
|------|-----|
| Name | 火山方舟 ark-code |
| Model name | ark-code-latest |
| Model type | openai |
| OpenAI config | Base URL=`https://ark.cn-beijing.volces.com/api/coding/v3`, API Key=`ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c` |
| Max prompt size | 256000 |

#### 步骤 1.3：索引知识库

主界面 → Settings → Content Source → Files：
- Source type: Markdown
- Path: `D:\知识库`
- Watch for changes: ✅ 勾上

点 Sync → 等索引完成（~3 万字约 30 秒）

#### 步骤 1.4：验证 API 可用

```powershell
curl "http://localhost:42110/api/search?q=新疆+市政+沥青砼&t=markdown"
```

返回 JSON 即部署成功。

#### 步骤 1.5：安装 Obsidian 插件

Obsidian → 社区插件 → 搜索 Khoj → 安装 → 配置：
- API URL: `http://127.0.0.1:42110`
- Sync vault: ✅ 勾上

之后在 Obsidian 中按 `Cmd/Ctrl + P` → "Khoj: Search" 即可。

#### 步骤 1.6：生成 API Key（供外部调用）

管理后台 → API → Generate → 复制 key → 填入 `engines.json`

---

### 4.2 第二阶段：AnythingLLM 部署（P0，并行任务，预计 20 分钟）

AnythingLLM 是**桌面文档对话入口**——拖拽 PDF/Word/Excel/MD 就能问，自带向量库。

#### 步骤 2.1：安装 AnythingLLM Desktop

```powershell
# 下载 https://anythingllm.com/download → AnythingLLMDesktop.exe
# 双击安装，一路下一步
```

#### 步骤 2.2：首次配置

启动后三个关键配置：

**LLM Provider** → 选 Generic OpenAI Compatible：
```
Base URL:    https://ark.cn-beijing.volces.com/api/coding/v3
API Key:     ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c
Model Name:  ark-code-latest
Token limit: 256000
```

**Embedding Engine** → 选 AnythingLLM Embedder（默认，开箱即用）

**Vector Database** → 选 LanceDB（默认）

#### 步骤 2.3：创建工作区

创建三个工作区隔离不同业务：

| 工作区 | 数据源 |
|--------|--------|
| `造价核心` | D:\知识库\01-造价核心\ |
| `项目资料` | D:\知识库\09-项目资料\ |
| `投标报价` | D:\知识库\05-投标报价\ |

每个工作区拖入对应目录的文档即可。

#### 步骤 2.4：开启 API

AnythingLLM 设置 → API Keys → 生成 key

验证 API：
```powershell
curl http://localhost:3001/api/health
```

#### 步骤 2.5：扩展索引 D:\造价知识库\（5.6GB）

创建额外工作区 `历史知识库`，将 D:\造价知识库\ 中的关键文件分批次拖入：
- 优先拖入：定额 PDF、政策法规 PDF、已完成项目的结算资料
- PDF 单文件控制在 ≤50MB，超过的先用 RAGFlow 切分

---

### 4.3 第三阶段：RAGFlow 部署（P1，按需，预计 40 分钟）

RAGFlow 在需要处理**扫描件规范/图集/复杂表格**时启用。

#### 步骤 3.1：安装 Docker Desktop

下载 https://www.docker.com/products/docker-desktop/ → Windows → AMD64
安装后重启。

#### 步骤 3.2：部署 RAGFlow slim

```powershell
cd D:\知识库\17-知识库引擎\02-RAGFlow
git clone https://github.com/infiniflow/ragflow.git
cd ragflow\docker
```

修改 `.env` 文件确保：
```
RAGFLOW_IMAGE=infiniflow/ragflow:nightly-slim
```

启动：
```powershell
docker compose -f docker-compose.yml up -d
# 首次拉镜像 ~5GB，等 5-10 分钟
```

#### 步骤 3.3：配置 LLM

浏览器打开 http://localhost → 注册账号 → 设置 → Model providers → Add LLM：

| 字段 | 值 |
|------|-----|
| Model Type | LLM |
| Model factory | OpenAI-API-Compatible |
| Model name | ark-code-latest |
| Base url | https://ark.cn-beijing.volces.com/api/coding/v3 |
| API-Key | ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c |

Embedding 先用默认的 BAAI/bge-large-zh-v1.5（跑通后再试 doubao-embedding）。

#### 步骤 3.4：上传扫描件

创建知识库 → 命名 `规范图集` → 上传扫描 PDF → DeepDoc 自动解析 → 测试检索

---

### 4.4 第四阶段：统一检索层配置（P0，与一二阶段并行，预计 10 分钟）

统一检索脚本已经写好，只需配置 API key。

#### 步骤 4.1：更新 engines.json

编辑 `D:\知识库\17-知识库引擎\99-统一检索脚本\config\engines.json`：

```json
{
  "engines": {
    "khoj": {
      "enabled": true,
      "url": "http://localhost:42110",
      "api_key": "<从 Khoj 后台获取的 key>"
    },
    "anythingllm": {
      "enabled": true,
      "url": "http://localhost:3001",
      "api_key": "<从 AnythingLLM 生成 key>",
      "workspace": "造价核心"
    },
    "ragflow": {
      "enabled": false,
      "url": "http://localhost",
      "api_key": "",
      "kb_id": ""
    },
    "local_md": {
      "enabled": true,
      "root": "D:\\知识库",
      "exclude_dirs": [".obsidian", ".archive", "99-归档库"]
    }
  },
  "output": {
    "dir": "D:\\知识库\\17-知识库引擎\\99-统一检索脚本\\output",
    "save_md": true,
    "top_per_engine": 8
  }
}
```

#### 步骤 4.2：验证统一检索

```powershell
cd D:\知识库\17-知识库引擎\99-统一检索脚本
node search.js "特克斯阳光谷 变更签证"
```

输出应当包含来自 Khoj + AnythingLLM + 本地全文的结果。

---

### 4.5 第五阶段：对外暴露 API 接口（P0，核心目标）

#### 方案：将统一检索脚本包装为 HTTP API 服务

这是实现"需要 API 的那种"RAG 的核心步骤。知识库里已有 search.js 做检索聚合，只需在外面包一层 FastAPI/Express 服务。

##### 方式 A（推荐）：Node.js Express API 服务

```javascript
// D:\知识库\17-知识库引擎\api-server\server.js
const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
app.use(express.json());

// POST /api/rag/search — 检索知识库
app.post('/api/rag/search', (req, res) => {
  const { query, top_k = 8, engines = ['local_md', 'khoj', 'anythingllm'] } = req.body;
  if (!query) return res.status(400).json({ error: 'query is required' });
  
  // 调用 search.js 获取结果
  const child = spawn('node', [
    path.join(__dirname, '..', '99-统一检索脚本', 'search.js'),
    query
  ], { shell: true });
  
  let stdout = '', stderr = '';
  child.stdout.on('data', d => stdout += d);
  child.stderr.on('data', d => stderr += d);
  
  child.on('close', (code) => {
    if (code !== 0) return res.status(500).json({ error: stderr });
    res.json({ query, results: parseOutput(stdout), elapsed: extractElapsed(stdout) });
  });
});

// POST /api/rag/ask — 基于检索结果回答问题
app.post('/api/rag/ask', async (req, res) => {
  const { question, top_k = 5 } = req.body;
  if (!question) return res.status(400).json({ error: 'question is required' });
  
  // 1. 先检索
  const searchResults = await callSearch(question, top_k);
  // 2. 构建 Prompt（含上下文片段）
  const context = searchResults.map(r => `【${r.title}】\n${r.snippet}`).join('\n\n');
  const prompt = `基于以下知识库内容回答问题。如果知识库中没有相关信息，请如实说明。\n\n知识库内容：\n${context}\n\n问题：${question}\n\n回答：`;
  // 3. 调火山方舟生成答案
  const answer = await callLLM(prompt);
  // 4. 返回
  res.json({ question, answer, sources: searchResults });
});

app.listen(3002, () => console.log('RAG API Server running on http://localhost:3002'));
```

**用法示例：**
```powershell
# 检索
curl -X POST http://localhost:3002/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query":"新疆市政沥青砼定额单价"}'

# 问答
curl -X POST http://localhost:3002/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"特克斯阳光谷项目的变更签证有哪些？"}'
```

##### 方式 B（备选）：Python FastAPI 服务

```python
# D:\知识库\17-知识库引擎\api-server\server.py
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess, json, re

app = FastAPI(title="昕田造价知识库 RAG API")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 8

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

@app.post("/api/rag/search")
async def search(req: SearchRequest):
    result = subprocess.run(
        ["node", "D:\\知识库\\17-知识库引擎\\99-统一检索脚本\\search.js", req.query],
        capture_output=True, text=True, timeout=15
    )
    return {"query": req.query, "output": result.stdout}

@app.post("/api/rag/ask")
async def ask(req: AskRequest):
    # 1. 检索
    result = subprocess.run(
        ["node", "D:\\知识库\\17-知识库引擎\\99-统一检索脚本\\search.js", req.question],
        capture_output=True, text=True, timeout=15
    )
    # 2. 调用火山方舟 LLM 生成回答
    import requests
    # ...（调用火山方舟 API 生成答案）
    return {"question": req.question, "sources": result.stdout}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
```

#### 直接调用三件套原生 API

如果不想走统一检索层，各引擎也有原生 API 可直接调用：

**Khoj API：**
```powershell
# 检索
curl "http://localhost:42110/api/search?q=新疆+市政+沥青砼&t=markdown&n=5"

# 聊天
curl -X POST http://localhost:42110/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"新疆2024定额中混凝土章节的说明","stream":false}'
```

**AnythingLLM API：**
```powershell
# 工作区聊天（需先建工作区）
curl -X POST http://localhost:3001/api/v1/workspace/造价核心/chat \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"message":"查一下特克斯项目的人工单价","mode":"chat"}'
```

**RAGFlow API：**
```powershell
# 检索知识库
curl -X POST http://localhost/api/v1/retrieval \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"question":"冬季施工增加费费率","kb_id":"<kb-id>","top_k":5}'
```

#### API 接入 Claude 工作流

这是最关键的一步——让 Claude 在回答造价问题时能自动调 RAG API 获取知识库内容。

```yaml
# 在 D:\Claude-3p\CLAUDE.md 或其他配置中加入 RAG API 工具调用说明：
# 当需要查定额、历史项目、合同条款时，自动调
# POST http://localhost:3002/api/rag/search 获取相关片段
```

Claude（当前对话环境）在回答造价问题时，会基于 soul.md/CLAUDE.md 的指令主动说明"需要查知识库"，但目前尚不能自动调本地 HTTP API。替代方案：
- 用户手动复制问题到 RAG API 返回结果后粘贴回来
- 或将 RAG API 注册为 MCP Tool 供 Claude Desktop 调用

---

## 五、对接贵司 API 密钥体系

### 5.1 火山方舟（LLM + Embedding）

| 用途 | API 地址 | 模型 | API Key |
|------|----------|------|---------|
| LLM 推理 | `https://ark.cn-beijing.volces.com/api/coding/v3` | `ark-code-latest` | `ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c` |
| Embedding（Khoj 默认） | 内置 sentence-transformers | 本地 bge-small-zh | 无 |
| Embedding（AnythingLLM 默认） | 内置 LanceDB embedder | 本地 | 无 |
| Embedding（RAGFlow 默认） | 内置 BAAI/bge-large-zh-v1.5 | 本地 | 无 |

> ⚠ 火山方舟的 doubao-embedding-vision-251215 端点 (`/embeddings/multimodal`) 与 OpenAI 标准 `/embeddings` 不完全兼容，Khoj/AnythingLLM 可能无法直接使用。建议各引擎先用内置本地 embedding 跑通，后续再尝试对接。

### 5.2 API 端口汇总

| 服务 | 端口 | 协议 | 认证方式 |
|------|------|------|----------|
| Khoj API | 42110 | HTTP | API Key 或匿名 |
| AnythingLLM API | 3001 | HTTP | API Key |
| RAGFlow API | 80 | HTTP | API Key |
| 统一检索 API（自建） | 3002 | HTTP | 可选 API Key |
| Obsidian REST API | 27124 | HTTPS | API Key |

### 5.3 安全注意事项

- 所有 API 默认仅监听 `localhost`，不对外暴露
- API Key 存储在 `engines.json` 中，该文件应加入 `.gitignore`
- 不建议在生产环境暴露 3002 端口到公网
- 如需要远程访问，建议通过 VPN 或反向代理（Nginx）加密码保护

---

## 六、运维与日常使用

### 6.1 启动顺序

每次开机后的启动顺序（建议写一个启动脚本）：

```powershell
# D:\知识库\17-知识库引擎\start-rag-engines.ps1
Write-Host "启动 RAG 引擎..." -ForegroundColor Green

# 1. Khoj（后台）
Start-Process -NoNewWindow -FilePath "khoj" -ArgumentList "--anonymous-mode"
Write-Host "  [1/3] Khoj 启动中... http://localhost:42110"

# 2. AnythingLLM（桌面应用，需手动确认）
Write-Host "  [2/3] 请手动启动 AnythingLLM Desktop"
Write-Host "        -> 快捷键或开始菜单"

# 3. RAGFlow（如果已部署）
# docker start ragflow-server 2>$null

# 4. 统一检索 API
# Start-Process -NoNewWindow -FilePath "node" -ArgumentList "D:\知识库\17-知识库引擎\api-server\server.js"

Write-Host "`n各引擎就绪后，运行测试："
Write-Host "  node D:\知识库\17-知识库引擎\99-统一检索脚本\search.js ""测试查询"""
```

### 6.2 日常使用场景

| 场景 | 工具 | 操作 |
|------|------|------|
| 查定额单价 | RAG API 或 Khoj | `curl -X POST http://localhost:3002/api/rag/search -d '{"query":"沥青砼 AC-13 定额单价"}'` |
| 找历史项目资料 | Khoj / Obsidian 插件 | Obsidian 内 Cmd+P → Khoj Search → "哈密国源 综合单价" |
| 分析合同条款 | AnythingLLM | 拖合同 PDF 到「合同审查」工作区 → 直接提问 |
| 查变更签证 | 统一检索脚本 | `node search.js "特克斯 签证 变更"` |
| 读扫描规范 | RAGFlow | 上传扫描 PDF → 知识库内搜索 |
| 做投标报价 | AnythingLLM + Claude | 检索类似项目报价 → 复制到 Claude 分析 |

### 6.3 维护计划

| 频率 | 任务 | 工具 |
|------|------|------|
| 每周 | 检查引擎运行状态 | `start-rag-engines.ps1` 健康检查 |
| 每月 | 清理检索缓存和日志 | 手动清理 output 目录 |
| 每月 | Khoj 增量索引 | 自动（Watch 模式已开） |
| 每季度 | 重新索引全库 | Khoj 设置 → Force Re-sync |
| 每次新增项目 | 将项目资料拖入 AnythingLLM 对应工作区 | 手动 |

---

## 七、三件套决策矩阵（快速判断用哪个）

| 你的需求 | 推荐引擎 | 为什么 |
|----------|----------|--------|
| 日常搜索 markdown 笔记 | Khoj | 直接索引 D:\知识库，Obsidian 联动 |
| 拖个 PDF 问问题 | AnythingLLM | 桌面拖拽即用，不需要导入 |
| 扫描的规范书/图集 | RAGFlow | DeepDoc OCR 最强 |
| 同时在多个引擎搜 | 统一检索脚本 | 自动聚合结果 |
| Claude 需要查知识库 | RAG API（暂手动） | HTTP API 供 Claude 调用 |

---

## 八、实施路线图

```
Phase 1（立即 · 30分钟）                    Phase 2（今天 · 20分钟）
┌─────────────────────┐                    ┌─────────────────────┐
│ ✅ 装 Khoj          │                    │ ✅ 装 AnythingLLM   │
│ ✅ 配火山方舟        │ ──── 可并行 ────→ │ ✅ 创建三个工作区    │
│ ✅ 索引 D:\知识库    │                    │ ✅ 配 LLM + Embed   │
│ ✅ 装 Obsidian 插件  │                    │ ✅ 开启 API          │
│ ✅ 验证 API          │                    │ ✅ 拖入造价知识库    │
└──────────┬──────────┘                    └──────────┬──────────┘
           │                                          │
           └──────────────┬───────────────────────────┘
                          │
              Phase 3（按需 · 40分钟）
              ┌─────────────────────┐
              │ 🟡 装 Docker Desktop│
              │ 🟡 部署 RAGFlow     │
              │ 🟡 上传扫描件       │
              └──────────┬──────────┘
                         │
              Phase 4（关键 · 15分钟）
              ┌─────────────────────┐
              │ ✅ 配置 engines.json │
              │ ✅ 搭建 RAG API 服务 │
              │ ✅ 验证端到端检索    │
              │ 🟡 注册为 MCP Tool  │
              └─────────────────────┘
```

### 里程碑

| 里程碑 | 时间 | 验收标准 |
|--------|------|----------|
| M1: Khoj 上线 | 立即 | `curl http://localhost:42110/api/search?q=测试` 返回 JSON |
| M2: AnythingLLM 上线 | 今天 | `curl http://localhost:3001/api/health` 返回 200 |
| M3: 统一检索可用 | 今天 | `node search.js "特克斯 签证"` 返回跨引擎结果 |
| M4: API 服务上线 | 今天 | `curl -X POST http://localhost:3002/api/rag/search -d '{"query":"定额"}'` 返回 JSON |
| M5: RAGFlow 部署（可选）| 需要时 | 扫描 PDF 可检索 |

---

## 九、风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| Khoj 索引大文件超时 | 低 | 中 | 先索引 D:\知识库\（3 万字），D:\造价知识库\ 分批次处理 |
| AnythingLLM 大 PDF 卡死 | 中 | 低 | 单文件 ≤50MB，扫描件用 RAGFlow |
| 火山方舟 API 限流 | 低 | 中 | 本地 embedding 不依赖火山，LLM 调用有 256K 上下文窗口 |
| Docker 占用资源过高 | 中 | 中 | RAGFlow 用 slim 版，非必需时不启动 |
| Obsidian REST 端口冲突 | 低 | 低 | 改端口号即可 |

---

## 十、总结

本方案基于知识库已有的 RAG 理论文章（DDC III-3.3.5）和技术积累（三件套部署文档 + 统一检索脚本），提出了一条**从理论到可调 API** 的完整路径：

1. **理论依据**：RAG 技术 = 索引 + 检索，将 LLM 与企业数据结合，适合造价这种高可靠性专业场景
2. **技术选型**：Khoj（主力）+ AnythingLLM（桌面入口）+ RAGFlow（OCR 备用）的三件套分层架构
3. **API 实现**：基于 search.js 包装为 RESTful API 服务（localhost:3002），供 curl/代码/（将来）Claude 调用
4. **LLM 统一**：所有引擎统一对接火山方舟 ark-code-latest，embedding 先用本地模型
5. **落地节奏**：Phase 1-2 今天可完成（Khoj + AnythingLLM），Phase 3 按需，Phase 4 包装 API

**一句话结论：30 分钟装好 Khoj 和 AnythingLLM，再花 15 分钟包装一个 API 服务，昕田的造价知识库 RAG 就能跑起来。**

---

🔗 **相关链接**：
- [[17-知识库引擎/README]] — 三件套总入口
- [[17-知识库引擎/01-AnythingLLM/SETUP]] — AnythingLLM 部署
- [[17-知识库引擎/03-Khoj/SETUP]] — Khoj 部署
- [[17-知识库引擎/02-RAGFlow/SETUP]] — RAGFlow 部署
- [[06-参考文档/DDC数字驱动建设/cards/card_III_3_3_5_RAG_Intelligent_LLM-可访问公司数据的助理]] — RAG 理论原文
- [[07-AI工具与技能/自动化脚本改进方案]] — RAG 技术选型参考
- [[10-索引与导航/AI-Agent五件套/工作手册/系统架构]] — 系统架构
- [[10-索引与导航/AI-Agent五件套/MEMORY]] — 记忆工程关联
