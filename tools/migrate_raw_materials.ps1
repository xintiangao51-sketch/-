# 原料生命周期迁移脚本
# 作者: AI Assistant
# 日期: 2026-06-26
# 功能: 将主知识库中的大型原始资料迁移到D盘原始资料库

$sourceRoot = \"D:\知识库\"
$destRoot = \"D:\高治国资料\知识库原始资料\"
$logFile = \"D:\高治国资料\知识库原始资料\迁移日志_项目资料_20260626.txt\"
$skipExtensions = @(\".md\", \".markdown\", \".txt\")  # 跳过markdown等小文件
$maxSizeMB = 10  # 大于10MB的文件优先迁移

function Add-Log {
    param([string]$message)
    $timestamp = Get-Date -Format \"yyyy-MM-dd HH:mm:ss\"
    Add-Content -Path $logFile -Value \"[$timestamp] $message\"
    Write-Host \"📝 $message\"
}

function Test-ShouldMigrate {
    param([string]$filePath)
    
    # 检查文件扩展名
    $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
    if ($skipExtensions -contains $extension) {
        return $false
    }
    
    # 检查文件大小
    try {
        $fileInfo = Get-Item $filePath
        $sizeMB = $fileInfo.Length / 1MB
        if ($sizeMB -ge $maxSizeMB) {
            Add-Log \"大文件检测: $(Split-Path $filePath -Leaf) ($sizeMB.ToString('F2'))MB\"
            return $true
        }
        
        # 检查文件类型
        $largeTypes = @(\".pdf\", \".dwg\", \".dxf\", \".xlsx\", \".xls\", \".doc\", \".docx\", \".zip\", \".rar\", \".7z\")
        if ($largeTypes -contains $extension) {
            return $true
        }
        
        return $false
    }
    catch {
        return $false
    }
}

function Migrate-Directory {
    param([string]$sourceDir, [string]$destDir, [string]$relativePath)
    
    Add-Log \"开始迁移目录: $relativePath\"
    
    if (-not (Test-Path $destDir)) {
        New-Item -Path $destDir -ItemType Directory | Out-Null
        Add-Log \"创建目标目录: $destDir\"
    }
    
    $items = Get-ChildItem -Path $sourceDir -File
    $migratedCount = 0
    $skippedCount = 0
    
    foreach ($item in $items) {
        if (Test-ShouldMigrate $item.FullName) {
            $destPath = Join-Path $destDir $item.Name
            try {
                # 检查目标文件是否已存在
                if (Test-Path $destPath) {
                    Add-Log \"文件已存在，跳过: $(Split-Path $item.FullName -Leaf)\"
                    $skippedCount++
                    continue
                }
                
                Copy-Item -Path $item.FullName -Destination $destPath -Force
                $migratedCount++
                Add-Log \"✅ 迁移: $(Split-Path $item.FullName -Leaf)\"
            }
            catch {
                Add-Log \"❌ 迁移失败: $(Split-Path $item.FullName -Leaf) - $($_.Exception.Message)\"
            }
        }
        else {
            $skippedCount++
        }
    }
    
    Add-Log \"目录迁移完成: $relativePath | 迁移: $migratedCount | 跳过: $skippedCount\"
    return $migratedCount, $skippedCount
}

function Create-RedirectFile {
    param([string]$sourcePath, [string]$destPath)
    
    $redirectContent = @\"
# 原始资料迁移跳转页面

> 本目录的原始资料已迁移至D盘独立存储，以提升知识库性能。

## 迁移信息
- **迁移时间**: 
- **原路径**: $sourcePath
- **新路径**: $destPath
- **访问方式**: 直接访问新路径或使用原始资料库

## 目录结构
\"\@
    
    $subDirs = Get-ChildItem -Path $destPath -Directory | Select-Object -First 10
    foreach ($dir in $subDirs) {
        $redirectContent += \"- \\"$($dir.Name)/\\" - 项目资料\
\"
    }
    
    $redirectContent += @\"

## 注意事项
- 本页面仅作为跳转指引，不再包含实际文件
- 原始资料保持原样存档，便于法规/合同溯源
- 如需查阅原始资料，请直接访问D盘对应路径

---
*迁移完成时间: 06/26/2026 14:57:41*
\"\@
    
    Set-Content -Path $sourcePath -Value $redirectContent -Encoding UTF8
    Add-Log \"🔗 创建跳转页面: $(Split-Path $sourcePath -Leaf)\"
}

# 主迁移流程
try {
    Add-Log \"=== 原料资料迁移开始 ===\"
    
    # 迁移 09-项目资料
    $source09 = Join-Path $sourceRoot \"09-项目资料\"
    $dest00 = Join-Path $destRoot \"00-项目资料\"
    
    if (Test-Path $source09) {
        Add-Log \"开始迁移 09-项目资料 到 00-项目资料\"
        $totalMigrated, $totalSkipped = Migrate-Directory $source09 $dest00 \"09-项目资料\"
        
        # 创建跳转文件
        Create-RedirectFile $source09 $dest00
        Add-Log \"09-项目资料迁移完成 | 迁移: $totalMigrated | 跳过: $totalSkipped\"
    }
    else {
        Add-Log \"❌ 源目录不存在: 09-项目资料\"
    }
    
    # 迁移 13-工程图纸
    $source13 = Join-Path $sourceRoot \"13-工程图纸\"
    $dest13 = Join-Path $destRoot \"13-工程图纸\"
    
    if (Test-Path $source13) {
        Add-Log \"开始迁移 13-工程图纸\"
        $totalMigrated, $totalSkipped = Migrate-Directory $source13 $dest13 \"13-工程图纸\"
        
        # 创建跳转文件
        Create-RedirectFile $source13 $dest13
        Add-Log \"13-工程图纸迁移完成 | 迁移: $totalMigrated | 跳过: $totalSkipped\"
    }
    else {
        Add-Log \"❌ 源目录不存在: 13-工程图纸\"
    }
    
    Add-Log \"=== 迁移完成 ===\"
}
catch {
    Add-Log \"❌ 迁移过程中出现错误: $($_.Exception.Message)\"
}

Write-Host \"🎯 迁移脚本执行完成，请查看日志: $logFile\"
