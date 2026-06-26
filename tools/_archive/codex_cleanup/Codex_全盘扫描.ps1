# ============================================================
# Codex 全盘扫描脚本
# 用途：扫描电脑中所有Codex安装、配置、缓存、记忆文件
# 运行方式：右键 → 使用 PowerShell 运行
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Codex 全盘扫描工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ===== 1. 扫描 npm 全局安装 =====
Write-Host "[1/6] 扫描 npm 全局安装..." -ForegroundColor Yellow
$npmPaths = @(
    "$env:APPDATA\npm\codex*",
    "$env:APPDATA\npm\node_modules\@openai\codex",
    "$env:APPDATA\npm\node_modules\codex"
)
foreach ($pattern in $npmPaths) {
    $items = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $version = "?"
        try { $version = (npm list -g @openai/codex --depth=0 2>$null) -replace '.*@','' -replace '@.*','' } catch {}
        Write-Host "  📦 npm: $($item.FullName) | v$version" -ForegroundColor White
    }
}

# ===== 2. 扫描 scoop/choco/winget 安装 =====
Write-Host "[2/6] 扫描包管理器安装..." -ForegroundColor Yellow
# Scoop
$scoopPath = "$env:USERPROFILE\scoop\apps\codex"
if (Test-Path $scoopPath) {
    Write-Host "  📦 Scoop: $scoopPath" -ForegroundColor White
}
# Chocolatey
$chocoPath = "$env:ProgramData\chocolatey\lib\codex"
if (Test-Path $chocoPath) {
    Write-Host "  📦 Choco: $chocoPath" -ForegroundColor White
}
# Winget
try {
    $wingetList = winget list --name codex --exact 2>$null
    if ($wingetList -match "codex") {
        Write-Host "  📦 Winget: 已安装" -ForegroundColor White
        $wingetList | ForEach-Object { Write-Host "     $_" }
    }
} catch {}

# ===== 3. 扫描桌面端安装 =====
Write-Host "[3/6] 扫描桌面端安装..." -ForegroundColor Yellow
$desktopPaths = @(
    "$env:LOCALAPPDATA\Programs\OpenAI",
    "$env:LOCALAPPDATA\Programs\codex",
    "$env:LOCALAPPDATA\OpenAI",
    "$env:ProgramFiles\OpenAI",
    "$env:ProgramFiles\codex",
    "$env:LOCALAPPDATA\codex-app",
    "$env:LOCALAPPDATA\Codex"
)
foreach ($path in $desktopPaths) {
    if (Test-Path $path) {
        $items = Get-ChildItem -Path $path -Recurse -Depth 1 -ErrorAction SilentlyContinue
        if ($items) {
            Write-Host "  🖥️  桌面端: $path" -ForegroundColor White
            $items | Where-Object { $_.PSIsContainer -or $_.Name -match "codex|Codex" } | ForEach-Object {
                Write-Host "       ├─ $($_.Name)" -ForegroundColor Gray
            }
        }
    }
}

# 搜索 AppData 中的 codex 相关目录
$codexDirs = @(
    "$env:LOCALAPPDATA\codex",
    "$env:APPDATA\codex",
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex"
)
Write-Host "[4/6] 扫描配置和缓存目录..." -ForegroundColor Yellow
foreach ($dir in $codexDirs) {
    if (Test-Path $dir) {
        $size = "{0:N2} MB" -f ((Get-ChildItem -Recurse $dir -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB)
        Write-Host "  📁 $dir ($size)" -ForegroundColor White
        Get-ChildItem -Path $dir -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "       ├─ $($_.Name)$(if(-not $_.PSIsContainer){' | ' + '{0:N1}KB'-f($_.Length/1KB)})" -ForegroundColor Gray
        }
    }
}

# ===== 5. 扫描 PATH 中的 codex =====
Write-Host "[5/6] 扫描 PATH 中的 codex..." -ForegroundColor Yellow
$envPaths = ($env:Path -split ';') | Where-Object { $_ -match "codex|Codex" }
if ($envPaths) {
    Write-Host "  发现 PATH 中的 Codex 路径：" -ForegroundColor White
    $envPaths | ForEach-Object { Write-Host "    📍 $_" -ForegroundColor Gray }
}
# 检查实际运行的 codex
try {
    $whichCodex = Get-Command codex -ErrorAction SilentlyContinue
    if ($whichCodex) {
        Write-Host "  当前默认 codex 命令：" -ForegroundColor Green
        Write-Host "    路径：$($whichCodex.Source)" -ForegroundColor Green
        $ver = & codex --version 2>$null
        Write-Host "    版本：$ver" -ForegroundColor Green
    }
} catch {}

# ===== 6. 记忆文件扫描（这些要保留） =====
Write-Host "[6/6] 扫描记忆/历史文件（这些要保留）..." -ForegroundColor Yellow
$memoryFiles = @()
$memoryDirs = @(
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:USERPROFILE\.codex"
)
foreach ($dir in $memoryDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Recurse -Include "*memory*","*history*","*session*","*conversation*","*.md" -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $memoryFiles += $f
            Write-Host "  💾 $($f.FullName) ($('{0:N1}KB'-f($f.Length/1KB)))" -ForegroundColor Green
        }
    }
}
if ($memoryFiles.Count -eq 0) {
    Write-Host "  (未找到独立的记忆文件)" -ForegroundColor Gray
}

# ===== 汇总 =====
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   扫描完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "检测到以下 Codex 安装/残留：" -ForegroundColor Magenta

# 汇总输出
$allFound = @()
if (Test-Path "$env:APPDATA\npm\codex") { $allFound += "npm全局安装: $env:APPDATA\npm\codex" }
foreach ($dir in $codexDirs) { if (Test-Path $dir) { $allFound += "配置目录: $dir" } }
foreach ($path in $desktopPaths) { if (Test-Path $path) { $allFound += "桌面端: $path" } }
if ($allFound.Count -eq 0) { $allFound += "(未找到任何安装)" }
$allFound | ForEach-Object { Write-Host "  ⚠️  $_" -ForegroundColor Yellow }

Write-Host ""
Write-Host "推荐操作：运行 Codex_彻底清理.ps1 进行清理" -ForegroundColor Green
Write-Host ""

# 暂停，让用户看到结果
Read-Host "按 Enter 键退出"
