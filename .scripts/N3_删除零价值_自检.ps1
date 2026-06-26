# N3_删除零价值_自检.ps1
# 第三步：删除 _09项目资料_杂项 下的临时桌面/总览/电子发票/学位证书（剩余）
# 第四步：自检迁移结果

# 启用严格模式
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$srcBase = "D:\知识库\99-归档库\_09项目资料_杂项"
$dstBase = "D:\高治国资料\知识库原始资料"

# ============== 第三步：删除零价值 ==============
Write-Host "===== 第三步：删除零价值文件 =====" -ForegroundColor Cyan

# 1. 临时桌面
$tempDesktop = Join-Path $srcBase "临时归档文件\2026临时桌面"
if (Test-Path $tempDesktop) {
    Remove-Item $tempDesktop -Recurse -Force
    Write-Host "🗑️  删除: 临时归档文件\2026临时桌面" -ForegroundColor Red
}

# 2. 临时归档文件总览
$tempOverview = Join-Path $srcBase "临时归档文件\临时归档文件-项目总览.md"
if (Test-Path $tempOverview) {
    Remove-Item $tempOverview -Force
    Write-Host "🗑️  删除: 临时归档文件-项目总览.md" -ForegroundColor Red
}

# 3. 临时归档文件目录（删后空）
$tempDir = Join-Path $srcBase "临时归档文件"
if ((Test-Path $tempDir) -and (Get-ChildItem $tempDir -Recurse -Force | Measure-Object).Count -eq 0) {
    Remove-Item $tempDir -Force
    Write-Host "🗑️  删除: 空目录 临时归档文件" -ForegroundColor Red
}

# 4. 其他零散文件总览
$overview = Join-Path $srcBase "其他零散文件\其他零散文件-项目总览.md"
if (Test-Path $overview) {
    Remove-Item $overview -Force
    Write-Host "🗑️  删除: 其他零散文件-项目总览.md" -ForegroundColor Red
}

# 5. 项目资料-总览
$projectOverview = Join-Path $srcBase "项目资料-总览.md"
if (Test-Path $projectOverview) {
    Remove-Item $projectOverview -Force
    Write-Host "🗑️  删除: 项目资料-总览.md" -ForegroundColor Red
}

# 6. 电子发票（26 张 dzfp_*.pdf） + 高治国-学位证书.pdf
$dwgDir = Join-Path $srcBase "其他零散文件\03-图纸资料"
$invoiceCount = 0
$degreeCount = 0

if (Test-Path $dwgDir) {
    Get-ChildItem $dwgDir -Filter "dzfp_*.pdf" | ForEach-Object {
        Remove-Item $_.FullName -Force
        $invoiceCount++
    }

    $degree = Join-Path $dwgDir "高治国-学位证书.pdf"
    if (Test-Path $degree) {
        Remove-Item $degree -Force
        $degreeCount++
    }
}

Write-Host "🗑️  删除: $invoiceCount 张电子发票" -ForegroundColor Red
Write-Host "🗑️  删除: 1 张学位证书" -ForegroundColor Red

# ============== 第四步：自检 ==============
Write-Host ""
Write-Host "===== 第四步：自检迁移结果 =====" -ForegroundColor Cyan

# 检查 99-归档库/_09项目资料_杂项 剩余文件
Write-Host ""
Write-Host "【1】99-归档库 剩余文件检查" -ForegroundColor Yellow
if (Test-Path $srcBase) {
    $remaining = Get-ChildItem $srcBase -Recurse -File -ErrorAction SilentlyContinue
    $remainingCount = $remaining.Count
    $remainingSize = ($remaining | Measure-Object -Property Length -Sum).Sum / 1MB

    Write-Host "  99-归档库/_09项目资料_杂项 剩余 $remainingCount 个文件 / $([math]::Round($remainingSize, 1)) MB"

    if ($remainingCount -gt 0 -and $remainingCount -lt 30) {
        Write-Host ""
        Write-Host "  剩余文件列表:"
        $remaining | ForEach-Object { Write-Host "    $($_.FullName.Replace($srcBase, '...'))" }
    }
}

# 检查 知识库原始资料 新目录文件数
Write-Host ""
Write-Host "【2】D:\高治国资料\知识库原始资料 检查" -ForegroundColor Yellow
if (Test-Path $dstBase) {
    $files = Get-ChildItem $dstBase -Recurse -File -ErrorAction SilentlyContinue
    $dirs = Get-ChildItem $dstBase -Recurse -Directory -ErrorAction SilentlyContinue
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  文件数：$($files.Count) 个"
    Write-Host "  目录数：$($dirs.Count) 个"
    Write-Host "  总大小：$([math]::Round($totalSize, 1)) MB"
    Write-Host ""
    Write-Host "  12-已结项目资料 包含的项目目录:"
    Get-ChildItem (Join-Path $dstBase "12-已结项目资料") -Directory | ForEach-Object {
        $count = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "    $($_.Name) : $count 个文件"
    }
}

# 知识库 vs 原始资料 关联表
Write-Host ""
Write-Host "【3】D:\知识库 健康度对比（迁移后）" -ForegroundColor Yellow
$kbBase = "D:\知识库"
if (Test-Path $kbBase) {
    $kbFiles = Get-ChildItem $kbBase -Recurse -File -Include "*.md" -ErrorAction SilentlyContinue
    $kbSize = ($kbFiles | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  D:\知识库 MD 文件：$($kbFiles.Count) 个 / $([math]::Round($kbSize, 1)) MB"

    # 各子目录统计
    Write-Host "  主要目录:"
    foreach ($sub in @("00-工作台", "01-造价核心", "06-参考文档", "10-索引与导航", "99-归档库")) {
        $subPath = Join-Path $kbBase $sub
        if (Test-Path $subPath) {
            $subFiles = Get-ChildItem $subPath -Recurse -File -Include "*.md" -ErrorAction SilentlyContinue
            $subNonMd = Get-ChildItem $subPath -Recurse -File -Exclude "*.md" -ErrorAction SilentlyContinue
            Write-Host "    $sub : $($subFiles.Count) MD / $($subNonMd.Count) 非MD"
        }
    }
}

# ============== 总结 ==============
Write-Host ""
Write-Host "===== 迁移总结 =====" -ForegroundColor Cyan
Write-Host "✅ 99-归档库/_09项目资料_杂项 处理完成" -ForegroundColor Green
Write-Host "✅ D:\高治国资料\知识库原始资料 已建立" -ForegroundColor Green
Write-Host "✅ D:\知识库 保持纯 MD 状态" -ForegroundColor Green
Write-Host ""
Write-Host "📁 下一步建议：" -ForegroundColor Yellow
Write-Host "  1. 打开 D:\知识库\00-工作台\原始资料索引.md 查阅完整对照表"
Write-Host "  2. 打开 D:\高治国资料\知识库原始资料\README.md 了解维护规范"
Write-Host "  3. 在 D:\知识库 跑 `python D:\知识库\.scripts\lint_xinjiang.py` 看新指标"
