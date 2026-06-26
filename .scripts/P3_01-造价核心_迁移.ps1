<#
.P3 01-造价核心 非MD文件 → 原始资料/01-定额资料/ + 05-费用定额/ + 12-已结项目资料/
.运行：powershell -ExecutionPolicy Bypass -File D:\知识库\.scripts\P3_01-造价核心_迁移.ps1
#>

$src = "D:\知识库\01-造价核心"
$dstBase = "D:\高治国资料\知识库原始资料"

Write-Host "===== P3 01-造价核心 → 知识库原始资料 =====" -ForegroundColor Cyan

# 子目录映射：造价核心子目录 → 原始资料目标子目录
$map = @{
    "取费与税金"   = "05-费用定额"
    "变更索赔"     = "12-已结项目资料"
    "工程量计算"   = "02-计算规则"
    "定额与计价"   = "01-定额资料"
    "材料价格"     = "07-材料价格"
}

$totalMoved = 0
$totalSkipped = 0

foreach ($subDir in $map.Keys) {
    $srcDir = Join-Path $src $subDir
    if (-not (Test-Path $srcDir)) { continue }

    $dstDir = Join-Path $dstBase $map[$subDir]
    if (-not (Test-Path $dstDir)) { New-Item $dstDir -ItemType Directory -Force | Out-Null }

    $files = Get-ChildItem $srcDir -Recurse -File -ErrorAction SilentlyContinue |
             Where-Object { $_.Extension -ne '.md' }

    foreach ($file in $files) {
        $relPath = $file.FullName.Replace($srcDir, "").TrimStart("\")
        $dstFile = Join-Path $dstDir $relPath
        $dstFileDir = Split-Path $dstFile -Parent

        if (-not (Test-Path $dstFileDir)) { New-Item $dstFileDir -ItemType Directory -Force | Out-Null }

        if (Test-Path $dstFile) { $totalSkipped++; continue }

        Move-Item $file.FullName $dstFile -Force
        Write-Host "  📦 [$subDir] $($file.Name) → $($map[$subDir])" -ForegroundColor Green
        $totalMoved++
    }
}

# 根目录文件（直接迁到 01-定额资料 根）
$rootFiles = Get-ChildItem $src -File -ErrorAction SilentlyContinue |
             Where-Object { $_.Extension -ne '.md' }
$dstRoot = Join-Path $dstBase "01-定额资料"

foreach ($file in $rootFiles) {
    $dstFile = Join-Path $dstRoot $file.Name
    if (Test-Path $dstFile) { $totalSkipped++; continue }
    Move-Item $file.FullName $dstFile -Force
    Write-Host "  📦 [根目录] $($file.Name)" -ForegroundColor Green
    $totalMoved++
}

Write-Host ""
Write-Host "===== 迁移完成 =====" -ForegroundColor Cyan
Write-Host "✅ 成功移动: $totalMoved 个文件" -ForegroundColor Green
Write-Host "⏭️  跳过（已存在）: $totalSkipped 个文件" -ForegroundColor Yellow
Write-Host "📂 保留MD文件: 在原位" -ForegroundColor White
