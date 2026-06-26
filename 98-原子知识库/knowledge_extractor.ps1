# knowledge_extractor.ps1 - 从交付物中提取原子知识
# 用法：.\knowledge_extractor.ps1 -Type principle -Content "人工调增只计税金" -Tags "人工费,取费" -Source "XX项目"
# 用法：.\knowledge_extractor.ps1 -BatchFile "extract_batch.json"

param(
    [ValidateSet("principle","method","case","anti_pattern","tool","insight")]
    [string]$Type = "",
    [string]$Content = "",
    [string]$Tags = "",
    [string]$Source = "",
    [string]$Confidence = "B",
    [string]$BatchFile = ""
)

$kbPath = "D:\知识库\99-原子知识库"
$typeMap = @{
    "principle" = "principles"
    "method" = "methods"
    "case" = "cases"
    "anti_pattern" = "anti_patterns"
    "tool" = "tools"
    "insight" = "insights"
}

function Add-AtomicEntry {
    param(
        [string]$EntryType,
        [string]$EntryContent,
        [string]$EntryTags,
        [string]$EntrySource,
        [string]$EntryConfidence
    )
    
    $fileType = $typeMap[$EntryType]
    $filePath = "$kbPath\$fileType.jsonl"
    
    if (-not (Test-Path $filePath)) {
        Write-Host "错误：文件不存在 $filePath"
        return
    }
    
    # 生成ID：类型前缀-年份-序号
    $prefixMap = @{
        "principle" = "P"
        "method" = "M"
        "case" = "C"
        "anti_pattern" = "AP"
        "tool" = "T"
        "insight" = "I"
    }
    $prefix = $prefixMap[$EntryType]
    $year = (Get-Date).ToString("yyyy")
    
    # 读取现有最大序号
    $maxSeq = 0
    $lines = Get-Content $filePath -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match "$prefix-$year-(\d+)") {
            $seq = [int]$Matches[1]
            if ($seq -gt $maxSeq) { $maxSeq = $seq }
        }
    }
    $newId = "$prefix-$year-$("{0:D3}" -f ($maxSeq + 1))"
    
    # 构建标签数组
    $tagArray = $EntryTags -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    
    # 构建记录
    $entry = @{
        id = $newId
        type = $EntryType
        content = $EntryContent
        tags = $tagArray
        source = $EntrySource
        confidence = $EntryConfidence
        created = (Get-Date -Format "yyyy-MM-dd")
        last_used = $null
        use_count = 0
    } | ConvertTo-Json -Compress
    
    # 追加写入
    Add-Content -Path $filePath -Value $entry -Encoding UTF8
    
    # 更新索引
    Update-Index -NewId $newId -NewType $fileType -NewTags $tagArray
    
    Write-Host "[OK] $newId -> $fileType.jsonl"
    Write-Host "  内容: $EntryContent"
    Write-Host "  标签: $($tagArray -join ', ')"
    Write-Host "  置信度: $EntryConfidence"
    
    return $newId
}

function Update-Index {
    param($NewId, $NewType, $NewTags)
    
    $indexPath = "$kbPath\index.json"
    $index = Get-Content $indexPath -Encoding UTF8 -Raw | ConvertFrom-Json
    
    # 更新计数
    $index.categories.$NewType.count++
    $index.total_entries++
    
    # 更新标签索引
    foreach ($tag in $NewTags) {
        if ($index.tag_index.$tag) {
            $existing = @($index.tag_index.$tag)
            if ($existing -notcontains $NewId) {
                $index.tag_index.$tag = $existing + $NewId
            }
        } else {
            $index.tag_index | Add-Member -NotePropertyName $tag -NotePropertyValue @($NewId) -Force
        }
    }
    
    $index | ConvertTo-Json -Depth 5 | Out-File $indexPath -Encoding UTF8
}

# 单条模式
if ($Type -and $Content) {
    if (-not $Tags) { $Tags = "" }
    if (-not $Source) { $Source = "手动录入" }
    Add-AtomicEntry -EntryType $Type -EntryContent $Content -EntryTags $Tags -EntrySource $Source -EntryConfidence $Confidence
}
# 批量模式
elseif ($BatchFile -and (Test-Path $BatchFile)) {
    $batch = Get-Content $BatchFile -Encoding UTF8 -Raw | ConvertFrom-Json
    foreach ($item in $batch) {
        Add-AtomicEntry `
            -EntryType $item.type `
            -EntryContent $item.content `
            -EntryTags ($item.tags -join ',') `
            -EntrySource $item.source `
            -EntryConfidence $item.confidence
    }
}
else {
    Write-Host "用法："
    Write-Host "  单条：.\knowledge_extractor.ps1 -Type principle -Content '内容' -Tags '标签1,标签2' -Source '来源'"
    Write-Host "  批量：.\knowledge_extractor.ps1 -BatchFile 'batch.json'"
    Write-Host ""
    Write-Host "Type可选：principle, method, case, anti_pattern, tool, insight"
}
