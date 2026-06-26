# Codex Deep Scan - Find ALL remaining traces
# Run as Administrator

$ErrorActionPreference = "SilentlyContinue"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   CODEX DEEP SCAN - Find EVERY trace" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$outputFile = "$env:TEMP\codex_deep_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
"Codex Deep Scan Report - $(Get-Date)" | Out-File $outputFile
"" | Out-File $outputFile -Append

function Write-Log {
    param([string]$text, [string]$color="White")
    Write-Host $text -ForegroundColor $color
    $text | Out-File $outputFile -Append
}

# =====================================================================
# 1. SHORTCUTS - All possible locations
# =====================================================================
Write-Log "============================================" Cyan
Write-Log "[1/10] Shortcuts - ALL locations" Cyan
Write-Log "============================================" Cyan

$shortcutLocations = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs",
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs",
    "$env:ProgramData\Microsoft\Windows\Start Menu",
    "$env:PUBLIC\Desktop",
    "$env:USERPROFILE\Desktop",
    "$env:USERPROFILE\Links",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\StartMenu",
    "C:\Users\Public\Desktop",
    "C:\ProgramData\Desktop"
)

foreach ($loc in $shortcutLocations) {
    if (Test-Path $loc) {
        $shortcuts = Get-ChildItem -Path $loc -Include "*codex*", "*Codex*", "*CODEX*" -Recurse -ErrorAction SilentlyContinue
        foreach ($s in $shortcuts) {
            Write-Log "  [SHORTCUT] $($s.FullName)" Yellow
            # Check if it's a .lnk file and get its target
            if ($s.Extension -eq ".lnk") {
                try {
                    $shell = New-Object -ComObject WScript.Shell
                    $shortcut = $shell.CreateShortcut($s.FullName)
                    Write-Log "       Target: $($shortcut.TargetPath)" Gray
                    Write-Log "       Arguments: $($shortcut.Arguments)" Gray
                } catch {}
            }
        }
    }
}

# =====================================================================
# 2. D: Drive scan - .codex directories and workspace data
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[2/10] D: Drive - Codex workspace data" Cyan
Write-Log "============================================" Cyan

# Scan D: root and common locations
$dDrives = @("D:\", "D:\知识库", "D:\造价工作台", "D:\造价知识库")
foreach ($d in $dDrives) {
    if (Test-Path $d) {
        # Look for .codex directories
        $dotCodexDirs = Get-ChildItem -Path $d -Directory -Filter ".codex" -Recurse -ErrorAction SilentlyContinue -Depth 5
        foreach ($dir in $dotCodexDirs) {
            $items = Get-ChildItem -Path $dir.FullName -Recurse -ErrorAction SilentlyContinue
            $size = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
            Write-Log "  [D:\.codex] $($dir.FullName) ($size)" Yellow
            $items | Select-Object -First 20 | ForEach-Object {
                Write-Log "       $($_.Name)" Gray
            }
        }

        # Look for codex config files
        $cfgFiles = Get-ChildItem -Path $d -Include "config.toml", "codex.json", ".codex.json" -Recurse -ErrorAction SilentlyContinue -Depth 5
        foreach ($f in $cfgFiles) {
            Write-Log "  [D:CONFIG] $($f.FullName)" Yellow
        }

        # Look for codex session/history files
        $sessionFiles = Get-ChildItem -Path $d -Include "*history*", "*session*", "*conversation*", "*codex*state*" -Recurse -ErrorAction SilentlyContinue -Depth 5
        foreach ($f in $sessionFiles) {
            Write-Log "  [D:DATA] $($f.FullName) ($('{0:N1}KB' -f ($f.Length/1KB)))" Yellow
        }
    }
}

# =====================================================================
# 3. Registry entries
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[3/10] Registry entries" Cyan
Write-Log "============================================" Cyan

$regPaths = @(
    "HKCU:\Software\OpenAI",
    "HKCU:\Software\codex",
    "HKLM:\Software\OpenAI",
    "HKLM:\Software\codex",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*codex*",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*codex*"
)

foreach ($regPath in $regPaths) {
    $items = Get-Item -Path $regPath -ErrorAction SilentlyContinue
    if ($items) {
        Write-Log "  [REGISTRY] $regPath" Yellow
        $items.Property | ForEach-Object {
            Write-Log "       $_ = $($items.GetValue($_))" Gray
        }
    }
}

# Also search registry broadly
$regBases = @("HKCU:\Software", "HKLM:\Software")
foreach ($base in $regBases) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match "codex|Codex|OpenAI.*Codex" } | ForEach-Object {
            Write-Log "  [REGISTRY] $($_.PSPath)" Yellow
        }
    }
}

