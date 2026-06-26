---
tags: [AI, 工具, 使用说明]
---

# price_downloader.py · 使用说明

> **脚本路径**：`07-AI工具与技能/price_downloader.py`
> **数据源**：xjzj.com 月度综合价格信息
> **输出**：`01-造价核心/定额与计价/近期材料价/{YYYY-MM}/{YYYY-MM}-{地州}-综合价格信息.{doc,xlsx}`

## 一、能力

| 命令 | 行为 |
|------|------|
| `python price_downloader.py` | 下载最新一期全部地州（自动探查） |
| `python price_downloader.py --month 2026-04` | 下载指定月份全部地州 |
| `python price_downloader.py --month 2026-04 --region 乌鲁木齐` | 下载指定月份+地州 |
| `python price_downloader.py --all` | 下载最近 3 个月（探查 + 已知） |
| `python price_downloader.py --discover` | 仅探查 xjzj.com 不下载（写 JSON） |
| `python price_downloader.py --list-known` | 列出已知 ID 映射（不联网） |

## 二、当前已知 ID（2026-06-24 实测）

| 月份 | 地州 | xjzj.com ID |
|------|------|-------------|
| 2026-04 | 全疆汇总 | 6773 |
| 2026-04 | 克州 | 6784 |
| 2026-04 | 石河子 | 6785 |
| 2026-04 | 塔城地区 | 6786 |
| 2026-04 | 吐鲁番 | 6787 |
| 2026-04 | 乌鲁木齐市 | 6788 |
| 2026-04 | 五家渠市 | 6789 |
| 2026-04 | 伊犁州直各县市 | 6790 |
| 2026-03 | 全疆汇总 | 6754 |
| 2026-01 | 全疆汇总 | 6716 |
| 2025-12 | 全疆汇总 | 6696 |

📌 **新增 ID 来源**：每次 `--discover` 会把 xjzj.com 首页新出现的条目自动加入 KNOWN_IDS。

## 三、文件命名规范

```
{YYYY-MM}-{地州}-综合价格信息.{doc|xlsx}
例：2026-04-乌鲁木齐市-综合价格信息.doc
```

目录结构：
```
01-造价核心/定额与计价/近期材料价/
├── _主索引.md
├── 2026-04-乌鲁木齐-综合价格信息.doc         ← 已下载
├── 2026-04-乌鲁木齐-综合价格信息.xlsx        ← 已下载
├── 2026-04-乌鲁木齐-材料价格_全量.json       ← 已生成
├── 乌鲁木齐2026-04_速查.md                   ← 已生成
└── 2026-03/                                  ← 待下载
    ├── 2026-03-全疆汇总-综合价格信息.doc
    └── ...
```

## 四、依赖安装

```bash
pip install requests beautifulsoup4 openpyxl
```

## 五、典型工作流

### 场景 1：月初自动下载最新一期

```bash
python D:\知识库\07-AI工具与技能\price_downloader.py
```

### 场景 2：补齐历史月份

```bash
# 一次性下载最近 3 个月
python price_downloader.py --all
```

### 场景 3：仅做探查 + 备份

```bash
# 探查后写 JSON，再人工审核
python price_downloader.py --discover
notepad "D:\知识库\01-造价核心\采集日志\price_discover_20260624.json"
```

## 六、关联

- [[01-造价核心/定额与计价/近期材料价/_主索引|近期材料价主索引]]
- [[10-索引与导航/知识库总索引#KC-286]]
- [daily_crawl](file:///daily_crawl.py)（采集政策+定额，与本脚本互补）
- [[Windows任务计划配置]]（建议挂每日 09:00 自动下载月度）

## 七、变更日志

- **v1.0** (2026-06-24)：初版发布，支持 discover + 按月+地州下载 + KNOWN_IDS 维护

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
