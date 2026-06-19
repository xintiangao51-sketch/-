---
tags: [工具, 维护]
created: 2026-06-09
type: tool-docs
---

# 🛠️ 知识库维护工具

> 位于 `D:\知识库\.tools\`

---

## 工具清单

| 脚本 | 功能 | 用法 |
|------|------|------|
| `dedup_scanner.py` | 去冗扫描 | `python .tools/dedup_scanner.py` |
| `desensitize.py` | 脱敏处理 | `python .tools/desensitize.py --dry-run` |
| `run_tools.py` | 一键入口 | `python .tools/run_tools.py dedup` |

## 去冗扫描器

扫描知识库中的：
- 空文件
- 垃圾/临时文件（~$开头、.tmp等）
- 完全同名文件
- 相似文件名（模糊匹配）
- MD5完全重复文件
- 内容相似文件（TF-IDF余弦相似度≥0.85）

```bash
# 运行扫描
python .tools/dedup_scanner.py

# 指定目录
python .tools/dedup_scanner.py "D:\知识库\01-造价核心"
```

报告输出：`.archive/去冗扫描报告.md`

## 脱敏处理器

检测并替换敏感信息：
- 手机号（11位）
- 身份证号（18位/15位）
- 邮箱地址
- 银行卡号（16位/19位）
- 固定电话（含区号格式）
- IP地址

```bash
# 仅扫描，不修改文件
python .tools/desensitize.py --dry-run

# 执行脱敏（会修改文件，自动备份.bak）
python .tools/desensitize.py --execute

# 指定目录
python .tools/desensitize.py "D:\知识库\09-项目资料" --dry-run
```

报告输出：`.archive/脱敏扫描报告.md`

## 扩展脱敏规则

编辑 `desensitize.py` 中的 `CUSTOM_REPLACEMENTS` 字典：

```python
CUSTOM_REPLACEMENTS = {
    "中铁二十五局": "[施工单位A]",
    "高治国": "[姓名A]",
    "某手机号": "[手机号]",
}
```

## 建议运行频率

| 频率 | 操作 |
|------|------|
| 每月 | 去冗扫描，清理垃圾文件 |
| 导入新文件后 | 脱敏扫描（dry-run） |
| 每季度 | 内容相似度检测，合并重复 |

---

*工具文档 v1.0 · 2026-06-09*
