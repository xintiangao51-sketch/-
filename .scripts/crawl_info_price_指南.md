---
标题: 信息价自动采集脚本使用指南
日期: 2026-06-25
版本: 1.0
主标签: #方法 #信息价 #采集 #自动化
tags: [AI, 方法, 信息价, 自动化]
created: 2026-06-25
type: guide
---

# 信息价自动采集脚本使用指南

> 配套脚本：`crawl_info_price.py`

## 安装依赖（一次性）

```cmd
pip install requests beautifulsoup4 openpyxl --break-system-packages
```

## 常用命令

### 全地州扫描

```cmd
python D:\知识库\.scripts\crawl_info_price.py
```

### 单地州扫描

```cmd
python D:\知识库\.scripts\crawl_info_price.py --region 乌鲁木齐
python D:\知识库\.scripts\crawl_info_price.py --region 哈密
```

### 查看支持地州

```cmd
python D:\知识库\.scripts\crawl_info_price.py --list-regions
```

## 输出

- 信息价文件：`D:\信息价\{地州名}\` 或 `D:\知识库\11-材料设备价格库\{地州名}\`
- 索引文件：`D:\知识库\11-材料设备价格库\_info_price_index.json`

## ⚠ 注意

- xjzj.com 为新疆造价信息网，如站点改版需更新选择器
- 部分公告可能需要登录，脚本不支持登录态
- 下载文件为原始格式（xls/xlsx/docx/doc/pdf），非结构化数据
- 如需转为结构化 Markdown，需另写解析脚本
