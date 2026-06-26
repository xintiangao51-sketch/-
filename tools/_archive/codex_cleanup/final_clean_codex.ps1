# Codex FINAL Cleanup - Remove remaining traces
$ErrorActionPreference = "Continue"

Write-Host "================================================================" -ForegroundColor Red
Write-Host "   CODEX FINAL CLEANUP" -ForegroundColor Red
Write-Host "   Targets the 4 remaining directories + env vars" -ForegroundColor Red
Write-Host "================================================================" -ForegroundColor Red
Write-Host ""

Write-Host "This will delete these remaining Codex directories:" -ForegroundColor Yellow
Write-Host "  1. C:\Users\20752\.codex" -ForegroundColor Yellow
Write-Host "  2. C:\Users\20752\.config\codex" -ForegroundColor Yellow
Write-Host "  3. C:\Users\20752\AppData\Roaming\codex" -ForegroundColor Yellow
Write-Host "  4. C:\Users\20752\AppData\Local\OpenAI" -ForegroundColor Yellow
Write-Host "  5. CODEX_HOME environment variable" -ForegroundColor Yellow
Write-Host "  6. CODEX_PROXY environment variable" -ForegroundColor Yellow
Write-Host ""

Write-Host "The following will NOT be deleted (project data):" -ForegroundColor Green
Write-Host "  - D:\Codex_Workspace\.codex" -ForegroundColor Green
Write-Host "  - D:\Hermes Agent中文端\skills\skill-creator\.codex" -ForegroundColor Green
Write-Host "  - C:\Users\20752\Documents\Codex\ (session archives)" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Cyan
    exit
}

# Kill any Codex processes first
Write-Host "[1/6] Killing any Codex processes..." -ForegroundColor Yellow
Get-Process -Name "*codex*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Delete directories one by one with verbose output
Write-Host "[2/6] Deleting remaining directories..." -ForegroundColor Yellow

$dirsToDelete = @(
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex",
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\OpenAI"
)

foreach ($dir in $dirsToDelete) {
    if (Test-Path $dir) {
        try {
            Write-Host "  Attempting to delete: $dir" -ForegroundColor Gray
            # Try normal delete first
            Remove-Item -Path $dir -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Deleted: $dir" -ForegroundColor Green
        } catch {
            Write-Host "  Normal delete failed, trying takeown..." -ForegroundColor Yellow
            try {
                # Take ownership first
                takeown /f "$dir" /r /d y 2>$null
                icacls "$dir" /grant "$env:USERNAME`:F" /T /Q 2>$null
                Remove-Item -Path $dir -Recurse -Force
                if (-not (Test-Path $dir)) {
                    Write-Host "  [OK] Deleted (with ownership): $dir" -ForegroundColor Green
                }
            } catch {
                Write-Host "  [FAIL] Could not delete $dir" -ForegroundColor Red
                Write-Host "         You may need to delete this folder manually" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  [SKIP] Not found: $dir" -ForegroundColor Gray
    }
}

# Delete environment variables
Write-Host "[3/6] Removing environment variables..." -ForegroundColor Yellow

$envVarsToRemove = @("CODEX_HOME", "CODEX_PROXY")
foreach ($varName in $envVarsToRemove) {
    # Check if it exists
    $currentVal = [Environment]::GetEnvironmentVariable($varName, "User")
    if ($currentVal) {
        Write-Host "  Removing $varName=$currentVal" -ForegroundColor Yellow
        [Environment]::SetEnvironmentVariable($varName, $null, "User")
        # Also remove from current session
        Remove-Item -Path "Env:$varName" -ErrorAction SilentlyContinue
        Write-Host "  [OK] Removed $varName" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] $varName not set" -ForegroundColor Gray
    }
}

# Delete shortcuts
Write-Host "[4/6] Removing shortcuts..." -ForegroundColor Yellow

$shortcutDirs = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu",
    "$env:PUBLIC\Desktop",
    "$env:USERPROFILE\Desktop"
)
$foundShortcuts = $false
foreach ($base in $shortcutDirs) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -Recurse -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force
                Write-Host "  [OK] Removed shortcut: $($_.FullName)" -ForegroundColor Green
                $foundShortcuts = $true
            } catch {
                Write-Host "  [FAIL] Could not remove: $($_.FullName)" -ForegroundColor Red
            }
        }
    }
}
if (-not $foundShortcuts) {
    Write-Host "  No shortcuts found in scanned locations" -ForegroundColor Gray
}

# Check taskbar pins (special location)
$taskbarPins = "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
if (Test-Path $taskbarPins) {
    Get-ChildItem $taskbarPins -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  [TASKBAR] $($_.FullName) - unpin manually" -ForegroundColor Yellow
        Write-Host "           Right-click the taskbar icon > Unpin from taskbar" -ForegroundColor Yellow
    }
}

# Check Start Menu tiles
$startTiles = "$env:LOCALAPPDATA\Microsoft\Windows\Shell"
if (Test-Path $startTiles) {
    Get-ChildItem $startTiles -Recurse -Include "*codex*","*Codex*" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  [STARTTILE] $($_.FullName)" -ForegroundColor Yellow
        $_ | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

# Verify
Write-Host "[5/6] Verifying deletion..." -ForegroundColor Yellow
$stillThere = @()
foreach ($dir in $dirsToDelete) {
    if (Test-Path $dir) {
        $stillThere += $dir
    }
}
if ($stillThere.Count -eq 0) {
    Write-Host "  [OK] All directories successfully deleted" -ForegroundColor Green
} else {
    Write-Host "  [WARN] These directories still exist:" -ForegroundColor Yellow
    $stillThere | ForEach-Object { Write-Host "         $_" -ForegroundColor Yellow }
}

# Check env var
$checkHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "User")
$checkProxy = [Environment]::GetEnvironmentVariable("CODEX_PROXY", "User")
if ($checkHome -or $checkProxy) {
    Write-Host "  [WARN] Some env vars still persist (will clear on restart)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Environment variables cleared" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   FINAL CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEP: Restart your computer NOW" -ForegroundColor Magenta
Write-Host ""
Write-Host "After restart:" -ForegroundColor Green
Write-Host "  1. Check that Codex icon is gone from Start Menu / Desktop" -ForegroundColor Green
Write-Host "  2. Run: npm install -g @openai/codex" -ForegroundColor Green
Write-Host "  3. Create config.toml with sandbox_mode = 'off'" -ForegroundColor Green
Write-Host "  4. Run: codex app" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
