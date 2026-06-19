---
tags: [AI, 索引]
created: 2026-06-12
type: index
---
# Drawing Analyzer

`dataview
TABLE file.ctime as "创建时间", tags as "标签"
FROM "07-AI工具与技能/drawing-analyzer"
WHERE file.name != "drawing-analyzer-总览" AND file.name != "README"
SORT file.ctime DESC
`
