import os
import re
from openpyxl import Workbook

# 根目录
root_dir = r"D:高治国资料高治国2025年重要资料鼎梁柱"
exclude_dirs = ["$RECYCLE.BIN", "System Volume Information"]

# 创建工作簿
wb = Workbook()
ws = wb.active
ws.title = "文件目录"
# 表头
headers = ["序号", "一级分类", "二级分类", "文件名", "文件类型", "提取金额(元)", "所属项目", "文件路径"]
ws.append(headers)

# 金额正则
amount_pattern = re.compile(r'(\d+(\.\d{1,2})?)元')
# 项目关键词
project_keywords = {
    "昌南X125": ["昌南", "X125"],
    "若羌米兰": ["若羌", "米兰"],
    "G331交安": ["G331", "交安"],
    "和田项目": ["和田", "旋挖钻"],
    "中核西北项目": ["中核西北"],
    "通用": []
}

count = 1
for root, dirs, files in os.walk(root_dir):
    # 排除不需要的目录
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    # 计算相对路径
    rel_path = os.path.relpath(root, root_dir)
    # 拆分分类
    if rel_path == ".":
        continue
    parts = rel_path.split(os.sep)
    cate1 = parts[0] if len(parts) >=1 else ""
    cate2 = parts[1] if len(parts) >=2 else ""
    
    for file in files:
        if file == "generate_catalog.py" or file == "鼎梁柱文件目录.xlsx":
            continue
        # 文件类型
        file_type = os.path.splitext(file)[1].upper().strip(".")
        # 提取金额
        amount_match = amount_pattern.search(file)
        amount = amount_match.group(1) if amount_match else ""
        # 匹配项目
        project = "通用"
        for proj, keywords in project_keywords.items():
            for kw in keywords:
                if kw in file:
                    project = proj
                    break
            if project != "通用":
                break
        # 完整路径
        full_path = os.path.join(root, file)
        # 写入行
        ws.append([count, cate1, cate2, file, file_type, amount, project, full_path])
        count +=1

# 调整列宽
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter
    for cell in col:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = (max_length + 2) * 1.2
    ws.column_dimensions[column].width = adjusted_width

# 保存
wb.save("鼎梁柱文件目录.xlsx")
print(f"目录生成完成，共统计{count-1}个文件，已保存为鼎梁柱文件目录.xlsx")
