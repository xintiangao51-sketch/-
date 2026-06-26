---
tags: ["AI", "日志"]
created: 2026-06-24
type: reference
---

# 新疆造价信息采集 · Windows 任务计划配置

> **目标**：让 `daily_crawl.py` 每日 08:00（北京时间）自动跑，结果写入 `D:\知识库\01-造价核心\造价信息日报_YYYY-MM-DD.md`
> **环境**：Windows 10/11，需 Python 3.x + requests + bs4 + openpyxl

---

## 一键配置（PowerShell 管理员）

打开 **PowerShell（管理员）** → 执行下面这段：

```powershell
# === 新疆造价信息采集 - 自动配置脚本 ===
# 用法：复制全部 → 粘贴到 PowerShell（管理员）→ 回车

# 1. 定义变量
$taskName = "新疆造价信息采集"
$pythonPath = (Get-Command python.exe).Source
$scriptPath = "D:\知识库\07-AI工具与技能\daily_crawl.py"
$logDir = "D:\知识库\01-造价核心\采集日志"
$startTime = "08:00"

# 2. 确保日志目录存在
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# 3. 删除已存在的同名任务
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# 4. 创建新任务
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument "`"$scriptPath`" --quick" `
    -WorkingDirectory "D:\知识库"

$trigger = New-ScheduledTaskTrigger -Daily -At $startTime

$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "每日 08:00 自动采集新疆造价信息（住建厅+xjzj.com），生成日报至 D:\知识库\01-造价核心\造价信息日报_YYYY-MM-DD.md" `
    -Force | Out-Null

Write-Host "✅ 任务已创建: $taskName" -ForegroundColor Green
Write-Host "📋 任务详情：" -ForegroundColor Cyan
Get-ScheduledTask -TaskName $taskName | Format-List TaskName, State, Description
```

---

## 验证 / 查询 / 管理

### 查看任务状态

```powershell
Get-ScheduledTask -TaskName "新疆造价信息采集" | Format-List *
```

### 立即手动触发（不等 08:00）

```powershell
Start-ScheduledTask -TaskName "新疆造价信息采集"
```

### 查看最近运行历史

```powershell
Get-ScheduledTaskInfo -TaskName "新疆造价信息采集" | Format-List LastRunTime, LastTaskResult, NextRunTime
```

### 删除任务

```powershell
Unregister-ScheduledTask -TaskName "新疆造价信息采集" -Confirm:$false
```

---

## 备选：用 schtasks 命令（不依赖 PowerShell）

```cmd
:: 创建任务（管理员 CMD）
schtasks /create ^
  /tn "新疆造价信息采集" ^
  /tr "python D:\知识库\07-AI工具与技能\daily_crawl.py --quick" ^
  /sc daily ^
  /st 08:00 ^
  /ru SYSTEM ^
  /rl HIGHEST ^
  /f

:: 查询
schtasks /query /tn "新疆造价信息采集" /v /fo list

:: 手动运行
schtasks /run /tn "新疆造价信息采集"

:: 删除
schtasks /delete /tn "新疆造价信息采集" /f
```

---

## 查看历史日志

任务跑过之后，会留下日志：

```powershell
# 控制台日志：直接打开看
notepad "D:\知识库\01-造价核心\采集日志\cron.log"

# 日报文件：按日期
Get-ChildItem "D:\知识库\01-造价核心\造价信息日报_*.md" | Sort-Object LastWriteTime -Descending

# 原始数据：按日期 JSON
Get-ChildItem "D:\知识库\01-造价核心\采集日志\raw_*.json" | Sort-Object LastWriteTime -Descending
```

---

## 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 任务不触发 | 系统休眠 / 任务被禁用 | `电源选项 → 关闭显示器时间 → 永不`<br>检查 `Get-ScheduledTask \| ? State -ne Ready` |
| 任务运行但无输出 | 路径错误 / 权限 | 检查 `$scriptPath` 是否正确存在<br>改用 `--no-report` 测试 |
| LastTaskResult ≠ 0 | Python 错误 | 看 `cron.log` 末尾的错误栈 |
| 日报格式乱码 | 编码问题 | 已在脚本中处理 `gb2312 → utf-8` 兜底 |

---

## 变更日志

- **v1.0** (2026-06-24)：初版配置（PowerShell + schtasks 双方案）

---

🔗 **AI工具总览**：[[07-AI工具与技能/AI工具与技能-总览]]
