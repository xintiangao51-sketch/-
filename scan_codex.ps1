# Codex Full System Scanner
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CODEX FULL SYSTEM SCANNER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1/6] Scanning npm global installs..." -ForegroundColor Yellow

$npmFiles = @(
    "$env:APPDATA\npm\codex",
    "$env:APPDATA\npm\codex.cmd",
    "$env:APPDATA\npm\codex.ps1"
)
foreach ($f in $npmFiles) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $size = "{0:N0} KB" -f ($item.Length / 1KB)
        Write-Host "  [NPM] $f ($size)" -ForegroundColor White
    }
}

# Check npm global modules
$npmModule = "$env:APPDATA\npm\node_modules\@openai\codex"
if (Test-Path $npmModule) {
    $verFile = "$npmModule\package.json"
    if (Test-Path $verFile) {
        $pkg = Get-Content $verFile -Raw | ConvertFrom-Json
        Write-Host "  [NPM] $npmModule (v$($pkg.version))" -ForegroundColor White
    } else {
        Write-Host "  [NPM] $npmModule" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "[2/6] Scanning desktop app installs..." -ForegroundColor Yellow

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
        $items = Get-ChildItem -Path $path -Recurse -Depth 2 -ErrorAction SilentlyContinue
        $totalSize = "{0:N1} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
        Write-Host "  [DESKTOP] $path ($totalSize)" -ForegroundColor White
        $items | Where-Object { -not $_.PSIsContainer } | Select-Object -First 10 | ForEach-Object {
            Write-Host "         $($_.Name)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "[3/6] Scanning config and cache directories..." -ForegroundColor Yellow

$codexDirs = @(
    "$env:LOCALAPPDATA\codex",
    "$env:APPDATA\codex",
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex"
)
foreach ($dir in $codexDirs) {
    if (Test-Path $dir) {
        $items = Get-ChildItem -Recurse $dir -ErrorAction SilentlyContinue
        $totalSize = "{0:N2} MB" -f (($items | Measure-Object -Property Length -Sum).Sum / 1MB)
        Write-Host "  [CONFIG] $dir ($totalSize)" -ForegroundColor White
        Get-ChildItem $dir -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.PSIsContainer) {
                Write-Host "         [DIR] $($_.Name)" -ForegroundColor Gray
            } else {
                Write-Host "         $($_.Name) ($('{0:N1}KB' -f ($_.Length/1KB)))" -ForegroundColor Gray
            }
        }
    }
}

Write-Host ""
Write-Host "[4/6] Locating config.toml files..." -ForegroundColor Yellow

$tomlSearch = @(
    "$env:LOCALAPPDATA\codex",
    "$env:APPDATA\codex",
    "$env:USERPROFILE\.codex",
    "$env:USERPROFILE\.config\codex",
    "$env:USERPROFILE"
)
foreach ($base in $tomlSearch) {
    if (Test-Path $base) {
        Get-ChildItem -Path $base -Filter "config.toml" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "  [TOML] $($_.FullName)" -ForegroundColor Yellow
            Get-Content $_.FullName -ErrorAction SilentlyContinue | ForEach-Object {
                Write-Host "       | $_" -ForegroundColor DarkYellow
            }
        }
    }
}

Write-Host ""
Write-Host "[5/6] Checking PATH for Codex..." -ForegroundColor Yellow

$envPaths = ($env:Path -split ';') | Where-Object { $_ -match "codex|Codex" }
if ($envPaths) {
    Write-Host "  PATH entries containing codex:" -ForegroundColor White
    $envPaths | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  No codex entries found in PATH" -ForegroundColor Gray
}

try {
    $cmd = Get-Command codex -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  Current default codex command:" -ForegroundColor Green
        Write-Host "    Path: $($cmd.Source)" -ForegroundColor Green
    } else {
        Write-Host "  'codex' command not found in current PATH" -ForegroundColor Gray
    }
} catch {
    Write-Host "  'codex' command not found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[6/6] Scanning memory/history files..." -ForegroundColor Yellow

$foundMemory = $false
foreach ($dir in $codexDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Recurse -Include "*.md", "history*", "memory*", "session*", "conversation*", "*.jsonl" -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $foundMemory = $true
            Write-Host "  [MEMORY] $($f.FullName) ($('{0:N1}KB' -f ($f.Length/1KB)))" -ForegroundColor Green
        }
    }
}
if (-not $foundMemory) {
    Write-Host "  No memory files found" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SCAN COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$found = @()
if (Test-Path "$env:APPDATA\npm\codex") { $found += "npm: $env:APPDATA\npm\codex" }
if (Test-Path "$env:APPDATA\codex") { $found += "config: $env:APPDATA\codex" }
if (Test-Path "$env:LOCALAPPDATA\codex") { $found += "cache: $env:LOCALAPPDATA\codex" }
if (Test-Path "$env:USERPROFILE\.codex") { $found += "old config: $env:USERPROFILE\.codex" }
if (Test-Path "$env:USERPROFILE\.config\codex") { $found += "user config: $env:USERPROFILE\.config\codex" }

foreach ($path in @("$env:LOCALAPPDATA\Programs\OpenAI","$env:LOCALAPPDATA\Programs\codex","$env:LOCALAPPDATA\OpenAI","$env:ProgramFiles\OpenAI")) {
    if (Test-Path $path) { $found += "desktop: $path" }
}

if ($found.Count -eq 0) {
    Write-Host "  No Codex installations found." -ForegroundColor Green
} else {
    Write-Host "  Found $($found.Count) Codex components:" -ForegroundColor Yellow
    $found | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Next step: Run clean_codex.ps1 to remove everything" -ForegroundColor Green
Read-Host "Press Enter to exit"
