---
标题: E3 语义探针 Windows 执行指南
日期: 2026-06-25
版本: 1.0
主标签: #方法 #AI #知识库 #体检
tags: [AI, 方法, 知识库, 体验]
created: 2026-06-25
type: guide
aliases: [语义探针指南, E3 指南]
---

# E3 语义探针 Windows 执行指南

> 目标：在 Windows 真机运行 `semantic_scan_xj.py`，识别 D:\知识库 内高相似度但未关联的页面对（≥ 0.75），为下一步知识页合并/拆页/交叉链接提供数据驱动决策。

---

## 故障背景

在 bash 沙箱尝试 `pip install sentence-transformers` 失败：

```
ProxyError('Cannot connect to proxy.', OSError('Tunnel connection failed: 403 Forbidden'))
```

沙箱无 pip 权限。**需在 Windows 真机运行**。

---

## 第 1 步：安装依赖（一次性）

打开 cmd（Win+R → cmd），执行：

```cmd
pip install sentence-transformers numpy --break-system-packages
```

或者如果你有 conda 环境：

```cmd
conda install -c conda-forge sentence-transformers
```

**预期下载**：bge-small-zh-v1.5 模型（约 95MB，下载至 `C:\Users\<用户名>\.cache\huggingface\hub\`）

**镜像配置**（如下载慢，脚本已内置 `HF_ENDPOINT=https://hf-mirror.com`）：

---

## 第 2 步：执行扫描

按需求选用以下命令之一：

### 全库扫描（推荐）

```cmd
python D:\知识库\.scripts\semantic_scan_xj.py
```

**输出示例**（预期）：
```
📊 未关联的高相似度页面对 (X pairs ≥ 0.75)
═══════════════════════════════════════════════════════════════════════════════
  0.92 ██████████████████████████████  KC-222_管理费  ↔  KC-227_新疆费率与取费查询路径
  0.88 ██████████████████████████████  KC-130·类型与流程  ↔  KC-130·签证单规范
  ...
```

### 自定义阈值

```cmd
python D:\知识库\.scripts\semantic_scan_xj.py --threshold 0.7
```

（0.7 更容易发现关联，但噪音也多；0.75 平衡；0.85 保证高精）

### 单页扫描（提炼时用）

```cmd
python D:\知识库\.scripts\semantic_scan_xj.py --page "01-造价核心/定额"
```

### JSON 输出（供 AI 解析）

```cmd
python D:\知识库\.scripts\semantic_scan_xj.py --json
```

---

## 预期产出

| 产出 | 格式 | 用途 |
|------|------|------|
| 终端报告 | 文本条形图 | 人工查看不需要关联的页面 |
| JSON 文件（可选） | .json | 供 lint_xinjiang.py 或老高批量处理 |
| 缓存文件 | `.scripts/.cache/embeddings_cache.json` | 下次扫描加速（增量嵌入）|

---

## 结果解读与决策建议

### 相似度分级

| 相似度 | 信号强度 | 建议处理 |
|:-----:|:-------:|---------|
| ≥ 0.85 | 🔴 非常高 | 强烈建议检查是否应合并或双向链接 |
| 0.75-0.85 | 🟡 中 | 建议审查后决定是否添加 [[wikilink]] |
| 0.65-0.75 | 🟢 低 | 备用信号，暂时忽略 |

### 典型发现类型

| 类型 | 例 | 处理 |
|------|----|------|
| **同名异页** | KC-222_管理费 vs KC-227_新疆费率 | 合并或交叉引用 |
| **辐页重逢** | KC-130·类型 vs KC-130·签证单 | 已有枢纽页链接，**无需处理** |
| **内容等效** | 两篇不同工程合同条款分析 | 拆为一篇加对比表 |
| **框架重复** | 多个冬施方案页相似度极高 | 合并为模版 |

### 决策流程（按 C5 台律迭代制）

```
语义探针对 (p1, p2, sim)
  │
  ├── 已在推荐阅读区互相引用 → 忽略
  │
  ├── 已知框架关联（同枢纽页不同辐页）→ 忽略
  │
  └── 新的发现 → 人工判断：
        │
        ├── 内容等效 → 合并为一页（保留原版为辐页备份）
        ├── 框架重复 → 去重，保留内容更全的那篇
        └── 概念相近但互补 → 补 [[wikilink]] 双向链接
```

---

## E3 预期产出位置

运行完成后，建议将结果写入（按 E5 报告 § 七.2）：

```
D:\知识库\00-工作台\语义探针对日志.md
```

格式示例：

```markdown
# 语义探针对日志

> 每周探针对日志。倒序排列。

## 2026-06-25

| 相似度 | 页 A | 页 B | 处理 |
|:-----:|:-----|:-----|:----:|
| 0.92 | KC-222_管理费 | KC-227_新疆费率 | 已添加 [[KC-227]] 引用 |
| 0.88 | KC-130·类型与流程 | KC-130·签证单规范 | 同一枢纽页，忽略 |
```

---

## 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError: No module named 'sentence_transformers'` | 未安装 | `pip install sentence-transformers --break-system-packages` |
| `HF_ENDPOINT` 代理超时 | 国内网络 | 脚本已内置 `hf-mirror.com` ，如仍慢可手动下载模型文件 |
| CUDNN 报错 | GPU 驱动问题 | 脚本默认 CPU 推理，忽略 |
| 缓存损坏 | 异常中断 | 删除 `D:\知识库\.scripts\.cache\embeddings_cache.json` 重跑 |

---

## 与 fix_tags.py 的关系

- **fix_tags.py**（P0 第 1 项）：已执行完毕 ✅ FM tags 49% → 91.8%
- **E3 语义探针**（P1 第 6 项）：待 Windows 真机运行 ⏳
- **两任务独立**：先执行完 fix_tags 再跑 semantic_scan，互不冲突

---

## 变更日志

- 2026-06-25：v1.0 创建，E3 语义探针 Windows 真机执行指南
