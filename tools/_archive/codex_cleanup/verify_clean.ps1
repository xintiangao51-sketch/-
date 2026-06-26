# Codex Post-Restart Verification
$ErrorActionPreference = "SilentlyContinue"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   CODEX POST-RESTART VERIFICATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ===== CHECK 1: Old directories =====
Write-Host "[1/5] Checking old directories..." -ForegroundColor Yellow
$dirsToCheck = @(
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex",
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:LOCALAPPDATA\OpenAI",
    "$env:LOCALAPPDATA\Programs\OpenAI",
    "$env:ProgramFiles\OpenAI"
)
$foundAny = $false
foreach ($dir in $dirsToCheck) {
    if (Test-Path $dir) {
        Write-Host "  [REMAINING] $dir" -ForegroundColor Red
        $foundAny = $true
    }
}
if (-not $foundAny) {
    Write-Host "  [OK] All old directories cleaned" -ForegroundColor Green
}

# ===== CHECK 2: npm =====
Write-Host "[2/5] Checking npm..." -ForegroundColor Yellow
$npmFiles = @(
    "$env:APPDATA\npm\codex",
    "$env:APPDATA\npm\codex.cmd",
    "$env:APPDATA\npm\codex.ps1",
    "$env:APPDATA\npm\node_modules\@openai\codex"
)
$foundNpm = $false
foreach ($f in $npmFiles) {
    if (Test-Path $f) {
        Write-Host "  [REMAINING] $f" -ForegroundColor Red
        $foundNpm = $true
    }
}
if (-not $foundNpm) {
    Write-Host "  [OK] npm directory clean" -ForegroundColor Green
}

# ===== CHECK 3: Environment variables =====
Write-Host "[3/5] Checking environment variables..." -ForegroundColor Yellow
$envVarsToCheck = @("CODEX_HOME", "CODEX_PROXY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "DEEPSEEK_API_KEY")
foreach ($varName in $envVarsToCheck) {
    $userVal = [Environment]::GetEnvironmentVariable($varName, "User")
    $procVal = [Environment]::GetEnvironmentVariable($varName, "Process")
    if ($userVal -or $procVal) {
        Write-Host "  [FOUND] $varName = $($userVal)$($procVal)" -ForegroundColor Yellow
        if ($varName -match "DEEPSEEK|OPENAI") {
            Write-Host "         (this is your API key, keep it - not Codex related)" -ForegroundColor Gray
        }
    }
}
Write-Host "  [OK] No Codex-related env vars remain" -ForegroundColor Green

# ===== CHECK 4: PATH =====
Write-Host "[4/5] Checking PATH..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$sysPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($userPath -match "codex|Codex|npm") {
    Write-Host "  [INFO] User PATH contains npm (this is normal):" -ForegroundColor Gray
    ($userPath -split ';') | Where-Object { $_ -match "codex|Codex|npm" } | ForEach-Object {
        Write-Host "       $_" -ForegroundColor Gray
    }
} else {
    Write-Host "  [INFO] No npm in user PATH - will be added when Node.js runs" -ForegroundColor Yellow
}
Write-Host "  [OK] No Codex-specific PATH entries" -ForegroundColor Green

# ===== CHECK 5: CLI command =====
Write-Host "[5/5] Checking if 'codex' command exists..." -ForegroundColor Yellow
try {
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  [FOUND] codex still available: $($cmd.Source)" -ForegroundColor Red
    } else {
        Write-Host "  [OK] 'codex' command not found - clean slate" -ForegroundColor Green
    }
} catch {
    Write-Host "  [OK] 'codex' command not found - clean slate" -ForegroundColor Green
}

# ===== D: Drive check =====
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   D: DRIVE PROJECT DATA (these stay, they're yours)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
if (Test-Path "D:\") {
    Get-ChildItem -Path "D:\" -Directory -Filter ".codex" -Recurse -ErrorAction SilentlyContinue -Depth 3 | ForEach-Object {
        $size = "{0:N2} MB" -f ((Get-ChildItem -Recurse $_.FullName -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB)
        Write-Host "  [PROJECT] $($_.FullName) ($size) - will be reused by Codex" -ForegroundColor Cyan
    }
}

# ===== Summary =====
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$hasRemaining = $foundAny -or $foundNpm
if ($hasRemaining) {
    Write-Host "There ARE remaining files to clean up." -ForegroundColor Red
} else {
    Write-Host "System is CLEAN. Ready for fresh install." -ForegroundColor Green
}

Write-Host ""
Read-Host "Press Enter to exit"
