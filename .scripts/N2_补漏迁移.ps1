# N2_补漏迁移.ps1
# 第四步：补漏迁移 - 把 99-归档库/_09项目资料_杂项\ 剩余 42 文件按文件名分类
# 区分：真实业务资料（应迁）vs 个人/无关资料（可忽略）

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$srcBase = "D:\知识库\99-归档库\_09项目资料_杂项\其他零散文件"
$dstBase = "D:\高治国资料\知识库原始资料\12-已结项目资料"

if (-not (Test-Path $srcBase)) {
    Write-Error "源目录不存在: $srcBase"
    exit 1
}

# 补漏映射表（基于实际剩余 42 文件）
# 格式：源文件相对路径 → 目标子目录
$漏迁 = @{
    # 01-合同招投标 漏迁
    "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段 加筋陡坡明墩工程02标（项目名称）加筋陡坡明墩工程02标（包件名称）公路工程（专业类别名称）劳务分包招标.zip" = "G0711乌尉"
    "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段 桩基工程（项目名称）桩基工程（包件名称）公路工程（专业类别名称）劳务分包招标(1).zip" = "G0711乌尉"
    "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段（项目名称）明墩工程01标（包件名称）公路工程（专业类别名称）劳务分包招标.zip" = "G0711乌尉"
    "01-合同招投标\借款协议.docx" = "金国机械租赁部"
    "01-合同招投标\建筑工程劳务分包合同(1).pdf" = "霍尔果斯檀悦府"

    # 02-工程量与计价 漏迁
    "02-工程量与计价\3.29发  风机基础及道路标段建议价格.xlsx" = "木垒风电"
    "02-工程量与计价\乌鲁木齐市土方工程预算书编制说明 一.docx" = "将军庙水库"
    "02-工程量与计价\体育学院室外清单(1).docx" = "喀什体校"
    "02-工程量与计价\场外护坡及防洪工程清单综合报价2025.6.27.pdf" = "前进水源护坡"
    "02-工程量与计价\工程量预算书 一.docx" = "红雁池"
    "02-工程量与计价\新疆交通建设集团股份有限公司新疆新和至拜城铁路项目总承包EPC（一标段）桥涵及路堤防护工程劳务服务2025.5.18.xlsx" = "G0711乌尉"
    "02-工程量与计价\新疆交通建设集团股份有限公司新疆新和至拜城铁路项目总承包EPC（一标段）桥涵及路堤防护工程劳务服务采购项目固化清单(1).xlsx" = "G0711乌尉"
    "02-工程量与计价\羊圈工程量清单及报价.xlsx" = "红墩二道渠"
    "02-工程量与计价\表1_分部分项工程量清单与计价表.xlsx" = "将军庙水库"
    "02-工程量与计价\表2_综合单价分析表.xlsx" = "将军庙水库"
    "02-工程量与计价\表3_措施项目清单与计价表.xlsx" = "将军庙水库"
    "02-工程量与计价\表4_其他项目清单与计价表.xlsx" = "将军庙水库"
    "02-工程量与计价\表5_人材机汇总表.xlsx" = "将军庙水库"

    # 03-图纸资料 漏迁
    "03-图纸资料\3#大棚结构施工图0122.dwg" = "其他"
    "03-图纸资料\G219线昭苏-温宿ZW-3标拱形骨架护坡.pdf" = "G0711乌尉"
    "03-图纸资料\G219线昭苏-温宿ZW-3标方格网.pdf" = "G0711乌尉"
    "03-图纸资料\G219线昭苏-温宿ZW-3标第三篇 路基、路面（路基防护、挡墙、排水工程）.pdf" = "G0711乌尉"
    "03-图纸资料\G219线昭苏-温宿ZW-3标被动防护网.pdf" = "G0711乌尉"
    "03-图纸资料\商务标-青岛德泰36350482.09(1).PDF" = "其他"
    "03-图纸资料\景航酒店(1).pdf" = "其他"
    "03-图纸资料\缴费凭证_BILL-20260120-018533.pdf" = "其他"
    "03-图纸资料\羊圈_t3.dwg" = "红墩二道渠"
    "03-工程量与计价\羊圈_t3.pdf" = "红墩二道渠"  # 上一版误分类
    "03-图纸资料\融信-签收凭证-陕西三耕建设工程有限公司-SYJSGS-20251230-005-000019.pdf" = "其他"
    "03-图纸资料\融资凭证_融信_SYJSGS-20251230-005-000019.pdf" = "其他"
    "03-图纸资料\（4月3日）4、5号给水泵变频改造（建筑、结构、电气）.pdf" = "其他"

    # 06-物资采购 漏迁
    "06-物资采购\G219线昭苏-温宿ZW-3标混凝土护坡工程.pdf" = "G0711乌尉"

    # 07-往来文件 漏迁
    "07-往来文件\博州博乐市前进水源项目护坡工程技术方案.docx" = "博乐前进水源项目"
    "07-往来文件\现浇楼板支撑架施工方案.docx" = "其他"

    # 08-结算归档 漏迁
    "08-结算归档\投资人+施工总承包模式定义.docx" = "鼎梁柱公司"
    "08-结算归档\新疆伊犁酒店外墙粉刷施工单价分析及利润率计算.docx" = "天山乡综合能源站"
    "08-结算归档\红雁池工程内容说明.docx" = "红雁池"

    # 09-人员与行政 漏迁
    "09-人员与行政\不拖欠农民工工资承诺函2026年6月2日.pdf" = "鼎梁柱公司"
    "09-人员与行政\代发工资委托书2026年4月份农民工（砌筑班组）工资2026年6月2日.docx" = "鼎梁柱公司"
    "09-人员与行政\微信图片_20250523125523.png" = "其他"
}

