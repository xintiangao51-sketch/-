# 原料frontmatter标记脚本
# 为迁移后的原料文件添加6态追踪标记

$sourceRoot = \"D:\高治国资料\知识库原始资料\"
$logFile = \"D:\高治国资料\知识库原始资料\frontmatter_log.txt\"

function Add-Frontmatter {
    param([string]$filePath, [string]$status)
    
    $extension = [System.IO.Path]::GetExtension($filePath)
    if ($extension -notin @('.md', '.markdown')) {
        return $false
    }
    
    try {
        $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return $false }
        
        # 检查是否已有frontmatter
        if ($content -match '^---') {
            # 已有frontmatter，检查是否有所需字段
            if ($content -match '处理状态:' -and $content -match '处理日期:') {
                return $false  # 已有标记，跳过
            }
            
            # 在已有frontmatter中添加字段
            $lines = $content -split \"
\"
            $newLines = @()
            $added = $false
            
            foreach ($line in $lines) {
                $newLines += $line
                if ($line -match '^---' -and -not $added) {
                    $newLines += \"处理状态: $status\"
                    $newLines += \"处理日期: 2026-06-26\"
                    $added = $true
                }
            }
            
            Set-Content -Path $filePath -Value ($newLines -join \"
\") -Encoding UTF8
            return $true
        }
        else {
            # 添加新frontmatter
            $frontmatter = @\"
---
处理状态: $status
处理日期: 2026-06-26
---

$content
\"@
            Set-Content -Path $filePath -Value $frontmatter -Encoding UTF8
            return $true
        }
    }
    catch {
        return $false
    }
}

# 主流程
Add-Content -Path $logFile -Value \"=== frontmatter标记开始: 06/26/2026 15:35:51 ===\"

# 处理00-项目资料
$dir00 = Join-Path $sourceRoot \"00-项目资料\"
if (Test-Path $dir00) {
    $mdFiles = Get-ChildItem -Path $dir00 -Recurse -Include *.md -File
    $count = 0
    foreach ($file in $mdFiles) {
        if (Add-Frontmatter $file.FullName \"待提炼\") {
            $count++
        }
    }
    Add-Content -Path $logFile -Value \"00-项目资料: 标记 $count 个文件\"
    Write-Host \"✅ 00-项目资料: 标记 $count 个文件\"
}

# 处理13-工程图纸
$dir13 = Join-Path $sourceRoot \"13-工程图纸\"
if (Test-Path $dir13) {
    $mdFiles = Get-ChildItem -Path $dir13 -Recurse -Include *.md -File
    $count = 0
    foreach ($file in $mdFiles) {
        if (Add-Frontmatter $file.FullName \"待提炼\") {
            $count++
        }
    }
    Add-Content -Path $logFile -Value \"13-工程图纸: 标记 $count 个文件\"
    Write-Host \"✅ 13-工程图纸: 标记 $count 个文件\"
}

Add-Content -Path $logFile -Value \"=== frontmatter标记完成 ===\"
Write-Host \"🎯 frontmatter标记完成\"
