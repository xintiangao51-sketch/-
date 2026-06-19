#!/usr/bin/env python3
"""
新疆造价信息自动采集系统
每日采集全疆定额、人工单价、材料信息价
"""

import os
import sys
import yaml
import logging
import sqlite3
from datetime import datetime, date
from pathlib import Path

# 确保项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler.zjt import ZJTCrawler
from crawler.wlmq_zjj import WLMQCrawler
from crawler.jtyst import JTYSTCrawler
from crawler.bingtuan import BingtuanCrawler
from storage.db import Database
from notify.change_alert import ChangeAlert


def load_config(config_path="config.yaml"):
    """加载配置"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(config):
    """配置日志"""
    log_dir = Path(config["download"]["base_dir"]) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().strftime("%Y%m%d")
    log_file = log_dir / f"crawl_{today}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("main")


def ensure_dirs(config):
    """确保目录结构"""
    base = Path(config["download"]["base_dir"])
    dirs = [
        base / "db",
        base / "downloads" / "quota",
        base / "downloads" / "labor",
        base / "downloads" / "material",
        base / "downloads" / "policy",
        base / "reports" / "daily",
        base / "reports" / "change",
        base / "logs",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def run_daily_crawl(config, logger):
    """执行每日采集"""
    db = Database(config["database"]["path"])
    db.init_tables()

    alert = ChangeAlert(config, db)
    crawlers = []
    total_found = 0
    total_saved = 0
    errors = []

    # 按优先级加载启用的爬虫
    source_map = {
        "自治区住建厅": ZJTCrawler,
        "乌鲁木齐住建局": WLMQCrawler,
        "自治区交通运输厅": JTYSTCrawler,
        "新疆生产建设兵团": BingtuanCrawler,
    }

    for source_conf in config["sources"]:
        if not source_conf.get("enabled", True):
            continue
        name = source_conf["name"]
        if name in source_map:
            crawlers.append((source_conf["priority"], source_map[name](config, db, source_conf)))

    # 按优先级排序
    crawlers.sort(key=lambda x: x[0])

    for priority, crawler in crawlers:
        try:
            logger.info(f"开始采集: {crawler.name}")
            found, saved = crawler.run()
            total_found += found
            total_saved += saved
            logger.info(f"完成采集: {crawler.name} | 发现{found}条 | 保存{saved}条")
        except Exception as e:
            error_msg = f"{crawler.name} 采集失败: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            db.log_crawl(crawler.name, "daily", "fail", 0, 0, str(e))

    # 生成每日报告
    report = generate_daily_report(config, total_found, total_saved, errors)
    logger.info(f"每日采集完成 | 发现{total_found}条 | 保存{total_saved}条 | 错误{len(errors)}个")

    # 变更告警
    alert.check_and_notify()

    db.close()
    return report


def generate_daily_report(config, found, saved, errors):
    """生成每日报告"""
    today = date.today().strftime("%Y-%m-%d")
    report_dir = Path(config["download"]["base_dir"]) / "reports" / "daily"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"report_{date.today().strftime('%Y%m%d')}.md"

    status = "✅ 正常" if not errors else "⚠️ 有异常"

    content = f"""# 新疆造价信息采集日报 — {today}

**状态**: {status}

## 采集概况

| 指标 | 数量 |
|------|------|
| 发现条目 | {found} |
| 新增保存 | {saved} |
| 采集错误 | {len(errors)} |

"""

    if errors:
        content += "## 错误详情\n\n"
        for err in errors:
            content += f"- {err}\n"
        content += "\n"

    content += f"""## 数据库统计

（详见数据库查询）

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content


if __name__ == "__main__":
    config = load_config()
    logger = setup_logging(config)
    ensure_dirs(config)
    logger.info("="*50)
    logger.info("新疆造价信息自动采集系统启动")
    report = run_daily_crawl(config, logger)
    logger.info("采集系统运行结束")
