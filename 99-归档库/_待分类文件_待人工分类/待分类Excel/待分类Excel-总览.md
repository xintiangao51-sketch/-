---
tags: [模板, 索引]
created: 2026-06-12
type: index
---
# 待分类Excel

`dataview
TABLE file.ctime as "创建时间", tags as "标签"
FROM "06-参考文档/待分类Excel"
WHERE file.name != "待分类Excel-总览" AND file.name != "README"
SORT file.ctime DESC
`
