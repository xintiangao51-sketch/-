<#
.P2 04-施工方案 非MD文件 → 原始资料/00-项目资料/施工方案
.运行：powershell -ExecutionPolicy Bypass -File D:\知识库\.scripts\P2_04-施工方案_迁移.ps1
#>

$src = "D:\知识库\04-施工方案"
$dst = "D:\高治国资料\知识库原始资料\00-项目资料\施工方案"

Write-Host "===== P2 04-施工方案 → 知识库原始资料/00-项目资料/施工方案 =====" -ForegroundColor Cyan

if (-not (Test-Path $dst)) { New-Item $dst -ItemType Directory -Force | Out-Null }

$files = Get-ChildItem $src -Recurse -File -ErrorAction SilentlyContinue |
         Where-Object { $_.Extension -ne '.md' }

Write-Host "扫描到 $($files.Count) 个非MD文件" -ForegroundColor Yellow

$moved = 0
$skipped = 0

foreach ($file in $files) {
    $relPath = $file.FullName.Replace($src, "").TrimStart("\")
    $dstFile = Join-Path $dst $relPath
    $dstDir = Split-Path $dstFile -Parent

    if (-not (Test-Path $dstDir)) { New-Item $dstDir -ItemType Directory -Force | Out-Null }

    if (Test-Path $dstFile) { $skipped++; continue }

    try {
        Move-Item $file.FullName $dstFile -Force
        Write-Host "  📦 $($file.Name)" -ForegroundColor Green
        $moved++
    } catch {
        Write-Host "  ❌ $($file.Name) — $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "===== 迁移完成 =====" -ForegroundColor Cyan
Write-Host "✅ 成功移动: $moved 个文件" -ForegroundColor Green
Write-Host "⏭️  跳过（已存在）: $skipped 个文件" -ForegroundColor Yellow
Write-Host "📂 保留MD文件: 在原位" -ForegroundColor White
Write-Host ""
Write-Host "目标目录现状:"
Get-ChildItem $dst -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $c = @(Get-ChildItem $_.FullName -File -ErrorAction SilentlyContinue).Count
    if ($c -gt 0) { Write-Host "  $($_.FullName.Replace($dst,'')) : $c 个文件" }
}
