<#
.P5 清理临时文件
.运行：powershell -ExecutionPolicy Bypass -File D:\知识库\.scripts\P5_清理临时文件.ps1
#>

Write-Host "===== P5 清理临时文件 =====" -ForegroundColor Cyan
$log = @()

# 1. inbox/（DDC提取过程文件，已吸收完成）
$inbox = "D:\知识库\00-工作台\inbox"
if (Test-Path $inbox) {
    $count = @(Get-ChildItem $inbox -Recurse -File -ErrorAction SilentlyContinue).Count
    $size = (Get-ChildItem $inbox -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Remove-Item $inbox -Recurse -Force
    Write-Host "  🗑️  删除 inbox/ ($count 文件 / $([math]::Round($size,1)) MB)" -ForegroundColor Red
    $log += "inbox/: $count 文件 / $([math]::Round($size,1)) MB"
}

# 2. outputs/（临时输出）
$outputs = "D:\知识库\outputs"
if (Test-Path $outputs) {
    $count = @(Get-ChildItem $outputs -Recurse -File -ErrorAction SilentlyContinue).Count
    $size = (Get-ChildItem $outputs -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
    Remove-Item $outputs -Recurse -Force
    Write-Host "  🗑️  删除 outputs/ ($count 文件 / $([math]::Round($size,1)) MB)" -ForegroundColor Red
    $log += "outputs/: $count 文件 / $([math]::Round($size,1)) MB"
}

# 3. 根目录GB PDF（已在08-参考规范有引用，移到原始资料/09-参考规范/）
$gbPdf = "D:\知识库\GB50856-2013 通用安装工程工程量计算规范.pdf"
$dstGb = "D:\高治国资料\知识库原始资料\09-参考规范\国标清单\GB50856-2013 通用安装工程工程量计算规范.pdf"
$dstDir = Split-Path $dstGb -Parent
if (Test-Path $gbPdf) {
    if (-not (Test-Path $dstDir)) { New-Item $dstDir -ItemType Directory -Force | Out-Null }
    if (-not (Test-Path $dstGb)) {
        Move-Item $gbPdf $dstGb -Force
        Write-Host "  📦  迁移: GB50856-2013.pdf → 09-参考规范/国标清单/" -ForegroundColor Green
        $log += "GB50856-2013.pdf: 迁移到 09-参考规范/国标清单/"
    }
}

# 4. 12-项目案例库 .tsv 缓存（来源数据在Excel，tsv是导出缓存）
$tsvs = Get-ChildItem "D:\知识库\12-项目案例库" -Filter "*.tsv" -Recurse -File -ErrorAction SilentlyContinue
$tsvCount = $tsvs.Count
$tsvSize = ($tsvs | Measure-Object -Property Length -Sum).Sum / 1MB
foreach ($tsv in $tsvs) { Remove-Item $tsv.FullName -Force }
if ($tsvCount -gt 0) {
    Write-Host "  🗑️  删除 $tsvCount 个 .tsv 缓存文件 ($([math]::Round($tsvSize,1)) MB)" -ForegroundColor Red
    $log += "12-项目案例库 .tsv: $tsvCount 文件 / $([math]::Round($tsvSize,1)) MB"
}

Write-Host ""
Write-Host "===== 清理完成 =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 清理明细:" -ForegroundColor Yellow
$log | ForEach-Object { Write-Host "  • $_" }
