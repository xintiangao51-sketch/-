# Codex FINAL Verify - check EVERYTHING before reinstall
$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   CODEX FINAL VERIFICATION - Check EVERY trace" -ForegroundColor Cyan
Write-Host "   Run this BEFORE installing Codex Desktop" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()

# ===== 1. OLD DIRECTORIES =====
Write-Host "[1/8] Old directories..." -ForegroundColor Yellow
$dirsToCheck = @(
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex",
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:LOCALAPPDATA\OpenAI",
    "$env:LOCALAPPDATA\Programs\OpenAI",
    "$env:ProgramFiles\OpenAI",
    "$env:ProgramFiles\Codex"
)
$dirCount = 0
foreach ($dir in $dirsToCheck) {
    if (Test-Path $dir) {
        Write-Host "  [DIR] FOUND - $dir" -ForegroundColor Red
        $issues += "Directory: $dir"
        $dirCount++
    }
}
if ($dirCount -eq 0) { Write-Host "  [OK] No old directories found" -ForegroundColor Green }

# ===== 2. NPM =====
Write-Host "[2/8] npm packages..." -ForegroundColor Yellow

# Check npm global list
$npmList = npm list -g --depth=0 2>$null
if ($npmList -match "codex|@openai/codex") {
    Write-Host "  [NPM] FOUND - npm global still has codex:" -ForegroundColor Red
    $npmList | Select-String "codex" | ForEach-Object { Write-Host "       $_" -ForegroundColor Red }
    $issues += "npm global package still installed"
} else {
    Write-Host "  [OK] npm global list clean" -ForegroundColor Green
}

# Check npm cache
$npmCache = npm cache ls 2>$null | Select-String "codex|openai" -SimpleMatch
if ($npmCache) {
    Write-Host "  [NPM CACHE] Codex entries in npm cache - safe to ignore" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] npm cache clean" -ForegroundColor Green
}

# Check npm-global dir on D:
$npmGlobalDir = "D:\Codex_Workspace\npm-global"
if (Test-Path $npmGlobalDir) {
    $codexInNpmGlobal = Get-ChildItem "$npmGlobalDir\node_modules\@openai" -ErrorAction SilentlyContinue
    $codexShims = Get-ChildItem "$npmGlobalDir\codex*" -ErrorAction SilentlyContinue
    if ($codexInNpmGlobal -or $codexShims) {
        Write-Host "  [NPM-GLOBAL] FOUND - D:\Codex_Workspace\npm-global still has codex:" -ForegroundColor Red
        $codexInNpmGlobal | ForEach-Object { Write-Host "       $($_.FullName)" -ForegroundColor Red }
        $codexShims | ForEach-Object { Write-Host "       $($_.FullName)" -ForegroundColor Red }
        $issues += "D: npm-global has codex remnants"
    } else {
        Write-Host "  [OK] D: npm-global clean" -ForegroundColor Green
    }
}

# ===== 3. AppData all locations =====
Write-Host "[3/8] All AppData locations..." -ForegroundColor Yellow
$appDataLocs = @("$env:LOCALAPPDATA", "$env:APPDATA", "$env:USERPROFILE\AppData\LocalLow")
$appDataCount = 0
foreach ($base in $appDataLocs) {
    $codexItems = Get-ChildItem $base -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue
    foreach ($item in $codexItems) {
        Write-Host "  [APPDATA] FOUND - $($item.FullName)" -ForegroundColor Red
        $issues += "AppData: $($item.FullName)"
        $appDataCount++
    }
}
if ($appDataCount -eq 0) { Write-Host "  [OK] All AppData locations clean" -ForegroundColor Green }

# ===== 4. TEMP =====
Write-Host "[4/8] Temp folders..." -ForegroundColor Yellow
$tempLocs = @("$env:TEMP", "$env:LOCALAPPDATA\Temp", "C:\Windows\Temp")
$tempCount = 0
foreach ($base in $tempLocs) {
    if (Test-Path $base) {
        $codexItems = Get-ChildItem $base -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue
        foreach ($item in $codexItems) {
            Write-Host "  [TEMP] $($item.FullName)" -ForegroundColor Yellow
            $tempCount++
        }
    }
}
if ($tempCount -eq 0) { Write-Host "  [OK] Temp folders clean" -ForegroundColor Green }

