# ============================================================
# Codex 全新安装指南
# 运行前：重启电脑 → 确认已无旧版残留
# ============================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Codex 全新安装向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "本脚本提供两种安装方式，请二选一：" -ForegroundColor Yellow
Write-Host ""

Write-Host "┌─────────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│  方式A：npm 安装（推荐，适合你已经装了Node.js）      │" -ForegroundColor Green
Write-Host "│  方式B：官方安装脚本（自动处理，适合小白）          │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""

# ===== 检测 Node.js =====
$hasNode = $false
try {
    $nodeVer = node --version
    $hasNode = $true
    Write-Host "✅ 检测到 Node.js: $nodeVer" -ForegroundColor Green
    $npmVer = npm --version
    Write-Host "✅ 检测到 npm: v$npmVer" -ForegroundColor Green
} catch {
    Write-Host "❌ 未检测到 Node.js" -ForegroundColor Red
    Write-Host "   → 请先安装 Node.js：https://nodejs.org (LTS版本)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   或使用方式B（官方脚本会自动处理依赖）" -ForegroundColor Gray
}

Write-Host ""
Write-Host "选择安装方式：" -ForegroundColor Yellow
Write-Host "  [A] npm 安装（全局安装 @openai/codex）" -ForegroundColor Cyan
Write-Host "  [B] 官方安装脚本" -ForegroundColor Cyan
Write-Host "  [C] 手动下载 GitHub Release" -ForegroundColor Cyan
$choice = Read-Host "请输入 A、B 或 C"

switch ($choice.ToUpper()) {
    "A" {
        Write-Host ""
        Write-Host ">>> 方式A：npm 安装" -ForegroundColor Green
        if (-not $hasNode) {
            Write-Host "❌ 缺少 Node.js，请先安装" -ForegroundColor Red
            Start-Process "https://nodejs.org"
            exit
        }

        Write-Host "正在安装 @openai/codex..." -ForegroundColor Yellow
        npm install -g @openai/codex

        Write-Host ""
        Write-Host "验证安装..." -ForegroundColor Yellow
        $ver = & codex --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 安装成功！版本: $ver" -ForegroundColor Green
        } else {
            Write-Host "❌ 安装可能失败，请检查报错" -ForegroundColor Red
        }
    }
    "B" {
        Write-Host ""
        Write-Host ">>> 方式B：官方安装脚本" -ForegroundColor Green
        Write-Host "正在下载并执行官方安装脚本..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "⚠️  这是从 chatgpt.com 远程下载的脚本" -ForegroundColor Gray
        $confirm = Read-Host "是否继续？(y/n)"
        if ($confirm -eq "y") {
            powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"

            Write-Host ""
            $ver = & codex --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 安装成功！版本: $ver" -ForegroundColor Green
            } else {
                Write-Host "❌ 安装可能失败，请检查报错" -ForegroundColor Red
            }
        } else {
            Write-Host "已取消" -ForegroundColor Yellow
        }
    }
    "C" {
        Write-Host ""
        Write-Host ">>> 方式C：手动下载 GitHub Release" -ForegroundColor Green
        Write-Host "打开 GitHub Release 页面..." -ForegroundColor Yellow
        Start-Process "https://github.com/openai/codex/releases/latest"
        Write-Host ""
        Write-Host "请手动下载 Windows 版本的二进制文件" -ForegroundColor Yellow
        Write-Host "解压后放到 C:\Users\20752\codex-bin\ 目录" -ForegroundColor Gray
        Write-Host "然后将该目录添加到系统 PATH 中" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# ===== 安装后配置 =====
if ($choice.ToUpper() -eq "A" -or $choice.ToUpper() -eq "B") {
    Write-Host ""
    Write-Host ">>> 安装后配置" -ForegroundColor Green

    Write-Host ""
    Write-Host "是否要创建禁用沙盒的 config.toml？(y/n)" -ForegroundColor Yellow
    $createConfig = Read-Host "(如果没有WSL2，必须先禁用沙盒)"
    if ($createConfig -eq "y") {
        $configDir = "$env:APPDATA\codex"
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        Set-Content -Path "$configDir\config.toml" -Value @'
sandbox_mode = "off"
'@
        Write-Host "✅ 已创建 $configDir\config.toml（沙盒已禁用）" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host ">>> 安装后验证" -ForegroundColor Yellow
    Write-Host "运行以下命令启动 Codex：" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   codex app" -ForegroundColor White
    Write-Host ""
    Write-Host "如果启动正常，安装完成 🎉" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   安装指南结束" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 记忆文件备份位置：" -ForegroundColor Gray
Get-ChildItem -Path "$env:USERPROFILE" -Directory -Filter "Codex_Memory_Backup*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "   $($_.FullName)" -ForegroundColor Cyan
}

Read-Host "按 Enter 键退出"