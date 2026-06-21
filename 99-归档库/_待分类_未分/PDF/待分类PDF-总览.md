---
tags: [模板, 索引]
created: 2026-06-12
type: index
---
# 待分类PDF

`dataview
TABLE file.ctime as "创建时间", tags as "标签"
FROM "06-参考文档/待分类PDF"
WHERE file.name != "待分类PDF-总览" AND file.name != "README"
SORT file.ctime DESC
`
