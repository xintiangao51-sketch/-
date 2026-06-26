# Replace 05-数据资产 with 15-数据资产 in known md files
$files = @(
  '00-工作台\首页-项目驾驶舱.md',
  '00-工作台\知识库健康度报告.md',
  '00-工作台\新疆工程造价智能工作台V2.0建设任务书.md',
  '00-工作台\快速入口.md',
  '00-工作台\W-知识库重构记录-P1-P2_20260621.md'
)
foreach ($f in $files) {
  $p = Join-Path 'D:\知识库' $f
  if (-not (Test-Path $p)) { Write-Host "miss $f"; continue }
  $c = Get-Content -Path $p -Raw -Encoding UTF8
  $c2 = $c -replace '05-数据资产','15-数据资产'
  if ($c -ne $c2) {
    Set-Content -Path $p -Value $c2 -Encoding UTF8 -NoNewline
    Write-Host "updated $f"
  } else {
    Write-Host "no-op $f"
  }
}
