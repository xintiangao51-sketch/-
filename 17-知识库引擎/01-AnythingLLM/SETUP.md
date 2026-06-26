---
tags: ["AI", "合同", "投标", "项目"]
created: 2026-06-24
type: reference
---

# AnythingLLM 部署指南

> 角色：桌面工作台 / 拖拽即用的文档对话  
> 官网：https://anythingllm.com  
> GitHub：https://github.com/Mintplex-Labs/anything-llm （62K stars）

---

## 一、为什么选它

| 优势 | 说明 |
|---|---|
| 桌面安装包 | Windows .exe 一键装，零命令行 |
| 自带向量库 | LanceDB / Chroma 内置，不用单独装 |
| 多文件类型 | PDF / Word / Excel / Markdown / 网页 都能传 |
| 工作区隔离 | 不同项目分不同工作区（造价 / 投标 / 合同分开） |
| API 模式可选 | 本地 LLM (Ollama) 或 接你的火山方舟 / GLM |

---

## 二、安装步骤

### 1. 下载

打开浏览器到：
- https://anythingllm.com/download
- 选 **Windows Desktop** → 下载 `AnythingLLMDesktop.exe`

### 2. 安装

双击 .exe，一路下一步。默认安装位置：`C:\Users\20752\AppData\Local\Programs\AnythingLLM`

数据位置：`C:\Users\20752\AppData\Roaming\anythingllm-desktop\storage`

### 3. 首次启动配置

打开后会问你三个问题：

**问题 1：LLM Provider**

| 选项 | 老高建议 |
|---|---|
| OpenAI | ❌ 用不上 |
| Anthropic | ❌ 用不上 |
| **Generic OpenAI Compatible** | ✅ 推荐——填火山方舟 |
| Ollama | 🟡 想完全离线再选 |

填 Generic OpenAI Compatible 时填：
```
Base URL:    https://ark.cn-beijing.volces.com/api/coding/v3
API Key:     ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c
Model Name:  ark-code-latest
Token limit: 256000
```

**问题 2：Embedding Engine**

| 选项 | 老高建议 |
|---|---|
| AnythingLLM Embedder | ✅ 默认就选这个，开箱即用 |
| Ollama | 🟡 想本地化再换 |

> ⚠待核实：AnythingLLM 也支持"Generic OpenAI"作为 embedding，可以填火山方舟的 doubao-embedding-vision-251215。但 multimodal 端点（/embeddings/multimodal）与 OpenAI 标准 /embeddings 不完全兼容，第一次先用默认。

**问题 3：Vector Database**

选 **LanceDB**（默认），无需配置。

### 4. 创建第一个工作区

点 "+ New Workspace" → 命名 "造价核心" → 拖入 `D:\知识库\01-造价核心\` 的文档即可。

---

## 三、连接 Hermes（可选，进阶）

AnythingLLM 提供 HTTP API，可被 Hermes 工具调用：

```
默认 API 地址：http://localhost:3001/api
API Key：     在 AnythingLLM 设置 → API Keys 中生成
```

获取后填到 `D:\知识库\17-知识库引擎\99-统一检索脚本\config\engines.json` 的 anythingllm 段。

---

## 四、常见坑

| 坑 | 解决 |
|---|---|
| 安装后启动闪退 | 装 .NET 6 Desktop Runtime |
| 拖大 PDF 卡死 | 单文件 ≤50MB，扫描件先用 RAGFlow 处理 |
| 中文乱码 | 设置 → Appearance → Language 选简体中文 |
| 火山方舟报错 401 | API key 没复制全，重新复制不带空格 |

---

## 五、验证

工作区创建后，问一个老高的实际问题：
> "新疆市政 2024 定额里，沥青砼摊铺的人工单价是多少？"

如果给得出引用文档片段 = 装好了。

---

🔗 **知识库引擎**：[[17-知识库引擎/README]]
