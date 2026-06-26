# N2_v2_强制迁移.ps1
# 简化版：用 cmd.exe move 强制迁移（避免 PowerShell 字符串处理 Bug）
# 策略：直接对每个文件名做 Move-Item -Force，不存在 → 报错（不是跳过）

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$srcBase = "D:\知识库\99-归档库\_09项目资料_杂项\其他零散文件"
$dstBase = "D:\高治国资料\知识库原始资料\12-已结项目资料"

# 补漏映射（基于实际剩余 40 文件精确名）
$迁 = @(
    # 01-合同招投标
    @{ src = "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段 加筋陡坡明墩工程02标（项目名称）加筋陡坡明墩工程02标（包件名称）公路工程（专业类别名称）劳务分包招标.zip"; dst = "G0711乌尉" }
    @{ src = "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段 桩基工程（项目名称）桩基工程（包件名称）公路工程（专业类别名称）劳务分包招标(1).zip"; dst = "G0711乌尉" }
    @{ src = "01-合同招投标\中交第一航务工程局有限公司新疆乌尉公路包PPP项目WYTJ-01标段（项目名称）明墩工程01标（包件名称）公路工程（专业类别名称）劳务分包招标.zip"; dst = "G0711乌尉" }
    @{ src = "01-合同招投标\借款协议.docx"; dst = "金国机械租赁部" }
    @{ src = "01-合同招投标\建筑工程劳务分包合同(1).pdf"; dst = "霍尔果斯檀悦府" }

    # 02-工程量与计价
    @{ src = "02-工程量与计价\3.29发  风机基础及道路标段建议价格.xlsx"; dst = "木垒风电" }
    @{ src = "02-工程量与计价\乌鲁木齐市土方工程预算书编制说明 一.docx"; dst = "将军庙水库" }
    @{ src = "02-工程量与计价\体育学院室外清单(1).docx"; dst = "喀什体校" }
    @{ src = "02-工程量与计价\场外护坡及防洪工程清单综合报价2025.6.27.pdf"; dst = "前进水源护坡" }
    @{ src = "02-工程量与计价\工程量预算书 一.docx"; dst = "红雁池" }
    @{ src = "02-工程量与计价\新疆交通建设集团股份有限公司新疆新和至拜城铁路项目总承包EPC（一标段）桥涵及路堤防护工程劳务服务2025.5.18.xlsx"; dst = "G0711乌尉" }
    @{ src = "02-工程量与计价\新疆交通建设集团股份有限公司新疆新和至拜城铁路项目总承包EPC（一标段）桥涵及路堤防护工程劳务服务采购项目固化清单(1).xlsx"; dst = "G0711乌尉" }
    @{ src = "02-工程量与计价\羊圈工程量清单及报价.xlsx"; dst = "红墩二道渠" }
    @{ src = "02-工程量与计价\表1_分部分项工程量清单与计价表.xlsx"; dst = "将军庙水库" }
    @{ src = "02-工程量与计价\表2_综合单价分析表.xlsx"; dst = "将军庙水库" }
    @{ src = "02-工程量与计价\表3_措施项目清单与计价表.xlsx"; dst = "将军庙水库" }
    @{ src = "02-工程量与计价\表4_其他项目清单与计价表.xlsx"; dst = "将军庙水库" }
    @{ src = "02-工程量与计价\表5_人材机汇总表.xlsx"; dst = "将军庙水库" }

    # 03-图纸资料
    @{ src = "03-图纸资料\3#大棚结构施工图0122.dwg"; dst = "其他" }
    @{ src = "03-图纸资料\G219线昭苏-温宿ZW-3标拱形骨架护坡.pdf"; dst = "G0711乌尉" }
    @{ src = "03-图纸资料\G219线昭苏-温宿ZW-3标方格网.pdf"; dst = "G0711乌尉" }
    @{ src = "03-图纸资料\G219线昭苏-温宿ZW-3标第三篇 路基、路面（路基防护、挡墙、排水工程）.pdf"; dst = "G0711乌尉" }
    @{ src = "03-图纸资料\G219线昭苏-温宿ZW-3标被动防护网.pdf"; dst = "G0711乌尉" }
    @{ src = "03-图纸资料\商务标-青岛德泰36350482.09(1).PDF"; dst = "其他" }
    @{ src = "03-图纸资料\景航酒店(1).pdf"; dst = "其他" }
    @{ src = "03-图纸资料\缴费凭证_BILL-20260120-018533.pdf"; dst = "其他" }
    @{ src = "03-图纸资料\羊圈_t3.dwg"; dst = "红墩二道渠" }
    @{ src = "03-图纸资料\羊圈_t3.pdf"; dst = "红墩二道渠" }
    @{ src = "03-图纸资料\融信-签收凭证-陕西三耕建设工程有限公司-SYJSGS-20251230-005-000019.pdf"; dst = "其他" }
    @{ src = "03-图纸资料\融资凭证_融信_SYJSGS-20251230-005-000019.pdf"; dst = "其他" }
    @{ src = "03-图纸资料\（4月3日）4、5号给水泵变频改造（建筑、结构、电气）.pdf"; dst = "其他" }

    # 06-物资采购
    @{ src = "06-物资采购\G219线昭苏-温宿ZW-3标混凝土护坡工程.pdf"; dst = "G0711乌尉" }

    # 07-往来文件
    @{ src = "07-往来文件\博州博乐市前进水源项目护坡工程技术方案.docx"; dst = "博乐前进水源项目" }
    @{ src = "07-往来文件\现浇楼板支撑架施工方案.docx"; dst = "其他" }

    # 08-结算归档
    @{ src = "08-结算归档\投资人+施工总承包模式定义.docx"; dst = "鼎梁柱公司" }
    @{ src = "08-结算归档\新疆伊犁酒店外墙粉刷施工单价分析及利润率计算.docx"; dst = "天山乡综合能源站" }
    @{ src = "08-结算归档\红雁池工程内容说明.docx"; dst = "红雁池" }

    # 09-人员与行政
    @{ src = "09-人员与行政\不拖欠农民工工资承诺函2026年6月2日.pdf"; dst = "鼎梁柱公司" }
    @{ src = "09-人员与行政\代发工资委托书2026年4月份农民工（砌筑班组）工资2026年6月2日.docx"; dst = "鼎梁柱公司" }
    @{ src = "09-人员与行政\微信图片_20250523125523.png"; dst = "其他" }
)

