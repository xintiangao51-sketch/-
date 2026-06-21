# ============================================================
# Codex 彻底清理脚本（保留记忆文件）
# 用途：清理所有Codex安装/配置/缓存，只保留记忆文件
# 运行方式：右键 → 以管理员身份运行 PowerShell
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Red
Write-Host "   Codex 彻底清理工具" -ForegroundColor Red
Write-Host "   保留：记忆/历史/会话文件" -ForegroundColor Yellow
Write-Host "   删除：安装文件、配置、缓存、日志" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# ===== 确认 =====
$confirmation = Read-Host "⚠️  即将彻底清理所有 Codex 组件，是否继续？(y/n)"
if ($confirmation -ne "y") {
    Write-Host "已取消" -ForegroundColor Cyan
    exit
}

# ===== 第1步：备份记忆文件 =====
Write-Host "[1/5] 备份记忆文件..." -ForegroundColor Yellow
$backupDir = "$env:USERPROFILE\Codex_Memory_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$memoryExtensions = @("*.md", "*memory*", "*history*", "*session*", "*conversation*")
$memoryDirs = @(
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:USERPROFILE\.codex"
)

$backupCount = 0
foreach ($dir in $memoryDirs) {
    if (Test-Path $dir) {
        foreach ($ext in $memoryExtensions) {
            $files = Get-ChildItem -Path $dir -Recurse -Include $ext -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                $relPath = $f.FullName.Substring($dir.Length).TrimStart('\')
                $targetDir = Split-Path "$backupDir\$relPath" -Parent
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                Copy-Item -Path $f.FullName -Destination "$backupDir\$relPath" -Force
                $backupCount++
            }
        }
    }
}
Write-Host "   ✅ 已备份 $backupCount 个记忆文件到：$backupDir" -ForegroundColor Green

# ===== 第2步：关闭所有 Codex 进程 =====
Write-Host "[2/5] 关闭所有 Codex 进程..." -ForegroundColor Yellow
$processes = Get-Process -Name "*codex*" -ErrorAction SilentlyContinue
if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "   ✅ 已关闭 $($processes.Count) 个 Codex 进程" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  未发现运行中的 Codex 进程" -ForegroundColor Gray
}
Start-Sleep -Seconds 2

# ===== 第3步：删除所有安装和配置（保留记忆备份目录） =====
Write-Host "[3/5] 删除 Codex 安装和配置..." -ForegroundColor Yellow

# 3a. npm 全局卸载
Write-Host "   → 卸载 npm 全局包..." -ForegroundColor Gray
try {
    $npmOutput = npm uninstall -g @openai/codex 2>&1
    Write-Host "   ✅ npm 卸载完成" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  npm 卸载跳过（可能已损坏）" -ForegroundColor Yellow
}

# 3b. 删除 npm 残留文件
$npmFiles = @(
    "$env:APPDATA\npm\codex",
    "$env:APPDATA\npm\codex.cmd",
    "$env:APPDATA\npm\codex.ps1",
    "$env:APPDATA\npm\node_modules\@openai\codex"
)
foreach ($f in $npmFiles) {
    if (Test-Path $f) {
        Remove-Item -Path $f -Recurse -Force
        Write-Host "   🗑️  删除: $f" -ForegroundColor DarkRed
    }
}

# 3c. 删除配置目录（但记忆文件已在第1步备份）
$deleteDirs = @(
    "$env:APPDATA\codex",          # 配置 + 可能的记忆
    "$env:LOCALAPPDATA\codex",     # 缓存
    "$env:USERPROFILE\.codex",     # 旧版配置目录
    "$env:USERPROFILE\.config\codex", # 配置
    "$env:LOCALAPPDATA\Programs\OpenAI",  # 桌面端
    "$env:LOCALAPPDATA\Programs\codex",
    "$env:LOCALAPPDATA\OpenAI",
    "$env:ProgramFiles\OpenAI",
    "$env:LOCALAPPDATA\codex-app",
    "$env:LOCALAPPDATA\Codex"
)

# 注意：跳过记忆备份目录
foreach ($dir in $deleteDirs) {
    if (Test-Path $dir -and $dir -ne $backupDir) {
        try {
            Remove-Item -Path $dir -Recurse -Force
            Write-Host "   🗑️  删除: $dir" -ForegroundColor DarkRed
        } catch {
            Write-Host "   ⚠️  无法删除 $dir （需要手动删除）" -ForegroundColor Yellow
        }
    }
}

# 3d. 删除快捷方式
$shortcutPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Codex*",
    "$env:PUBLIC\Desktop\Codex*",
    "$env:USERPROFILE\Desktop\Codex*"
)
foreach ($pattern in $shortcutPaths) {
    Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Force
        Write-Host "   🗑️  删除快捷方式: $($_.FullName)" -ForegroundColor DarkRed
    }
}

# ===== 第4步：清理 PATH 中的 Codex 残留 =====
Write-Host "[4/5] 清理 PATH 环境变量..." -ForegroundColor Yellow
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = ($oldPath -split ';') | Where-Object { $_ -notmatch "codex|Codex" } | Join-String -Separator ';'
if ($oldPath -ne $newPath) {
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = $newPath
    Write-Host "   ✅ 已清理 PATH 中的 Codex 残留" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  PATH 中无 Codex 残留" -ForegroundColor Gray
}

# ===== 第5步：验证清理 =====
Write-Host "[5/5] 验证清理结果..." -ForegroundColor Yellow
$remaining = Get-ChildItem -Path "$env:APPDATA\npm" -Filter "*codex*" -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "   ⚠️  仍有残留文件：" -ForegroundColor Yellow
    $remaining | ForEach-Object { Write-Host "      $($_.FullName)" }
} else {
    Write-Host "   ✅ npm 目录已完全清理" -ForegroundColor Green
}

# 检查命令行是否还能找到 codex
try {
    $stillExists = Get-Command codex -ErrorAction SilentlyContinue
    if ($stillExists) {
        Write-Host "   ⚠️  PATH 中仍有 codex：$($stillExists.Source)" -ForegroundColor Yellow
        Write-Host "   → 请重启电脑确保彻底清除" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ 命令行中已找不到 codex" -ForegroundColor Green
    }
} catch {}

# ===== 汇总 =====
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   清理完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 记忆文件已备份到：$backupDir" -ForegroundColor Green
Write-Host "   重装后如果发现Codex无法读取记忆，从这里恢复" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  重要：请先重启电脑，再运行 Codex_重装指南.ps1 进行全新安装" -ForegroundColor Magenta
Write-Host ""

Read-Host "按 Enter 键退出"
