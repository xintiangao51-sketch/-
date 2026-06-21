# Codex Deep Scan v2 - NO Chinese chars in script
$ErrorActionPreference = "SilentlyContinue"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   CODEX DEEP SCAN - ALL LOCATIONS" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$outputFile = "$env:TEMP\codex_deep_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
"Codex Deep Scan Report - $(Get-Date)" | Out-File $outputFile
"" | Out-File $outputFile -Append

# =====================================================================
# 1. SHORTCUTS
# =====================================================================
Write-Host "[1/10] ALL Shortcuts..." -ForegroundColor Yellow
"=== SHORTCUTS ===" | Out-File $outputFile -Append

$shortcutLocs = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu",
    "$env:PUBLIC\Desktop",
    "$env:USERPROFILE\Desktop",
    "$env:USERPROFILE\Links",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch",
    "C:\Users\Public\Desktop"
)

foreach ($loc in $shortcutLocs) {
    if (Test-Path $loc) {
        Get-ChildItem -Path $loc -Recurse -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            $msg = "[SHORTCUT] $($_.FullName)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
            if ($_.Extension -eq ".lnk") {
                try {
                    $shell = New-Object -ComObject WScript.Shell
                    $sc = $shell.CreateShortcut($_.FullName)
                    "       Target: $($sc.TargetPath)" | Out-File $outputFile -Append
                } catch {}
            }
        }
    }
}

# =====================================================================
# 2. D: Drive - Codex workspace data
# =====================================================================
Write-Host "[2/10] D: Drive Codex data..." -ForegroundColor Yellow
"=== D: DRIVE ===" | Out-File $outputFile -Append

# Look for .codex directories on D: (up to 5 levels deep)
$dRoot = "D:\"
if (Test-Path $dRoot) {
    Get-ChildItem -Path $dRoot -Directory -Filter ".codex" -Recurse -ErrorAction SilentlyContinue -Depth 3 | ForEach-Object {
        $items = Get-ChildItem -Recurse $_.FullName -ErrorAction SilentlyContinue
        $size = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
        $msg = "[D: CODEX] $($_.FullName) ($size)"
        Write-Host "  $msg" -ForegroundColor Yellow
        $msg | Out-File $outputFile -Append
    }
    # config.toml on D:
    Get-ChildItem -Path $dRoot -Filter "config.toml" -Recurse -ErrorAction SilentlyContinue -Depth 3 | ForEach-Object {
        $msg = "[D: TOML] $($_.FullName)"
        Write-Host "  $msg" -ForegroundColor Yellow
        $msg | Out-File $outputFile -Append
    }
}

# =====================================================================
# 3. Registry
# =====================================================================
Write-Host "[3/10] Registry..." -ForegroundColor Yellow
"=== REGISTRY ===" | Out-File $outputFile -Append

$regBases = @("HKCU:\Software", "HKLM:\Software")
foreach ($base in $regBases) {
    if (Test-Path $base) {
        Get-ChildItem $base -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match "codex|Codex|OpenAI" } | ForEach-Object {
            $msg = "[REG] $($_.PSPath)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
        }
    }
}

# =====================================================================
# 4. ALL AppData
# =====================================================================
Write-Host "[4/10] ALL AppData..." -ForegroundColor Yellow
"=== APPDATA ===" | Out-File $outputFile -Append

$appDataLocs = @(
    "$env:LOCALAPPDATA",
    "$env:APPDATA",
    "$env:USERPROFILE\AppData\LocalLow"
)
foreach ($base in $appDataLocs) {
    if (Test-Path $base) {
        Get-ChildItem $base -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            $items = Get-ChildItem -Recurse $_.FullName -ErrorAction SilentlyContinue
            $size = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
            $msg = "[APPDATA] $($_.FullName) ($size)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
        }
    }
}

# =====================================================================
# 5. Temp folders
# =====================================================================
Write-Host "[5/10] Temp folders..." -ForegroundColor Yellow
"=== TEMP ===" | Out-File $outputFile -Append

$tempLocs = @("$env:TEMP", "$env:LOCALAPPDATA\Temp", "C:\Windows\Temp")
$foundTemp = $false
foreach ($base in $tempLocs) {
    if (Test-Path $base) {
        Get-ChildItem $base -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            $msg = "[TEMP] $($_.FullName)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
            $foundTemp = $true
        }
    }
}
if (-not $foundTemp) { Write-Host "  (none)" -ForegroundColor Gray }

# =====================================================================
# 6. Program Files
# =====================================================================
Write-Host "[6/10] Program Files..." -ForegroundColor Yellow
"=== PROGRAM FILES ===" | Out-File $outputFile -Append

$progLocs = @(
    "$env:ProgramFiles",
    "${env:ProgramFiles(x86)}",
    "$env:LOCALAPPDATA\Programs"
)
foreach ($base in $progLocs) {
    if (Test-Path $base) {
        Get-ChildItem $base -Include "*codex*","*Codex*","*CODEX*","*OpenAI*" -ErrorAction SilentlyContinue | ForEach-Object {
            $msg = "[PROG] $($_.FullName)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
        }
    }
}

