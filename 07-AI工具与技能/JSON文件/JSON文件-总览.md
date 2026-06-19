---
tags: [AI, 索引]
created: 2026-06-12
type: index
---
# JSON文件

`dataview
TABLE file.ctime as "创建时间", tags as "标签"
FROM "07-AI工具与技能/JSON文件"
WHERE file.name != "JSON文件-总览" AND file.name != "README"
SORT file.ctime DESC
`
