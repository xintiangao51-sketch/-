---
tags: [Dataview, 查询, 索引, 精华]
created: 2026-06-22
updated: 2026-06-22
type: reference
---

# 📊 Dataview 查询库

> 常用 Dataview 查询汇总，直接复制到任意笔记中使用。
> 数据基于 frontmatter 字段动态聚合，无需手动维护。
> 已增强至 7 大类 @ P3 知识沉淀。

---

## 1️⃣ 项目仪表盘

### 在建项目列表
```dataview
TABLE 
  project_name as "项目名称", 
  contract_amount as "合同金额(万)", 
  region as "地区", 
  status as "状态",
  date as "日期"
FROM "09-项目资料"
WHERE status = "在建" OR status = "#在建"
SORT date DESC
```

### 按地区分组
```dataview
TABLE length(rows) as "项目数"
FROM "09-项目资料"
WHERE region
GROUP BY region
SORT length(rows) DESC
```

### 最近更新项目
```dataview
TABLE file.mtime as "最后修改", status as "状态"
FROM "09-项目资料"
WHERE file.name != this.file.name
SORT file.mtime DESC
LIMIT 10
```

---

## 2️⃣ 材料价格查询

### 全库材料价格
```dataview
TABLE 材料名称 as "名称", 规格 as "规格", 单价 as "单价(元)", 单位 as "单位", 地区 as "地区", 日期 as "日期"
FROM "11-材料设备价格库"
WHERE 材料名称
SORT 日期 DESC, 材料名称 ASC
```

### 查询特定材料
```dataview
TABLE 单价 as "单价(元)", 地区, 日期
FROM "11-材料设备价格库"
WHERE 材料名称 = "水泥" OR contains(材料名称, "混凝土")
SORT 日期 DESC
LIMIT 5
```

### 按类别分组
```dataview
TABLE length(rows) as "条目数"
FROM "11-材料设备价格库"
WHERE 类别
GROUP BY 类别
SORT length(rows) DESC
```

### 最新入库材料
```dataview
TABLE 材料名称 as "名称", 单价 as "单价(元)", 日期
FROM "11-材料设备价格库"
WHERE 材料名称
SORT 日期 DESC
LIMIT 20
```

---

## 3️⃣ 待办任务聚合

### 全部未完成
```dataview
TASK
FROM "00-工作台" OR "01-造价核心"
WHERE !completed
SORT created DESC
```

### 本周已完成
```dataview
TASK
FROM "00-工作台" OR "01-造价核心"
WHERE completed AND completed >= date(today) - dur(7 days)
SORT completed DESC
```

### 按来源统计待办
```dataview
TABLE length(rows) as "待办数"
FROM "00-工作台" OR "01-造价核心"
WHERE file.tasks
FLATTEN file.tasks as t
WHERE !t.completed
GROUP BY file.folder as "来源"
SORT length(rows) DESC
```

---

## 4️⃣ 知识管理统计

### 按标签统计笔记数
```dataview
TABLE length(rows) as "笔记数"
FROM ""
WHERE file.tags
FLATTEN file.tags as tag
GROUP BY tag
SORT length(rows) DESC
```

### 最近修改的笔记
```dataview
TABLE file.mtime as "修改时间", file.folder as "目录"
FROM ""
SORT file.mtime DESC
LIMIT 20
```

### 按目录统计文件数
```dataview
TABLE length(rows) as "文件数"
FROM ""
GROUP BY file.folder as "目录"
SORT length(rows) DESC
```

---

## 5️⃣ 造价专项查询

### 按项目类型筛选
```dataview
TABLE 项目名称, 合同金额, 状态
FROM "09-项目资料"
WHERE contains(file.tags, "造价") OR contains(file.tags, "项目")
SORT 日期 DESC
```

### 近30天变更签证
```dataview
TABLE 项目名称 as "项目", 变更内容, 变更金额, 状态
FROM "09-项目资料"
WHERE 变更日期 AND 变更日期 >= date(today) - dur(30 days)
SORT 变更日期 DESC
```

---

## 6️⃣ Dataview JS 高级查询

### 按状态统计项目数
```dataviewjs
const statusCount = dv.pages('"09-项目资料"')
  .where(p => p.status)
  .groupBy(p => p.status)
  .map(g => [g.key, g.rows.length]);

dv.table(["状态", "项目数"], statusCount);
```

### 项目金额排名
```dataviewjs
const projects = dv.pages('"09-项目资料"')
  .where(p => p.contract_amount)
  .sort(p => p.contract_amount, 'desc')
  .limit(10);

dv.table(["排名", "项目", "金额(万)", "状态"], 
  projects.map((p, i) => [i+1, p.file.link, p.contract_amount, p.status])
);
```

---
## 7️⃣ 知识卡片（KC）检索

### KC 全量列表
```dataview
TABLE file.folder as "位置", file.mtime as "更新时间"
FROM ""
WHERE contains(file.name, "KC-")
SORT file.name ASC
```

### 按领域检索
```dataview
TABLE file.mtime as "更新时间"
FROM ""
WHERE contains(file.name, "KC-")
FLATTEN file.tags as tag
WHERE contains(tag, "清单计价") OR contains(tag, "造价管理") OR contains(tag, "定额")
SORT file.name ASC
```

---

## 使用说明

| 查询类型 | 依赖的 frontmatter 字段 | 适用目录 |
|---------|------------------------|---------|
| 项目台账 | `project_name`, `contract_amount`, `region`, `status` | 09-项目资料 |
| 材料价格 | `材料名称`, `规格`, `单价`, `单位`, `地区`, `日期` | 11-材料设备价格库 |
| 待办任务 | Obsidian 任务语法 `- [ ]` | 00-工作台, 01-造价核心 |
| 知识统计 | `tags` frontmatter | 全库 |
| 变更签证 | `变更内容`, `变更金额`, `变更日期` | 09-项目资料 |

> 💡 提示：在笔记中插入 `dataview` 代码块即可自动渲染为表格。
> 结合 Templater 模板，所有查询自动关联 frontmatter 字段。

---

[[🏠 知识库首页]] | [[10-索引与导航/项目台账仪表盘]] | [[10-索引与导航/知识库总索引]]
