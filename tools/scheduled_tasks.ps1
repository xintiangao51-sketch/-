# 知识库自动化 — Windows 定时任务注册命令
# 在管理员 PowerShell 中逐条执行

# 1. 每月1日 09:07 — 信息价月度采集
schtasks /create /tn "知识库-信息价月度采集" /tr "python D:/知识库/tools/crawl_xj_info_price.py" /sc monthly /d 1 /st 09:07 /f

# 2. 每周一 09:07 — 材料价格周更
schtasks /create /tn "知识库-材料价格周更" /tr "python D:/知识库/tools/material_price_updater.py" /sc weekly /d MON /st 09:07 /f

# 3. 每周三 09:07 — 知识采集 + KC 生成
schtasks /create /tn "知识库-知识采集KC生成" /tr "python D:/知识库/tools/crawl_policy.py" /sc weekly /d WED /st 09:07 /f

# 4. 每周五 09:07 — 知识库健康度检查
schtasks /create /tn "知识库-健康度检查" /tr "python D:/知识库/tools/obsidian_optimizer.py" /sc weekly /d FRI /st 09:07 /f

# 查看已注册任务
# schtasks /query /tn "知识库-"

# 删除任务
# schtasks /delete /tn "知识库-信息价月度采集" /f
