# kb_query.ps1 - 原子知识库查询工具
# 用法：.\kb_query.ps1 -Type "principles" -Tag "新疆"
# 用法：.\kb_query.ps1 -Search "定额"

param(
    [string]$Type = "",
    [string]$Tag = "",
    [string]$Search = "",
    [int]$Limit = 10
)

$kbPath = "D:\知识库\99-原子知识库"

# 确定查询文件
if ($Type) {
    $files = @("$kbPath\$Type.jsonl")
    if (-not (Test-Path $files[0])) {
        Write-Host "错误：类型 '$Type' 不存在。可用类型：principles, methods, cases, anti_patterns, tools, insights"
        exit 1
    }
} else {
    $files = Get-ChildItem "$kbPath\*.jsonl" | Select-Object -ExpandProperty FullName
}

$results = @()
foreach ($file in $files) {
    $lines = Get-Content $file -Encoding UTF8
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $entry = $line | ConvertFrom-Json
        
        $match = $true
        if ($Tag) {
            $match = $entry.tags -contains $Tag
        }
        if ($Search -and $match) {
            $match = $entry.content -match $Search
        }
        
        if ($match) {
            $results += $entry
        }
    }
}

# 输出结果
if ($results.Count -eq 0) {
    Write-Host "未找到匹配结果"
} else {
    $results | Select-Object -First $Limit | ForEach-Object {
        Write-Host "[$($_.id)] [$($_.confidence)] $($_.content)"
        Write-Host "  标签: $($_.tags -join ', ') | 来源: $($_.source)"
        Write-Host ""
    }
    Write-Host "共找到 $($results.Count) 条结果（显示前 $Limit 条）"
}
