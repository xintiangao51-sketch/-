<#
.P4 05-投标报价 非MD文件 → 原始资料/12-已结项目资料/ + 03-合同法务资料/招投标/
.运行：powershell -ExecutionPolicy Bypass -File D:\知识库\.scripts\P4_05-投标报价_迁移.ps1
#>

$src = "D:\知识库\05-投标报价"
$dstBase = "D:\高治国资料\知识库原始资料"

Write-Host "===== P4 05-投标报价 → 知识库原始资料 =====" -ForegroundColor Cyan

# 子目录映射
$map = @{
    "中铁二十五局投标资料\制度办法" = "03-合同法务资料\招投标"
    "中铁二十五局投标资料\合同"     = "03-合同法务资料\招投标"
    "中铁二十五局投标资料\投标"     = "03-合同法务资料\招投标"
    "投标分析"     = "12-已结项目资料"
    "投标文件"     = "12-已结项目资料"
    "投标编制"     = "12-已结项目资料\各项目"
    "报价策略"     = "12-已结项目资料\各项目"
    "招标文件"     = "03-合同法务资料\招投标"
    "项目报价"     = "12-已结项目资料\各项目"
    "项目报价\高治国资料组价报价知识整理" = "12-已结项目资料\各项目"
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

        try {
            Move-Item $file.FullName $dstFile -Force
            Write-Host "  📦 [$subDir] $($file.Name)" -ForegroundColor Green
            $totalMoved++
        } catch {
            Write-Host "  ❌ [$subDir] $($file.Name) — $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# 根目录文件（直接迁到 12-已结项目资料）
$rootFiles = Get-ChildItem $src -File -ErrorAction SilentlyContinue |
             Where-Object { $_.Extension -ne '.md' }
$dstRoot = Join-Path $dstBase "12-已结项目资料"

foreach ($file in $rootFiles) {
    $dstFile = Join-Path $dstRoot $file.Name
    if (Test-Path $dstFile) { $totalSkipped++; continue }
    try {
        Move-Item $file.FullName $dstFile -Force
        Write-Host "  📦 [根目录] $($file.Name)" -ForegroundColor Green
        $totalMoved++
    } catch {
        Write-Host "  ❌ [根目录] $($file.Name) — $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "===== 迁移完成 =====" -ForegroundColor Cyan
Write-Host "✅ 成功移动: $totalMoved 个文件" -ForegroundColor Green
Write-Host "⏭️  跳过（已存在）: $totalSkipped 个文件" -ForegroundColor Yellow
Write-Host "📂 保留MD文件: 在原位" -ForegroundColor White
Write-Host ""
Write-Host "目标目录现状:"
Get-ChildItem (Join-Path $dstBase "12-已结项目资料") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $c = @(Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
    if ($c -gt 0) { Write-Host "  12-已结项目资料\$($_.Name) : $c 个文件" }
}
Get-ChildItem (Join-Path $dstBase "03-合同法务资料\招投标") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $c = @(Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
    if ($c -gt 0) { Write-Host "  03-合同法务资料\招投标\$($_.Name) : $c 个文件" }
}
