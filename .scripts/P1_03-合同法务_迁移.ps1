<#
.P1 03-合同与法务 非MD文件 → 原始资料/03-合同法务资料/
.保持子目录结构，只移非MD文件，保留MD在原位
.运行：powershell -ExecutionPolicy Bypass -File D:\知识库\.scripts\P1_03-合同法务_迁移.ps1
#>

$src = "D:\知识库\03-合同与法务"
$dst = "D:\高治国资料\知识库原始资料\03-合同法务资料"

Write-Host "===== P1 03-合同与法务 → 知识库原始资料 =====" -ForegroundColor Cyan

if (-not (Test-Path $dst)) { New-Item $dst -ItemType Directory -Force | Out-Null }

$moved = 0
$skipped = 0
$total = 0

# 获取所有非MD文件（递归）
$files = Get-ChildItem $src -Recurse -File -ErrorAction SilentlyContinue |
         Where-Object { $_.Extension -ne '.md' }

Write-Host "扫描到 $($files.Count) 个非MD文件" -ForegroundColor Yellow

foreach ($file in $files) {
    $relPath = $file.FullName.Replace($src, "").TrimStart("\")
    $dstFile = Join-Path $dst $relPath
    $dstDir = Split-Path $dstFile -Parent

    if (-not (Test-Path $dstDir)) {
        New-Item $dstDir -ItemType Directory -Force | Out-Null
    }

    # 跳过已存在
    if (Test-Path $dstFile) {
        $skipped++
        continue
    }

    try {
        Move-Item $file.FullName $dstFile -Force
        $sizeKB = [math]::Round($file.Length / 1KB, 1)
        Write-Host "  📦 $($file.Name) → $relPath ($sizeKB KB)" -ForegroundColor Green
        $moved++
    } catch {
        Write-Host "  ❌ $($file.Name) — $($_.Exception.Message)" -ForegroundColor Red
    }
    $total++
}

# 删除已迁移完的非MD文件的空目录
Write-Host ""
Write-Host "清理空目录..." -ForegroundColor Cyan
$subDirs = Get-ChildItem $src -Recurse -Directory -ErrorAction SilentlyContinue |
           Sort-Object FullName -Descending
foreach ($dir in $subDirs) {
    $hasMd = @(Get-ChildItem $dir -Filter "*.md" -File -ErrorAction SilentlyContinue).Count -gt 0
    $hasNonMd = @(Get-ChildItem $dir -File -ErrorAction SilentlyContinue |
                   Where-Object { $_.Extension -ne '.md' }).Count -gt 0
    $hasSubDir = @(Get-ChildItem $dir -Directory -ErrorAction SilentlyContinue).Count -gt 0

    if (-not $hasMd -and -not $hasNonMd -and -not $hasSubDir) {
        Remove-Item $dir -Force
        Write-Host "  🗑️  删除空目录: $($dir.FullName.Replace($src,''))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "===== 迁移完成 =====" -ForegroundColor Cyan
Write-Host "✅ 成功移动: $moved 个文件" -ForegroundColor Green
Write-Host "⏭️  跳过（已存在）: $skipped 个文件" -ForegroundColor Yellow
Write-Host "📂 保留MD文件: 在原位" -ForegroundColor White
Write-Host ""
Write-Host "检查迁移后位置:" -ForegroundColor Cyan
Get-ChildItem $dst -Recurse -File -ErrorAction SilentlyContinue | Group-Object Directory | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) 个文件"
}
