@echo off
chcp 65001 >nul
echo ========================================
echo 通衢隧道Excel数据提取工具
echo ========================================
echo.
echo 正在安装openpyxl...
pip install openpyxl
if %ERRORLEVEL% NEQ 0 (
    echo pip安装失败，尝试使用pip3...
    pip3 install openpyxl
)
echo.
echo ========================================
echo 正在读取所有Excel文件...
echo ========================================
echo.
python "%~dp0read_excel_files.py"
echo.
echo ========================================
if exist "%~dp0excel_data.json" (
    echo 完成! 数据已保存到: %~dp0excel_data.json
    echo 文件大小:
    for %%I in ("%~dp0excel_data.json") do echo %%~zI 字节
) else (
    echo 文件未生成，请检查上方错误信息
)
echo ========================================
pause
