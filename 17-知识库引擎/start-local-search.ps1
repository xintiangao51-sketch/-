# D:\知识库\17-知识库引擎\start-local-search.ps1
# 本地搜索启动脚本（不依赖外部引擎）

Write-Host "🔍 启动本地统一检索..." -ForegroundColor Green

$query = "沥青砼 定额"
if ($args.Count -gt 0) { $query = $args[0] }

Write-Host "
查询: $query" -ForegroundColor Cyan
python "D:\知识库\17-知识库引擎\99-统一检索脚本\search.py" "$query"