# 不迁文件（保留 99-归档库）
$不迁 = @(
    @{ src = "03-图纸资料\2025年监理工程师职业资格考试.pdf"; reason = "个人考试资料（高治国本人）" }
    @{ src = "03-图纸资料\2025年监理工程师职业资格考试承诺书.pdf"; reason = "个人考试资料（高治国本人）" }
    @{ src = "03-图纸资料\四川中恒铭泰公司信息.pdf"; reason = "企业查询（一次性）" }
)

Write-Host "===== 阶段 1：清理目标位置已存在文件 =====" -ForegroundColor Cyan

# 强制清理目标位置可能存在的错误副本
$targetDirs = $迁 | ForEach-Object { $_.dst } | Sort-Object -Unique
foreach ($td in $targetDirs) {
    $tdPath = Join-Path $dstBase $td
    if (Test-Path $tdPath) {
        # 列出当前文件
        $files = Get-ChildItem $tdPath -File -ErrorAction SilentlyContinue
        Write-Host "  📂 $td 现有 $($files.Count) 个文件"
    } else {
        New-Item -Path $tdPath -ItemType Directory -Force | Out-Null
        Write-Host "  + 创建 $td"
    }
}

Write-Host ""
Write-Host "===== 阶段 2：执行迁移（Force 模式）=====" -ForegroundColor Cyan
Write-Host ""

$totalSuccess = 0
$totalFail = 0
$log = @()

