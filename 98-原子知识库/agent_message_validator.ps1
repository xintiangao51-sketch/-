# agent_message_validator.ps1 - AgentMessage四字段验收检查器
# 用法：.\agent_message_validator.ps1 -InputFile "agent_output.md"
# 或：  .\agent_message_validator.ps1 -Text "Thought: ... Action: ... Need: ... Progress: 0.5"

param(
    [string]$InputFile = "",
    [string]$Text = "",
    [string]$Agent = "unknown",
    [string]$TaskId = ""
)

# 读取输入
if ($InputFile -and (Test-Path $InputFile)) {
    $content = Get-Content $InputFile -Encoding UTF8 -Raw
} elseif ($Text) {
    $content = $Text
} else {
    Write-Host "错误：必须提供 -InputFile 或 -Text 参数"
    exit 1
}

# 初始化评分
$score = 100
$issues = @()
$findings = @{
    thought = @{ found = $false; has_source = $false; content = "" }
    action = @{ found = $false; is_specific = $false; content = "" }
    need = @{ found = $false; has_warning = $false; content = "" }
    progress = @{ found = $false; value = -1; content = "" }
}

# === 检查 Thought ===
if ($content -match '(?si)\*{0,2}Thought\*{0,2}\s*[:：]\s*(.+?)(?=\n\*{0,2}(?:Action|Need|Progress))') {
    $findings.thought.found = $true
    $findings.thought.content = $Matches[1].Trim()
    
    # 检查是否有依据引用（定额编号/规范条文/数据来源）
    $sourcePatterns = @('\d+-\d+-\d+', '定额', '规范', '合同第', '条款', '信息价', '来源', '依据', '数据')
    foreach ($p in $sourcePatterns) {
        if ($findings.thought.content -match $p) {
            $findings.thought.has_source = $true
            break
        }
    }
    
    if (-not $findings.thought.has_source) {
        $score -= 15
        $issues += "THOUGHT: 无依据引用（缺少定额编号/规范条文/数据来源）→ 置信度降为C/D"
    }
} else {
    $score -= 25
    $issues += "THOUGHT: 字段缺失 → 不合格"
}

# === 检查 Action ===
if ($content -match '(?si)\*{0,2}Action\*{0,2}\s*[:：]\s*(.+?)(?=\n\*{0,2}(?:Need|Progress))') {
    $findings.action.found = $true
    $findings.action.content = $Matches[1].Trim()
    
    # 检查是否具体可执行（排除模糊词）
    $vagueWords = @('尽快', '适当', '酌情', '考虑', '可能', '也许', '大概', '应该')
    $isVague = $false
    foreach ($w in $vagueWords) {
        if ($findings.action.content -match $w) {
            $isVague = $true
            break
        }
    }
    $findings.action.is_specific = -not $isVague
    
    if ($isVague) {
        $score -= 10
        $issues += "ACTION: 包含模糊词，需具体化"
    }
    if ($findings.action.content.Length -lt 10) {
        $score -= 10
        $issues += "ACTION: 描述过短（<10字），不够具体"
    }
} else {
    $score -= 25
    $issues += "ACTION: 字段缺失 → 不合格"
}

# === 检查 Need ===
if ($content -match '(?si)\*{0,2}Need\*{0,2}\s*[:：]\s*(.+?)(?=\n\*{0,2}(?:Progress))') {
    $findings.need.found = $true
    $findings.need.content = $Matches[1].Trim()
    
    if ($findings.need.content -match '⚠') {
        $findings.need.has_warning = $true
    }
} else {
    # Need不是每轮都必须，但有缺口时必须
    $findings.need.found = $false
}

# === 检查 Progress ===
if ($content -match '(?si)\*{0,2}Progress\*{0,2}\s*[:：]\s*(\d+\.?\d*)') {
    $findings.progress.found = $true
    $findings.progress.value = [double]$Matches[1]
    $findings.progress.content = $Matches[1]
    
    if ($findings.progress.value -lt 0 -or $findings.progress.value -gt 1) {
        $score -= 5
        $issues += "PROGRESS: 值超出0-1范围"
    }
} else {
    $score -= 15
    $issues += "PROGRESS: 字段缺失或格式错误（需0.00-1.00）"
}

# === 输出报告 ===
Write-Host "========================================="
Write-Host "  AgentMessage 验收报告"
Write-Host "========================================="
Write-Host "Agent:    $Agent"
Write-Host "TaskId:   $TaskId"
Write-Host "时间:     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

Write-Host "--- 字段检查 ---"
$status = if ($findings.thought.found) { if ($findings.thought.has_source) { "[OK] 有依据" } else { "[WARN] 无依据" } } else { "[FAIL] 缺失" }
Write-Host "Thought:  $status"

$status = if ($findings.action.found) { if ($findings.action.is_specific) { "[OK] 具体" } else { "[WARN] 模糊" } } else { "[FAIL] 缺失" }
Write-Host "Action:   $status"

if ($findings.need.found) {
    if ($findings.need.has_warning) {
        Write-Host "Need:     [WARN] 有未解决的依赖"
    } else {
        Write-Host "Need:     [OK] 已满足或无依赖"
    }
} else {
    Write-Host "Need:     [N/A] 无缺口"
}

$status = if ($findings.progress.found) { "[OK] $($findings.progress.value)" } else { "[FAIL] 缺失" }
Write-Host "Progress: $status"

Write-Host ""
Write-Host "--- 评分 ---"
$finalScore = [Math]::Max(0, $score)
Write-Host "总分: $finalScore / 100"

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "--- 扣分项 ---"
    foreach ($issue in $issues) {
        Write-Host "  - $issue"
    }
}

Write-Host ""
if ($finalScore -ge 90) {
    Write-Host "结论: PASS - 合格"
} elseif ($finalScore -ge 70) {
    Write-Host "结论: WARN - 需修正后重交"
} else {
    Write-Host "结论: FAIL - 不合格，打回重做"
}
Write-Host "========================================="

# 返回结构化结果
$result = @{
    score = $finalScore
    pass = ($finalScore -ge 90)
    agent = $Agent
    task_id = $TaskId
    issues = $issues
    fields = @{
        thought_found = $findings.thought.found
        thought_has_source = $findings.thought.has_source
        action_found = $findings.action.found
        action_is_specific = $findings.action.is_specific
        need_found = $findings.need.found
        need_has_warning = $findings.need.has_warning
        progress_found = $findings.progress.found
        progress_value = $findings.progress.value
    }
} | ConvertTo-Json -Compress

# 写入审计日志
$auditDir = "D:\知识库\99-原子知识库\audit"
if (Test-Path $auditDir) {
    $auditEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        action = "validation"
        agent = $Agent
        task_id = $TaskId
        score = $finalScore
        pass = ($finalScore -ge 90)
        issues = $issues
    } | ConvertTo-Json -Compress
    Add-Content -Path "$auditDir\audit.jsonl" -Value $auditEntry -Encoding UTF8
}
