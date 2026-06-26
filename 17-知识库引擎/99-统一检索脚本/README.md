---
tags: ["AI"]
created: 2026-06-24
type: reference
---

# 统一检索脚本 · README

> 跨 Khoj / AnythingLLM / RAGFlow / 本地 markdown 一句话检索  
> 位置：D:\知识库\17-知识库引擎\99-统一检索脚本\

---

## 快速开始

```powershell
cd D:\知识库\17-知识库引擎\99-统一检索脚本

# Node 版（推荐）
node search.js "新疆 市政 沥青砼 单价"

# Python 版
python search.py "新疆 市政 沥青砼 单价"
```

> ⚠ 三件套一个都没装也能跑——脚本会自动跳过未配置的引擎，至少 `local_md`（本地 D:\知识库 全文搜）总是能用。

---

## 输出

- 控制台：表格摘要 + 每条结果片段
- 文件：`output\<时间戳>_<查询词>.md` 保存完整报告

---

## 配置文件

`config\engines.json`

| 字段 | 含义 | 何时改 |
|---|---|---|
| engines.local_md.enabled | 本地 markdown 全文搜 | 默认开 |
| engines.local_md.exclude_dirs | 排除的子目录 | 想跳过某些目录改这里 |
| engines.khoj.enabled / url | Khoj 服务 | 装好 Khoj 后填 |
| engines.khoj.api_key | Khoj API key | 后台生成的 key |
| engines.anythingllm.url / api_key / workspace | AnythingLLM | 装好后填 |
| engines.ragflow.url / api_key / kb_id | RAGFlow | 装好后填 |
| output.top_per_engine | 每个引擎返回几条 | 默认 8 |

---

## 设计要点

| 要点 | 实现 |
|---|---|
| 并行查询 | Node 用 Promise.all、Python 用线程 |
| 单引擎失败不阻塞 | 各引擎独立 try/catch |
| 超时控制 | 默认 8s 每引擎 |
| 无外部依赖 | Node 用内置 fetch，Python 用 stdlib urllib |
| 中文友好 | UTF-8 全程，文件名安全转义 |

---

## 常见问题

| 问题 | 解决 |
|---|---|
| 控制台输出乱码 | 终端切 UTF-8：`chcp 65001` |
| Node fetch 报错 | Node ≥18 才有原生 fetch，老版本升一下 |
| 本地 markdown 搜不到 | 检查 config 里的 root 路径，确认查询词在文件里真的存在 |
| 三件套都连不上 | 检查 url 端口、检查防火墙、`curl http://localhost:42110` 看是否能通 |

---

## 与 Hermes 联动

把这个脚本注册为 Hermes 工具（可选，进阶）：

`~/.hermes/plugins/kb-search/plugin.yaml`：
```yaml
name: kb-search
tools:
  - name: kb_search
    description: 在三件套知识库中检索
    handler: scripts/run.py
```

之后在 Hermes 对话里说"查一下沥青砼定额"，模型可以自动调这个工具。

> 这个集成不是本轮工作内容，等三件套真跑起来再说。

---

## 维护

| 频率 | 任务 |
|---|---|
| 每次新装/卸载一个引擎 | 改 `config\engines.json` 的 `enabled` |
| 每次换 API key | 改对应引擎的 `api_key` |
| output 目录满了 | 手动清理或定期归档到 99-归档库 |

---

变更：
- 2026-06-23 初版（鼎梁筑创建，对接 Khoj/AnythingLLM/RAGFlow/local_md 四源）

---

🔗 **知识库引擎**：[[17-知识库引擎/README]]
