"""变更告警模块 — 检测价格/定额变化并生成告警"""

import json
from datetime import datetime, date
from pathlib import Path


class ChangeAlert:
    """造价信息变更告警"""

    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.report_dir = Path(config["download"]["base_dir"]) / "reports" / "change"

    def check_and_notify(self):
        """检查变更并生成告警报告"""
        changes = self.db.get_recent_changes(days=1)
        if not changes:
            return

        today = date.today().strftime("%Y%m%d")
        report_path = self.report_dir / f"change_{today}.md"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        content = f"""# 造价信息变更告警 — {date.today().strftime('%Y-%m-%d')}

⚠️ 以下信息发生变更，请及时关注：

| 序号 | 数据表 | 字段 | 旧值 | 新值 | 变更时间 |
|------|--------|------|------|------|----------|
"""

        for i, change in enumerate(changes, 1):
            content += f"| {i} | {change['table_name']} | {change['field_name']} | {change['old_value']} | {change['new_value']} | {change['change_time']} |\n"

        content += f"""
---
*告警生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*请核实变更内容，必要时更新预算文件*
"""

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return content
