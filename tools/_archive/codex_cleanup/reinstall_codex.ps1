# Codex Fresh Install Guide
# Run this AFTER restarting your computer
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CODEX FRESH INSTALL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
$hasNode = $false
try {
    $nodeVer = node --version
    $hasNode = $true
    Write-Host "[OK] Node.js: $nodeVer" -ForegroundColor Green
    $npmVer = npm --version
    Write-Host "[OK] npm: v$npmVer" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Node.js not found" -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org (LTS version)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Select install method:" -ForegroundColor Yellow
Write-Host "  [A] npm install @openai/codex (recommended, requires Node.js)" -ForegroundColor Cyan
Write-Host "  [B] Official install script from chatgpt.com" -ForegroundColor Cyan
Write-Host "  [C] Manual download from GitHub Releases" -ForegroundColor Cyan
$choice = Read-Host "Enter A, B, or C"

switch ($choice.ToUpper()) {
    "A" {
        Write-Host ""
        Write-Host ">>> Method A: npm install" -ForegroundColor Green
        if (-not $hasNode) {
            Write-Host "Node.js required. Install from https://nodejs.org first" -ForegroundColor Red
            Start-Process "https://nodejs.org"
            Read-Host "Press Enter after installing Node.js"
        }

        Write-Host "Installing @openai/codex..." -ForegroundColor Yellow
        npm install -g @openai/codex

        Write-Host ""
        Write-Host "Verifying..." -ForegroundColor Yellow
        try {
            $ver = & codex --version
            Write-Host "[OK] Codex installed! Version: $ver" -ForegroundColor Green
        } catch {
            Write-Host "[FAIL] Installation may have failed. Check errors above." -ForegroundColor Red
        }
    }
    "B" {
        Write-Host ""
        Write-Host ">>> Method B: Official install script" -ForegroundColor Green
        Write-Host "This will download and run a script from chatgpt.com" -ForegroundColor Yellow
        Write-Host ""
        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -eq "y") {
            powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
            Write-Host ""
            try {
                $ver = & codex --version
                Write-Host "[OK] Codex installed! Version: $ver" -ForegroundColor Green
            } catch {
                Write-Host "[FAIL] Installation may have failed. Check errors above." -ForegroundColor Red
            }
        }
    }
    "C" {
        Write-Host ""
        Write-Host ">>> Method C: Manual download" -ForegroundColor Green
        Start-Process "https://github.com/openai/codex/releases/latest"
        Write-Host "1. Download the Windows binary from GitHub Releases" -ForegroundColor Yellow
        Write-Host "2. Extract to: C:\Users\20752\codex-bin\" -ForegroundColor Yellow
        Write-Host "3. Add that folder to your system PATH" -ForegroundColor Yellow
    }
}

# Post-install: create config.toml with sandbox disabled
Write-Host ""
Write-Host "Creating config.toml (sandbox disabled for Windows)..." -ForegroundColor Yellow
$configDir = "$env:APPDATA\codex"
New-Item -ItemType Directory -Path $configDir -Force | Out-Null
$configContent = @'
sandbox_mode = "off"
'@
Set-Content -Path "$configDir\config.toml" -Value $configContent
Write-Host "[OK] Created: $configDir\config.toml" -ForegroundColor Green
Write-Host "     Content: sandbox_mode = \"off\"" -ForegroundColor Gray

# Show backup info
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Memory backup location:" -ForegroundColor Yellow
$backups = Get-ChildItem -Path "$env:USERPROFILE" -Directory -Filter "Codex_Backup_*" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if ($backups) {
    $backups | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Cyan }
    Write-Host ""
    Write-Host "To restore memory files, copy them back after first launch" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Run Codex desktop:" -ForegroundColor Green
Write-Host "  codex app" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