# =====================================================================
# 4. All AppData locations
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[4/10] ALL AppData locations" Cyan
Write-Log "============================================" Cyan

$appDataLocs = @(
    "$env:LOCALAPPDATA",
    "$env:APPDATA",
    "$env:USERPROFILE\AppData\LocalLow"
)
foreach ($base in $appDataLocs) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -Include "*codex*", "*Codex*", "*CODEX*" -ErrorAction SilentlyContinue | ForEach-Object {
            $items = Get-ChildItem -Recurse $_.FullName -ErrorAction SilentlyContinue
            $size = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
            Write-Log "  [APPDATA] $($_.FullName) ($size)" Yellow
            if ($_.PSIsContainer) {
                Get-ChildItem $_.FullName -ErrorAction SilentlyContinue | Select-Object -First 15 | ForEach-Object {
                    Write-Log "       $($_.Name)" Gray
                }
            }
        }
    }
}

# =====================================================================
# 5. TEMP folders
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[5/10] Temp folders" Cyan
Write-Log "============================================" Cyan

$tempLocs = @(
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp",
    "C:\Windows\Temp"
)
$codexTempCount = 0
foreach ($base in $tempLocs) {
    if (Test-Path $base) {
        $codexItems = Get-ChildItem -Path $base -Include "*codex*", "*Codex*" -ErrorAction SilentlyContinue
        foreach ($item in $codexItems) {
            Write-Log "  [TEMP] $($item.FullName)" Yellow
            $codexTempCount++
        }
    }
}
if ($codexTempCount -eq 0) {
    Write-Log "  No Codex temp files found" Gray
}

# =====================================================================
# 6. Program Files
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[6/10] Program Files" Cyan
Write-Log "============================================" Cyan

$progFilesLocs = @(
    "$env:ProgramFiles",
    "${env:ProgramFiles(x86)}",
    "$env:LOCALAPPDATA\Programs"
)
foreach ($base in $progFilesLocs) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -Include "*codex*", "*Codex*", "*CODEX*", "*OpenAI*" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Log "  [PROGRAM] $($_.FullName)" Yellow
        }
    }
}

# =====================================================================
# 7. All user profiles on system
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[7/10] All user profiles" Cyan
Write-Log "============================================" Cyan

$userProfiles = Get-ChildItem "C:\Users" -ErrorAction SilentlyContinue
foreach ($user in $userProfiles) {
    $searchPaths = @(
        "$($user.FullName)\.codex",
        "$($user.FullName)\.config\codex",
        "$($user.FullName)\AppData\Roaming\codex",
        "$($user.FullName)\AppData\Local\codex",
        "$($user.FullName)\AppData\Roaming\npm\codex*",
        "$($user.FullName)\AppData\Local\Programs\OpenAI",
        "$($user.FullName)\AppData\Local\OpenAI"
    )
    foreach ($p in $searchPaths) {
        $matches = Get-ChildItem -Path $p -ErrorAction SilentlyContinue
        if ($matches) {
            Write-Log "  [USER:$($user.Name)] $p" Yellow
        }
    }
}

# =====================================================================
# 8. Taskbar pinned items
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[8/10] Taskbar / Start pinned items" Cyan
Write-Log "============================================" Cyan

$pinnedPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
)
foreach ($p in $pinnedPaths) {
    if (Test-Path $p) {
        Get-ChildItem -Path $p -Include "*codex*", "*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Log "  [STARTUP] $($_.FullName)" Yellow
        }
    }
}

# Check scheduled tasks
Write-Log "  Checking scheduled tasks..." Gray
try {
    $schTasks = schtasks /query /fo LIST /v 2>$null | Select-String -Pattern "codex|Codex" -Context 0,2
    if ($schTasks) {
        Write-Log "  [SCHEDULED TASK] Found:" Yellow
        $schTasks | ForEach-Object { Write-Log "       $_" Yellow }
    } else {
        Write-Log "  No Codex scheduled tasks" Gray
    }
} catch {
    Write-Log "  Could not check scheduled tasks" Gray
}

# =====================================================================
# 9. Environment variables
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[9/10] Environment variables" Cyan
Write-Log "============================================" Cyan

# Check for Codex-related env vars
$envVars = Get-ChildItem Env: | Where-Object { $_.Name -match "CODEX|OPENAI|codex" }
if ($envVars) {
    foreach ($v in $envVars) {
        Write-Log "  [ENV] $($v.Name) = $($v.Value)" Yellow
    }
} else {
    Write-Log "  No Codex/OpenAI environment variables found" Gray
}

# Check User and System PATH for codex
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$sysPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($userPath -match "codex|Codex") {
    Write-Log "  [PATH USER] Contains codex entries - CLEANUP MISSED THIS" Red
    ($userPath -split ';') | Where-Object { $_ -match "codex|Codex" } | ForEach-Object {
        Write-Log "       $_" Red
    }
} else {
    Write-Log "  [PATH USER] Clean" Green
}
if ($sysPath -match "codex|Codex") {
    Write-Log "  [PATH SYSTEM] Contains codex entries" Red
    ($sysPath -split ';') | Where-Object { $_ -match "codex|Codex" } | ForEach-Object {
        Write-Log "       $_" Red
    }
} else {
    Write-Log "  [PATH SYSTEM] Clean" Green
}

# =====================================================================
# 10. D: drive - .codex project configs (deep scan)
# =====================================================================
Write-Log "" White
Write-Log "============================================" Cyan
Write-Log "[10/10] D: Drive - deep scan for .codex project dirs" Cyan
Write-Log "============================================" Cyan

$dDriveRoot = "D:\"
if (Test-Path $dDriveRoot) {
    $dCodexDirs = Get-ChildItem -Path $dDriveRoot -Directory -Filter ".codex" -Recurse -ErrorAction SilentlyContinue -Depth 3
    if ($dCodexDirs) {
        foreach ($dir in $dCodexDirs) {
            $items = Get-ChildItem -Path $dir.FullName -Recurse -ErrorAction SilentlyContinue
            $size = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
            Write-Log "  [PROJECT] $($dir.FullName) ($size)" Yellow
            Write-Log "       Contains project-level Codex config" Gray
            Write-Log "       This will be read by Codex on reinstall!" Cyan
            $items | Select-Object -First 10 | ForEach-Object {
                Write-Log "       $($_.Name)" Gray
            }
        }
    } else {
        Write-Log "  No .codex project directories found on D:" Gray
    }

    # Check for .codexignore, .codexguard files
    $guardFiles = Get-ChildItem -Path $dDriveRoot -Include ".codexignore", ".codexguard", "AGENTS.md", ".rules" -Recurse -ErrorAction SilentlyContinue -Depth 3
    foreach ($f in $guardFiles) {
        Write-Log "  [RULES] $($f.FullName)" Yellow
    }
}

# =====================================================================
# SUMMARY
# =====================================================================
Write-Log "" White
Write-Log "================================================================" Cyan
Write-Log "   DEEP SCAN COMPLETE" Cyan
Write-Log "================================================================" Cyan
Write-Log "" White
Write-Log "Report saved to: $outputFile" Cyan
Write-Log "" White
Read-Host "Press Enter to exit"