# ===== 5. ENV VARS =====
Write-Host "[5/8] Environment variables..." -ForegroundColor Yellow
$envVarIssues = $false
$envVarsToCheck = @("CODEX_HOME", "CODEX_PROXY", "CODEX_PATH")
foreach ($varName in $envVarsToCheck) {
    $userVal = [Environment]::GetEnvironmentVariable($varName, "User")
    $procVal = [Environment]::GetEnvironmentVariable($varName, "Process")
    if ($userVal) {
        Write-Host "  [ENV] FOUND - $varName = $userVal (User)" -ForegroundColor Red
        $issues += "Env var: $varName (User)"
        $envVarIssues = $true
    }
}
if (-not $envVarIssues) { Write-Host "  [OK] No Codex env vars" -ForegroundColor Green }

# ===== 6. PATH =====
Write-Host "[6/8] PATH..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$sysPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$pathIssues = $false

if ($userPath -match "codex|Codex") {
    Write-Host "  [PATH] FOUND - User PATH has Codex:" -ForegroundColor Red
    ($userPath -split ';') | Where-Object { $_ -match "codex|Codex" } | ForEach-Object {
        Write-Host "       $_" -ForegroundColor Red
        $issues += "PATH: $_"
    }
    $pathIssues = $true
}
if ($sysPath -match "codex|Codex") {
    Write-Host "  [PATH] FOUND - System PATH has Codex:" -ForegroundColor Red
    ($sysPath -split ';') | Where-Object { $_ -match "codex|Codex" } | ForEach-Object {
        Write-Host "       $_" -ForegroundColor Red
        $issues += "System PATH: $_"
    }
    $pathIssues = $true
}
if (-not $pathIssues) { Write-Host "  [OK] PATH clean" -ForegroundColor Green }

# ===== 7. CLI command =====
Write-Host "[7/8] 'codex' command..." -ForegroundColor Yellow
try {
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  [CLI] FOUND - codex still available: $($cmd.Source)" -ForegroundColor Red
        $issues += "codex command: $($cmd.Source)"
    } else {
        Write-Host "  [OK] No 'codex' command found" -ForegroundColor Green
    }
} catch {
    Write-Host "  [OK] No 'codex' command found" -ForegroundColor Green
}

# ===== 8. Shortcuts =====
Write-Host "[8/8] Shortcuts..." -ForegroundColor Yellow
$shortcutLocs = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu",
    "$env:PUBLIC\Desktop",
    "$env:USERPROFILE\Desktop"
)
$shortcutCount = 0
foreach ($loc in $shortcutLocs) {
    if (Test-Path $loc) {
        $shortcuts = Get-ChildItem $loc -Recurse -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue
        foreach ($s in $shortcuts) {
            Write-Host "  [SHORTCUT] FOUND - $($s.FullName)" -ForegroundColor Red
            $issues += "Shortcut: $($s.FullName)"
            $shortcutCount++
        }
    }
}
if ($shortcutCount -eq 0) { Write-Host "  [OK] No Codex shortcuts found" -ForegroundColor Green }

# ===== D: Drive project data =====
Write-Host ""
Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "D: Drive project data (these are YOURS - KEEP THEM)" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
$dProjects = Get-ChildItem "D:\" -Directory -Filter ".codex" -Recurse -ErrorAction SilentlyContinue -Depth 3
foreach ($p in $dProjects) {
    Write-Host "  [PROJECT] $($p.FullName)" -ForegroundColor Cyan
}

# ===== SUMMARY =====
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   RESULTS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "  SYSTEM IS COMPLETELY CLEAN." -ForegroundColor Green
    Write-Host "  No Codex traces found anywhere." -ForegroundColor Green
    Write-Host ""
    Write-Host "  You can safely install Codex Desktop from:" -ForegroundColor White
    Write-Host "    https://chatgpt.com/codex" -ForegroundColor White
    Write-Host "    or run: winget install Codex -s msstore" -ForegroundColor White
} else {
    Write-Host "  $($issues.Count) ISSUE(S) FOUND:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "  Clean these up before installing Codex Desktop." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