# =====================================================================
# 7. All user profiles
# =====================================================================
Write-Host "[7/10] All user profiles..." -ForegroundColor Yellow
"=== USER PROFILES ===" | Out-File $outputFile -Append

$userProfiles = Get-ChildItem "C:\Users" -ErrorAction SilentlyContinue
foreach ($user in $userProfiles) {
    $searchPaths = @(
        "$($user.FullName)\.codex",
        "$($user.FullName)\.config\codex",
        "$($user.FullName)\AppData\Roaming\codex",
        "$($user.FullName)\AppData\Local\codex",
        "$($user.FullName)\AppData\Local\OpenAI",
        "$($user.FullName)\AppData\Local\Programs\OpenAI"
    )
    foreach ($p in $searchPaths) {
        $matches = Get-ChildItem $p -ErrorAction SilentlyContinue
        if ($matches) {
            $msg = "[USER:$($user.Name)] $p"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
        }
    }
}

# =====================================================================
# 8. Startup / Scheduled tasks
# =====================================================================
Write-Host "[8/10] Startup & Scheduled tasks..." -ForegroundColor Yellow
"=== STARTUP ===" | Out-File $outputFile -Append

$startupPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
)
foreach ($p in $startupPaths) {
    if (Test-Path $p) {
        Get-ChildItem $p -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            $msg = "[STARTUP] $($_.FullName)"
            Write-Host "  $msg" -ForegroundColor Yellow
            $msg | Out-File $outputFile -Append
        }
    }
}

# Scheduled tasks
try {
    $tasks = schtasks /query /fo CSV /nh 2>$null | Select-String -Pattern "codex|Codex" -SimpleMatch
    if ($tasks) {
        $msg = "[SCHTASK] Codex scheduled tasks found"
        Write-Host "  $msg" -ForegroundColor Yellow
        $msg | Out-File $outputFile -Append
        $tasks | ForEach-Object { "       $_" | Out-File $outputFile -Append }
    } else {
        Write-Host "  No Codex scheduled tasks" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Could not check scheduled tasks" -ForegroundColor Gray
}

# =====================================================================
# 9. Environment variables
# =====================================================================
Write-Host "[9/10] Environment variables..." -ForegroundColor Yellow
"=== ENV VARS ===" | Out-File $outputFile -Append

Get-ChildItem Env: | Where-Object { $_.Name -match "CODEX|OPENAI" } | ForEach-Object {
    $msg = "[ENV] $($_.Name)=$($_.Value)"
    Write-Host "  $msg" -ForegroundColor Yellow
    $msg | Out-File $outputFile -Append
}

# PATH check
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$sysPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($userPath -match "codex|Codex") {
    $msg = "[PATH USER] CONTAINS CODEX"
    Write-Host "  $msg" -ForegroundColor Red
    $msg | Out-File $outputFile -Append
    ($userPath -split ';') | Where-Object { $_ -match "codex|Codex" } | ForEach-Object {
        "       $_" | Out-File $outputFile -Append
        Write-Host "       $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [PATH USER] clean" -ForegroundColor Green
}
if ($sysPath -match "codex|Codex") {
    $msg = "[PATH SYS] CONTAINS CODEX"
    Write-Host "  $msg" -ForegroundColor Red
    $msg | Out-File $outputFile -Append
} else {
    Write-Host "  [PATH SYS] clean" -ForegroundColor Green
}

# =====================================================================
# 10. .npmrc cache (npm keeps a cache too)
# =====================================================================
Write-Host "[10/10] npm cache & other..." -ForegroundColor Yellow
"=== NPM CACHE ===" | Out-File $outputFile -Append

$npmCache = npm cache ls 2>$null | Select-String -Pattern "codex|openai" -SimpleMatch
if ($npmCache) {
    Write-Host "  Codex entries in npm cache" -ForegroundColor Yellow
    "npm cache contains Codex entries" | Out-File $outputFile -Append
} else {
    Write-Host "  No Codex in npm cache" -ForegroundColor Gray
}

# Check for .codex files anywhere in user home
Get-ChildItem "$env:USERPROFILE" -Include ".codexignore",".codexguard","AGENTS.md" -Recurse -ErrorAction SilentlyContinue -Depth 2 | ForEach-Object {
    $msg = "[HOME FILE] $($_.FullName)"
    Write-Host "  $msg" -ForegroundColor Yellow
    $msg | Out-File $outputFile -Append
}

# =====================================================================
# SUMMARY
# =====================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   SCAN COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Report saved to: $outputFile" -ForegroundColor Cyan
Write-Host ""

# Quick visual summary of issues
if ($userPath -match "codex|Codex") {
    Write-Host "ISSUE: PATH still has Codex entries - restart needed" -ForegroundColor Red
}
Write-Host "Check the report above for any remaining shortcuts" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
