---
tags: ["AI", "规范"]
created: 2026-06-24
type: reference
---

# RAGFlow 部署指南

> 角色：重型文档解析 / OCR / 表格抽取 / 规范图集  
> 官网：https://ragflow.io  
> GitHub：https://github.com/infiniflow/ragflow （83K stars）

---

## 一、为什么选它（也为什么"先别急着上"）

| 优点 | 缺点 |
|---|---|
| ✅ DeepDoc 文档解析全网最强 | 🔴 必须 Docker Desktop |
| ✅ 表格、扫描件、图集都能处理 | 🔴 容器要 16GB+ 磁盘 |
| ✅ 引用追溯到原文位置 | 🔴 首次启动 5-10 分钟 |
| ✅ 中文优化好 | 🔴 8GB 内存吃紧 |

建议：**先把 Khoj 和 AnythingLLM 跑通**，等你确实有大量扫描规范 / 图集要处理时再装这个。

---

## 二、前置：装 Docker Desktop

### 1. 下载

https://www.docker.com/products/docker-desktop/  → Windows  → AMD64

### 2. 安装注意

| 选项 | 选啥 |
|---|---|
| WSL 2 backend | ✅ 默认就是这个，保留 |
| Hyper-V | 老系统才需要 |
| 启动时自动启动 | 🟡 看你需要，造价机不常用就别勾 |

装完重启电脑。

### 3. 验证

```powershell
docker --version
docker compose version
```

两个都有版本号即装好。

---

## 三、部署 RAGFlow（slim 版，5GB 镜像够用）

### 1. 拉源码

```powershell
cd D:\知识库\17-知识库引擎\02-RAGFlow
git clone https://github.com/infiniflow/ragflow.git
cd ragflow\docker
```

### 2. 改配置（关键，避免拉满版 80GB 镜像）

打开 `.env` 文件，找到 `RAGFLOW_IMAGE`，确认为 slim 版：
```
RAGFLOW_IMAGE=infiniflow/ragflow:nightly-slim
```

### 3. 启动

```powershell
docker compose -f docker-compose.yml up -d
```

首次启动会拉镜像（~5GB）+ 启动 MySQL/Redis/Elasticsearch/MinIO，耐心等 5-10 分钟。

### 4. 验证

打开浏览器：http://localhost  
注册一个本地账号（不联网，纯本地）

---

## 四、配置 LLM 后端（连火山方舟）

登录后 → 右上角头像 → **Model providers** → **Add LLM**

| 字段 | 填啥 |
|---|---|
| Model Type | LLM |
| Model factory | OpenAI-API-Compatible |
| Model name | ark-code-latest |
| Base url | https://ark.cn-beijing.volces.com/api/coding/v3 |
| API-Key | ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c |
| Max tokens | 256000 |

保存即可。

### Embedding 模型（可选，默认 BAAI/bge-large-zh 已够用）

如要换成火山的：
| 字段 | 填啥 |
|---|---|
| Model Type | embedding |
| Model factory | OpenAI-API-Compatible |
| Model name | doubao-embedding-vision-251215 |
| Base url | https://ark.cn-beijing.volces.com/api/v3 |
| API-Key | （同上）|

> ⚠待核实：RAGFlow 默认调 /embeddings，火山的是 /embeddings/multimodal，可能要在 base url 后加 multimodal 子路径，第一次先用默认 bge-large-zh，跑通再换。

---

## 五、创建知识库

1. 左侧 → Knowledge → Create knowledge base
2. 命名 "工程造价规范"
3. Embedding 模型选 BAAI/bge-large-zh-v1.5（默认）或上面配的 doubao
4. Parser 选 **General / Manual / Paper**（不同文档类型不同 parser）
5. 上传文件 → 等解析（扫描件 1 页约 3 秒）

---

## 六、日常运维

```powershell
# 启动
cd D:\知识库\17-知识库引擎\02-RAGFlow\ragflow\docker
docker compose up -d

# 停止
docker compose down

# 看日志
docker compose logs -f ragflow

# 升级
git pull
docker compose pull
docker compose up -d
```

数据位置：Docker volume，删容器不丢数据。完全删除：`docker compose down -v`（**会删数据，慎用**）

---

## 七、API 接入 Hermes

RAGFlow API 文档：http://localhost/api  
API Key：账号设置 → API → Generate

填到 `99-统一检索脚本\config\engines.json` 的 ragflow 段。

---

## 八、何时装

- 🔴 现在不急着装（Docker 没装、首次部署 30 min）
- 🟢 等你拿到第一批扫描规范 / 图集再装
- 🟡 或者等 AnythingLLM 用不动了再装

---

🔗 **知识库引擎**：[[17-知识库引擎/README]]
