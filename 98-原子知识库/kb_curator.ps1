# kb_curator.ps1 - 原子知识库定期整理脚本
# 功能：价值重判、统计报告、标记过期、清理死条目
# 用法：.\kb_curator.ps1 -Mode report
# 用法：.\kb_curator.ps1 -Mode revalue
# 用法：.\kb_curator.ps1 -Mode cleanup

param(
    [ValidateSet("report","revalue","cleanup")]
    [string]$Mode = "report",
    [int]$StaleDays = 30
)

$kbPath = "D:\知识库\99-原子知识库"
$today = Get-Date
$report = @()

# === 报告模式 ===
if ($Mode -eq "report") {
    Write-Host "========================================="
    Write-Host "  原子知识库健康报告"
    Write-Host "  日期: $($today.ToString('yyyy-MM-dd'))"
    Write-Host "========================================="
    
    $totalEntries = 0
    $totalUsed = 0
    $totalUnused = 0
    $totalLowConfidence = 0
    
    $files = Get-ChildItem "$kbPath\*.jsonl"
    foreach ($f in $files) {
        $lines = Get-Content $f.FullName -Encoding UTF8 | Where-Object { $_.Trim() }
        $count = $lines.Count
        $used = 0
        $unused = 0
        $lowConf = 0
        
        foreach ($line in $lines) {
            $entry = $line | ConvertFrom-Json
            if ($entry.use_count -gt 0) { $used++ } else { $unused++ }
            if ($entry.confidence -in @("C","D")) { $lowConf++ }
        }
        
        $totalEntries += $count
        $totalUsed += $used
        $totalUnused += $unused
        $totalLowConfidence += $lowConf
        
        $bar = "█" * [Math]::Min(20, $count) + "░" * [Math]::Max(0, 20 - $count)
        Write-Host ""
        Write-Host "$($f.Name): $count 条"
        Write-Host "  已用: $used | 未用: $unused | 低置信: $lowConf"
    }
    
    Write-Host ""
    Write-Host "--- 汇总 ---"
    Write-Host "总条目:     $totalEntries"
    Write-Host "已使用:     $totalUsed ($([Math]::Round($totalUsed/$totalEntries*100))%)"
    Write-Host "未使用:     $totalUnused"
    Write-Host "低置信度:   $totalLowConfidence (C/D级)"
    
    # 标签分布
    Write-Host ""
    Write-Host "--- 热门标签 TOP 10 ---"
    $indexPath = "$kbPath\index.json"
    if (Test-Path $indexPath) {
        $index = Get-Content $indexPath -Encoding UTF8 -Raw | ConvertFrom-Json
        $tagCounts = @()
        $index.tag_index.PSObject.Properties | ForEach-Object {
            $tagCounts += [PSCustomObject]@{
                Tag = $_.Name
                Count = @($_.Value).Count
            }
        }
        $tagCounts | Sort-Object Count -Descending | Select-Object -First 10 | ForEach-Object {
            $bar = "█" * [Math]::Min(15, $_.Count)
            Write-Host "  $($_.Tag): $bar ($($_.Count))"
        }
    }
}

# === 价值重判模式 ===
if ($Mode -eq "revalue") {
    Write-Host "========================================="
    Write-Host "  价值重判 - 标记待审查条目"
    Write-Host "========================================="
    
    $staleDate = $today.AddDays(-$StaleDays)
    $staleEntries = @()
    
    $files = Get-ChildItem "$kbPath\*.jsonl"
    foreach ($f in $files) {
        $lines = Get-Content $f.FullName -Encoding UTF8 | Where-Object { $_.Trim() }
        foreach ($line in $lines) {
            $entry = $line | ConvertFrom-Json
            
            $isStale = $false
            $reason = ""
            
            # 条件1：use_count=0 且 confidence=C/D 且创建超过30天
            if ($entry.use_count -eq 0 -and $entry.confidence -in @("C","D")) {
                $created = [DateTime]::Parse($entry.created)
                if ($created -lt $staleDate) {
                    $isStale = $true
                    $reason = "未使用+低置信+超过${StaleDays}天"
                }
            }
            
            # 条件2：use_count=0 且 创建超过60天
            if ($entry.use_count -eq 0) {
                $created = [DateTime]::Parse($entry.created)
                if ($created -lt $today.AddDays(-60)) {
                    $isStale = $true
                    $reason = "未使用+超过60天"
                }
            }
            
            if ($isStale) {
                $staleEntries += [PSCustomObject]@{
                    Id = $entry.id
                    Content = $entry.Content.Substring(0, [Math]::Min(50, $entry.Content.Length))
                    Confidence = $entry.confidence
                    UseCount = $entry.use_count
                    Created = $entry.created
                    File = $f.Name
                    Reason = $reason
                }
            }
        }
    }
    
    if ($staleEntries.Count -eq 0) {
        Write-Host "无待审查条目"
    } else {
        Write-Host "待审查条目: $($staleEntries.Count) 条"
        Write-Host ""
        $staleEntries | ForEach-Object {
            Write-Host "  [$($_.Id)] $($_.Content)..."
            Write-Host "    置信度:$($_.Confidence) 使用:$($_.UseCount) 创建:$($_.Created) 原因:$($_.Reason)"
        }
        Write-Host ""
        Write-Host "建议：人工审查后决定保留/归档/删除"
    }
}

# === 清理模式（保守） ===
if ($Mode -eq "cleanup") {
    Write-Host "========================================="
    Write-Host "  清理模式 - 仅标记，不删除"
    Write-Host "========================================="
    
    $archiveDir = "$kbPath\archive"
    if (-not (Test-Path $archiveDir)) {
        New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    }
    
    $marked = 0
    $files = Get-ChildItem "$kbPath\*.jsonl"
    foreach ($f in $files) {
        $lines = Get-Content $f.FullName -Encoding UTF8 | Where-Object { $_.Trim() }
        $kept = @()
        $archived = @()
        
        foreach ($line in $lines) {
            $entry = $line | ConvertFrom-Json
            
            # 保守策略：仅归档 use_count=0 且 confidence=D 且超过60天
            $shouldArchive = $false
            if ($entry.confidence -eq "D" -and $entry.use_count -eq 0) {
                $created = [DateTime]::Parse($entry.created)
                if ($created -lt $today.AddDays(-60)) {
                    $shouldArchive = $true
                }
            }
            
            if ($shouldArchive) {
                $archived += $line
                $marked++
            } else {
                $kept += $line
            }
        }
        
        if ($archived.Count -gt 0) {
            # 归档
            $archiveFile = "$archiveDir\$($f.Name).archive_$(Get-Date -Format 'yyyyMMdd')"
            $archived | ForEach-Object { Add-Content -Path $archiveFile -Value $_ -Encoding UTF8 }
            # 保留文件不变（仅标记）
            Write-Host "$($f.Name): $($archived.Count) 条标记归档（原始文件保留）"
        }
    }
    
    if ($marked -eq 0) {
        Write-Host "无条目需要归档"
    } else {
        Write-Host "共标记 $marked 条归档（已保存到 archive/ 目录）"
    }
}

# 写入审计日志
$auditDir = "$kbPath\audit"
if (Test-Path $auditDir) {
    $auditEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        action = "curation_$Mode"
        agent = "Hermes"
        result = "mode=$Mode"
    } | ConvertTo-Json -Compress
    Add-Content -Path "$auditDir\audit.jsonl" -Value $auditEntry -Encoding UTF8
}
