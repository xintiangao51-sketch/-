# Codex Complete Cleanup Script
# Backs up memory files, then removes ALL Codex components
# Run as Administrator

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Red
Write-Host "   CODEX COMPLETE CLEANUP" -ForegroundColor Red
Write-Host "   Will BACKUP memory files first" -ForegroundColor Yellow
Write-Host "   Then REMOVE all Codex components" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

$confirmation = Read-Host "WARNING: This will remove ALL Codex components. Continue? (y/n)"
if ($confirmation -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Cyan
    exit
}

# ===== STEP 1: Backup memory files =====
Write-Host "[1/5] Backing up memory files..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "$env:USERPROFILE\Codex_Backup_$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$memoryPatterns = @("*.md", "*memory*", "*history*", "*session*", "*conversation*", "*.jsonl")
$searchDirs = @(
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:USERPROFILE\.codex"
)

$backupCount = 0
foreach ($dir in $searchDirs) {
    if (Test-Path $dir) {
        foreach ($pattern in $memoryPatterns) {
            $files = Get-ChildItem -Path $dir -Recurse -Include $pattern -ErrorAction SilentlyContinue
            foreach ($f in $files) {
                $relPath = $f.FullName.Substring($dir.Length).TrimStart('\')
                $targetFile = Join-Path $backupDir $relPath
                $targetDir = Split-Path $targetFile -Parent
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                Copy-Item -Path $f.FullName -Destination $targetFile -Force
                $backupCount++
            }
        }
    }
}
Write-Host "   Backed up $backupCount files to: $backupDir" -ForegroundColor Green

# ===== STEP 2: Kill Codex processes =====
Write-Host "[2/5] Killing Codex processes..." -ForegroundColor Yellow
$procs = Get-Process -Name "*codex*" -ErrorAction SilentlyContinue
if ($procs) {
    $procs | Stop-Process -Force
    Write-Host "   Killed $($procs.Count) Codex process(es)" -ForegroundColor Green
} else {
    Write-Host "   No running Codex processes" -ForegroundColor Gray
}
Start-Sleep -Seconds 2

# ===== STEP 3: Remove npm global package =====
Write-Host "[3/5] Removing npm global package..." -ForegroundColor Yellow
try {
    $uninstall = npm uninstall -g @openai/codex 2>&1
    Write-Host "   npm uninstall completed" -ForegroundColor Green
} catch {
    Write-Host "   npm uninstall skipped (may not be installed via npm)" -ForegroundColor Yellow
}

# Remove npm residual files
$npmFiles = @(
    "$env:APPDATA\npm\codex",
    "$env:APPDATA\npm\codex.cmd",
    "$env:APPDATA\npm\codex.ps1",
    "$env:APPDATA\npm\node_modules\@openai\codex"
)
foreach ($f in $npmFiles) {
    if (Test-Path $f) {
        Remove-Item -Path $f -Recurse -Force
        Write-Host "   Removed: $f" -ForegroundColor DarkRed
    }
}

# Remove config/cache/install directories (EXCEPT backup dir)
$removeDirs = @(
    "$env:APPDATA\codex",
    "$env:LOCALAPPDATA\codex",
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex",
    "$env:LOCALAPPDATA\Programs\OpenAI",
    "$env:LOCALAPPDATA\Programs\codex",
    "$env:LOCALAPPDATA\OpenAI",
    "$env:ProgramFiles\OpenAI",
    "$env:LOCALAPPDATA\codex-app",
    "$env:LOCALAPPDATA\Codex",
    "$env:USERPROFILE\scoop\apps\codex"
)
foreach ($dir in $removeDirs) {
    if (Test-Path $dir -and $dir -ne $backupDir) {
        try {
            Remove-Item -Path $dir -Recurse -Force
            Write-Host "   Removed: $dir" -ForegroundColor DarkRed
        } catch {
            Write-Host "   Could not remove $dir (may need manual delete)" -ForegroundColor Yellow
        }
    }
}

# Remove shortcuts
$shortcutPaths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Codex*",
    "$env:PUBLIC\Desktop\Codex*",
    "$env:USERPROFILE\Desktop\Codex*"
)
foreach ($pattern in $shortcutPaths) {
    Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -Path $_.FullName -Force
        Write-Host "   Removed shortcut: $($_.FullName)" -ForegroundColor DarkRed
    }
}

# ===== STEP 4: Clean PATH =====
Write-Host "[4/5] Cleaning PATH environment..." -ForegroundColor Yellow
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = ($oldPath -split ';') | Where-Object { $_ -notmatch "codex|Codex" } | Join-String -Separator ';'
if ($oldPath -ne $newPath) {
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = $newPath
    Write-Host "   Removed Codex entries from PATH" -ForegroundColor Green
} else {
    Write-Host "   No Codex entries in PATH" -ForegroundColor Gray
}

# ===== STEP 5: Verify =====
Write-Host "[5/5] Verifying cleanup..." -ForegroundColor Yellow

$remaining = Get-ChildItem -Path "$env:APPDATA\npm" -Filter "*codex*" -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "   WARNING: Residual files found in npm:" -ForegroundColor Yellow
    $remaining | ForEach-Object { Write-Host "      $($_.FullName)" }
} else {
    Write-Host "   npm directory clean" -ForegroundColor Green
}

try {
    $stillExists = Get-Command codex -ErrorAction SilentlyContinue
    if ($stillExists) {
        Write-Host "   WARNING: 'codex' still found in PATH: $($stillExists.Source)" -ForegroundColor Yellow
        Write-Host "   Please restart your computer to complete cleanup" -ForegroundColor Yellow
    } else {
        Write-Host "   'codex' command successfully removed from PATH" -ForegroundColor Green
    }
} catch {}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Memory backup: $backupDir" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Restart your computer NOW" -ForegroundColor Magenta
Write-Host "Then run: D:\path_to_knowledge_base\reinstall_codex.ps1" -ForegroundColor Magenta
Write-Host ""

Read-Host "Press Enter to exit"