foreach ($entry in $迁) {
    $relPath = $entry.src
    $target = $entry.dst

    $srcFile = Join-Path $srcBase $relPath
    $dstFile = Join-Path $dstBase $target
    $fileName = Split-Path $relPath -Leaf

    # 检查源是否存在
    if (-not (Test-Path $srcFile)) {
        Write-Host "  ⚠️  源不存在: $relPath" -ForegroundColor DarkYellow
        $log += "⚠️  [源不存在] $relPath"
        continue
    }

    # 准备目标目录
    $dstDir = Split-Path $dstFile -Parent
    if (-not (Test-Path $dstDir)) {
        New-Item -Path $dstDir -ItemType Directory -Force | Out-Null
    }

    # 删除目标位置已存在文件（避免 PS 误判）
    if (Test-Path $dstFile) {
        Remove-Item $dstFile -Force
    }

    # 执行移动
    try {
        Move-Item $srcFile $dstFile -Force
        $size = (Get-Item $dstFile).Length
        $sizeKB = [math]::Round($size / 1KB, 1)
        Write-Host "  📦  移动: $fileName → $target ($sizeKB KB)" -ForegroundColor Green
        $totalSuccess++
        $log += "📦  [移动] $relPath → $target ($sizeKB KB)"
    } catch {
        Write-Host "  ❌  失败: $fileName — $($_.Exception.Message)" -ForegroundColor Red
        $totalFail++
        $log += "❌  [失败] $relPath — $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "===== 阶段 3：清理空目录 =====" -ForegroundColor Cyan

$subDirsToCheck = @("01-合同招投标", "02-工程量与计价", "03-图纸资料", "06-物资采购", "07-往来文件", "08-结算归档", "09-人员与行政")
foreach ($sub in $subDirsToCheck) {
    $subPath = Join-Path $srcBase $sub
    if (Test-Path $subPath) {
        $files = @(Get-ChildItem $subPath -File -ErrorAction SilentlyContinue)
        if ($files.Count -eq 0) {
            Remove-Item $subPath -Recurse -Force
            Write-Host "  🗑️  删除空目录: $sub" -ForegroundColor Red
        } else {
            Write-Host "  ⏭️  保留 (还有 $($files.Count) 文件): $sub" -ForegroundColor DarkYellow
        }
    }
}

Write-Host ""
Write-Host "===== 阶段 4：自检 =====" -ForegroundColor Cyan

$srcFinal = @(Get-ChildItem $srcBase -Recurse -File -ErrorAction SilentlyContinue)
$srcFinalCount = $srcFinal.Count
$srcFinalSize = ($srcFinal | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "99-归档库/_09项目资料_杂项 剩余: $srcFinalCount 个文件 / $([math]::Round($srcFinalSize, 1)) MB"

# 列出剩余文件
$srcFinal | ForEach-Object {
    $rel = $_.FullName.Replace($srcBase, "")
    Write-Host "  $rel"
}

$dstFinal = @(Get-ChildItem $dstBase -Recurse -File -ErrorAction SilentlyContinue)
$dstFinalCount = $dstFinal.Count
$dstFinalSize = ($dstFinal | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host ""
Write-Host "D:\高治国资料\知识库原始资料\12-已结项目资料: $dstFinalCount 个文件 / $([math]::Round($dstFinalSize, 1)) MB"

Write-Host ""
Write-Host "===== 总结 =====" -ForegroundColor Cyan
Write-Host "✅ 成功移动: $totalSuccess 个文件" -ForegroundColor Green
Write-Host "❌ 失败: $totalFail 个文件" -ForegroundColor Red
Write-Host "🔒 不迁（保留 99-归档库）: 3 个文件" -ForegroundColor Magenta
Write-Host ""

# 保存日志
$logFile = "D:\高治国资料\知识库原始资料\__N2_v2_强制迁移日志_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$log | Out-File -FilePath $logFile -Encoding UTF8
Write-Host "📄 日志已保存：$logFile" -ForegroundColor Cyan
