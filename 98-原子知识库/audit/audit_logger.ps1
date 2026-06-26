# audit_logger.ps1 - 原子知识库审计日志工具
# 用法：.\audit_logger.ps1 -Action "查询" -Agent "Hermes" -Query "取费费率" -Result "命中3条" -Score 95

param(
    [string]$Action,
    [string]$Agent,
    [string]$Query = "",
    [string]$Result = "",
    [int]$Score = 0,
    [string]$TaskId = ""
)

$logFile = "D:\知识库\99-原子知识库\audit\audit.jsonl"

$entry = @{
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    action = $Action
    agent = $Agent
    query = $Query
    result = $Result
    score = $Score
    task_id = $TaskId
} | ConvertTo-Json -Compress

Add-Content -Path $logFile -Value $entry -Encoding UTF8
Write-Host "审计日志已记录：$Action by $Agent"
