---
tags: [AI, 索引]
created: 2026-06-12
type: reference
---

# 火山引擎 Python SDK 安装 | 2026-05-23

## 任务
安装火山引擎 Python SDK (volcengine-python-sdk) 并更新到最新版本。

## 环境
- 平台: Windows 10.0.26200 x64
- Python: 未安装 → 3.12.8
- pip: 未安装 → 24.3.1
- 包管理器: scoop/winget/choco 均未安装

## 步骤

### 1. Python 安装（降级方案）
- 无包管理器可用，从华为云镜像直接下载 python-3.12.8-amd64.exe (25.8MB)
- 静默安装到 `C:\Users\高\AppData\Local\Programs\Python\Python312`
- 已将 Python + Scripts 加入用户 PATH

### 2. volcengine-python-sdk 安装
- pip install volcengine-python-sdk → **v5.0.28**（最新版）
- 依赖: certifi, python-dateutil, six, urllib3

## 结果
✅ Python 3.12.8 + pip 24.3.1 已安装
✅ volcengine-python-sdk 5.0.28 已安装（远高于修复重试缺陷的 4.0.43 版本）

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
