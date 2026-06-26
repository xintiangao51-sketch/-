---
tags: ["AI", "规范"]
created: 2026-06-24
type: reference
---

# Khoj 部署指南

> 角色：第二大脑 / 全文 markdown 检索 / Obsidian 联动  
> 官网：https://khoj.dev  
> GitHub：https://github.com/khoj-ai/khoj （35K stars）

---

## 一、为什么选它（最适合老高的一个）

| 优势 | 老高用场景 |
|---|---|
| ✅ 直接索引 D:\知识库\ 全部 markdown | 不用搬运，原地索引 |
| ✅ Obsidian 插件双向打通 | 你已经在用 Obsidian |
| ✅ 浏览器扩展剪藏网页 | 论文/规范页面直接入库 |
| ✅ 桌面应用 + 网页 + Emacs/Obsidian | 哪里都能用 |
| ✅ 自带向量化（sentence-transformers） | 无需外部 embedding |

---

## 二、两种装法

### 方式 A：桌面应用（推荐，零命令行）

1. 访问 https://khoj.dev/downloads
2. 下载 **Khoj for Windows**（.msi 安装包）
3. 双击安装 → 启动
4. 访问 http://localhost:42110

### 方式 B：pip 装（适合喜欢命令行）

```powershell
# 进项目目录
cd D:\知识库\17-知识库引擎\03-Khoj

# 装（首次会拉 transformers + torch，约 2GB）
pip install khoj

# 启动
khoj --anonymous-mode
```

启动后 http://localhost:42110

> --anonymous-mode：跳过云端登录，纯本地用。

---

## 三、首次配置

### 1. 接 LLM（火山方舟）

进 http://localhost:42110/server/admin → **Chat Models** → Add

| 字段 | 填啥 |
|---|---|
| Name | 火山方舟 ark-code |
| Model name | ark-code-latest |
| Model type | openai |
| OpenAI config | 新建一个，filled： Base URL=https://ark.cn-beijing.volces.com/api/coding/v3, API Key=ark-e01c74bf-864d-479e-9cc4-a4c02846b10b-8615c |
| Max prompt size | 256000 |

### 2. 索引 D:\知识库\ 全部 markdown

主界面 → **Settings** → **Content Source** → **Files**

| 字段 | 填啥 |
|---|---|
| Source type | Markdown |
| Path | D:\知识库 |
| Watch for changes | ✅ 勾上（自动重索引） |

点 Sync → 等索引（~3 万字 markdown 约 30 秒）

### 3. Obsidian 联动（关键）

Obsidian 中安装插件：**Khoj**（社区插件市场搜 khoj）

配置：
- API URL: http://127.0.0.1:42110
- Sync vault：勾上

之后在 Obsidian 任意笔记里按 `Cmd+P` → "Khoj: Search" 即可。

### 4. 浏览器剪藏（可选）

Chrome / Edge 商店搜 **Khoj** → 装扩展 → 配 URL `http://localhost:42110` → 任何网页一键存为 markdown 入库

---

## 四、常见坑

| 坑              | 解决                                                                  |
| -------------- | ------------------------------------------------------------------- |
| pip 装超时        | 加镜像源：`pip install khoj -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 启动后访问 502      | torch 还在下载，看终端日志，等完                                                 |
| 索引慢            | 第一次正常，后续增量很快                                                        |
| Obsidian 搜不到结果 | 检查 D:\知识库 已索引、Watch 已开                                              |
|                |                                                                     |

---

## 五、Hermes 联动

Khoj 提供 HTTP API：
- 检索：`GET http://localhost:42110/api/search?q=...&t=markdown`
- 聊天：`POST http://localhost:42110/api/chat`

API Key：管理后台 → API → Generate

填到 `99-统一检索脚本\config\engines.json` 的 khoj 段。

---

## 六、日常使用

- **找文档**：浏览器 http://localhost:42110 直接问
- **Obsidian 内**：Cmd+P → Khoj Search
- **统一检索脚本**：`node search.js "..."` 自动带上 Khoj

---

## 七、何时装

🟢 **第一个装**。轻量、与现有 Obsidian + D:\知识库 无缝衔接、纯本地。

---

🔗 **知识库引擎**：[[17-知识库引擎/README]]