# 不迁的文件（个人/无关，保留在 99-归档库）
$不迁 = @{
    "03-图纸资料\2025年监理工程师职业资格考试.pdf" = "个人考试资料（高治国本人）"
    "03-图纸资料\2025年监理工程师职业资格考试承诺书.pdf" = "个人考试资料（高治国本人）"
    "03-图纸资料\四川中恒铭泰公司信息.pdf" = "企业查询（一次性）"
}

# 重要：检查不迁文件是否真的在源中
$不迁存在 = @()
foreach ($f in $不迁.Keys) {
    $path = Join-Path $srcBase $f
    if (Test-Path $path) {
        $不迁存在 += $f
    }
}

# === 阶段 1：报告不迁文件 ===
Write-Host "===== 阶段 1：识别不迁文件 =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔒 保留在 99-归档库（不迁）：" -ForegroundColor Yellow
foreach ($f in $不迁存在) {
    $reason = $不迁[$f]
    Write-Host "  ⏸️  $f"
    Write-Host "        原因: $reason" -ForegroundColor DarkYellow
}
Write-Host ""

# === 阶段 2：执行补漏迁移 ===
Write-Host "===== 阶段 2：补漏迁移 =====" -ForegroundColor Cyan
Write-Host ""

$totalMoved = 0
$totalSkipped = 0
$totalError = 0
$log = @()

foreach ($entry in $漏迁.GetEnumerator()) {
    $relPath = $entry.Key
    $target = $entry.Value

    $srcFile = Join-Path $srcBase $relPath
    if (-not (Test-Path $srcFile)) {
        Write-Host "  ⚠️  跳过（源不存在）: $relPath" -ForegroundColor DarkYellow
        $totalError++
        continue
    }

    $dstFile = Join-Path $dstBase $target
    $dstPath = Split-Path $dstFile -Parent

    if (-not (Test-Path $dstPath)) {
        New-Item -Path $dstPath -ItemType Directory -Force | Out-Null
    }

    $fileName = Split-Path $relPath -Leaf

    if (Test-Path $dstFile) {
        Write-Host "  ⏭️  跳过（已存在）: $fileName → $target" -ForegroundColor DarkYellow
        $totalSkipped++
        $log += "⏭️  [跳过] $relPath → $target (已存在)"
        continue
    }

    try {
        Move-Item $srcFile $dstFile -Force
        Write-Host "  📦  移动: $fileName → $target" -ForegroundColor Green
        $totalMoved++
        $log += "📦  [移动] $relPath → $target"
    } catch {
        Write-Host "  ❌  失败: $fileName — $($_.Exception.Message)" -ForegroundColor Red
        $totalError++
        $log += "❌  [失败] $relPath — $($_.Exception.Message)"
    }
}

# === 阶段 3：删除 99-归档库/_09项目资料_杂项 下不再需要的子目录 ===
Write-Host ""
Write-Host "===== 阶段 3：清理空目录 =====" -ForegroundColor Cyan

$subDirsToCheck = @("01-合同招投标", "02-工程量与计价", "03-图纸资料", "06-物资采购", "07-往来文件", "08-结算归档", "09-人员与行政", "其他零散文件")
foreach ($sub in $subDirsToCheck) {
    $subPath = Join-Path $srcBase $sub
    if (Test-Path $subPath) {
        $files = Get-ChildItem $subPath -Recurse -File -ErrorAction SilentlyContinue
        if ($files.Count -eq 0) {
            Remove-Item $subPath -Recurse -Force
            Write-Host "  🗑️  删除空目录: $sub" -ForegroundColor Red
        } else {
            Write-Host "  ⏭️  保留（还有 $($files.Count) 文件）: $sub" -ForegroundColor DarkYellow
        }
    }
}

# === 阶段 4：自检 + 报告 ===
Write-Host ""
Write-Host "===== 阶段 4：自检 =====" -ForegroundColor Cyan

$srcFinal = Get-ChildItem $srcBase -Recurse -File -ErrorAction SilentlyContinue
$srcFinalCount = $srcFinal.Count
$srcFinalSize = ($srcFinal | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "99-归档库/_09项目资料_杂项 剩余: $srcFinalCount 个文件 / $([math]::Round($srcFinalSize, 1)) MB"

if ($srcFinalCount -gt 0) {
    Write-Host ""
    Write-Host "剩余文件清单（应只剩 考试/不可迁移 文件）："
    $srcFinal | ForEach-Object { Write-Host "  $($_.FullName.Replace($srcBase, '...'))" }
}

$dstFinal = Get-ChildItem $dstBase -Recurse -File -ErrorAction SilentlyContinue
$dstFinalCount = $dstFinal.Count
$dstFinalSize = ($dstFinal | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host ""
Write-Host "D:\高治国资料\知识库原始资料 12-已结项目资料: $dstFinalCount 个文件 / $([math]::Round($dstFinalSize, 1)) MB"

# === 总结 ===
Write-Host ""
Write-Host "===== 补漏迁移总结 =====" -ForegroundColor Cyan
Write-Host "📦 新移动: $totalMoved 个文件" -ForegroundColor Green
Write-Host "⏭️  跳过: $totalSkipped 个文件" -ForegroundColor Yellow
Write-Host "❌ 错误: $totalError 个文件" -ForegroundColor Red
Write-Host "🔒 不迁文件: $($不迁存在.Count) 个（保留在 99-归档库）" -ForegroundColor Magenta
Write-Host ""

# 保存日志
$logFile = "D:\高治国资料\知识库原始资料\__N2_补漏日志_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$log | Out-File -FilePath $logFile -Encoding UTF8
Write-Host "📄 日志已保存：$logFile" -ForegroundColor Cyan
