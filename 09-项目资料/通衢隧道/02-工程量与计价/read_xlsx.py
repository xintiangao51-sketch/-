import pandas as pd
import tabulate
file_path = r'C:\Users\高\Desktop\通衢隧道洞口坡面治理工程\通衢隧道_劳务清包工报价单_不含主材_20260529.xlsx'
output_path = r'C:\Users\高\Desktop\报价单内容.md'
all_sheets = pd.read_excel(file_path, sheet_name=None)
with open(output_path, 'w', encoding='utf-8-sig') as f:
    for sheet_name, df in all_sheets.items():
        f.write(f"## 工作表：{sheet_name}\n\n")
        f.write(df.fillna('-').to_markdown(index=False))
        f.write("\n\n---\n\n")
print(f"内容已导出到：{output_path}")
