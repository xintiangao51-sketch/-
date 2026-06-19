"""数据库操作模块"""

import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    """SQLite数据库管理"""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS labor_rate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        category TEXT NOT NULL,
        project_type TEXT,
        price REAL NOT NULL,
        effective_date TEXT,
        quarter TEXT NOT NULL,
        source_url TEXT,
        source_file TEXT,
        crawl_time TEXT NOT NULL,
        UNIQUE(region, category, quarter)
    );

    CREATE TABLE IF NOT EXISTS material_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        material_name TEXT NOT NULL,
        spec TEXT,
        unit TEXT,
        price REAL NOT NULL,
        price_with_tax REAL,
        month TEXT NOT NULL,
        source_url TEXT,
        source_file TEXT,
        crawl_time TEXT NOT NULL,
        UNIQUE(region, material_name, spec, month)
    );

    CREATE TABLE IF NOT EXISTS quota_doc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        quota_system TEXT,
        publish_date TEXT,
        effective_date TEXT,
        file_url TEXT,
        local_path TEXT,
        crawl_time TEXT NOT NULL,
        UNIQUE(title, doc_type)
    );

    CREATE TABLE IF NOT EXISTS crawl_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL,
        items_found INTEGER DEFAULT 0,
        items_saved INTEGER DEFAULT 0,
        error_msg TEXT,
        crawl_time TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS change_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        record_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        change_time TEXT NOT NULL
    );
    """

    def __init__(self, db_path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def init_tables(self):
        """初始化数据表"""
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()

    def save_labor_rate(self, region, category, price, effective_date="", quarter="",
                        project_type=None, source_url="", source_file=""):
        """保存人工单价，有变化则记录变更"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # 检查是否已存在
            existing = self.conn.execute(
                "SELECT price FROM labor_rate WHERE region=? AND category=? AND quarter=?",
                (region, category, quarter)
            ).fetchone()

            if existing:
                if abs(existing["price"] - price) > 0.01:
                    # 价格变化，记录变更
                    self.conn.execute(
                        "INSERT INTO change_log (table_name, record_id, field_name, old_value, new_value, change_time) "
                        "VALUES ('labor_rate', "
                        "(SELECT id FROM labor_rate WHERE region=? AND category=? AND quarter=?), "
                        "'price', ?, ?, ?)",
                        (region, category, quarter, str(existing["price"]), str(price), now)
                    )
                    # 更新
                    self.conn.execute(
                        "UPDATE labor_rate SET price=?, effective_date=?, source_url=?, source_file=?, crawl_time=? "
                        "WHERE region=? AND category=? AND quarter=?",
                        (price, effective_date, source_url, source_file, now, region, category, quarter)
                    )
                # 价格未变化
                self.conn.commit()
                return 0
            else:
                # 新增
                self.conn.execute(
                    "INSERT INTO labor_rate (region, category, project_type, price, effective_date, quarter, source_url, source_file, crawl_time) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (region, category, project_type, price, effective_date, quarter,
                     source_url, source_file, now)
                )
                self.conn.commit()
                return 1

        except sqlite3.IntegrityError:
            self.conn.rollback()
            return 0

    def save_material_price(self, region, material_name, spec, unit, price,
                            price_with_tax, month, source_url="", source_file=""):
        """保存材料价格"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            existing = self.conn.execute(
                "SELECT price FROM material_price WHERE region=? AND material_name=? AND spec=? AND month=?",
                (region, material_name, spec or "", month)
            ).fetchone()

            if existing:
                if abs(existing["price"] - price) > 0.01:
                    self.conn.execute(
                        "INSERT INTO change_log (table_name, record_id, field_name, old_value, new_value, change_time) "
                        "VALUES ('material_price', "
                        "(SELECT id FROM material_price WHERE region=? AND material_name=? AND spec=? AND month=?), "
                        "'price', ?, ?, ?)",
                        (region, material_name, spec or "", month,
                         str(existing["price"]), str(price), now)
                    )
                    self.conn.execute(
                        "UPDATE material_price SET price=?, price_with_tax=?, source_url=?, source_file=?, crawl_time=? "
                        "WHERE region=? AND material_name=? AND spec=? AND month=?",
                        (price, price_with_tax, source_url, source_file, now,
                         region, material_name, spec or "", month)
                    )
                self.conn.commit()
                return 0
            else:
                self.conn.execute(
                    "INSERT INTO material_price (region, material_name, spec, unit, price, price_with_tax, month, source_url, source_file, crawl_time) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (region, material_name, spec, unit, price, price_with_tax, month,
                     source_url, source_file, now)
                )
                self.conn.commit()
                return 1

        except sqlite3.IntegrityError:
            self.conn.rollback()
            return 0

    def save_quota_doc(self, title, doc_type, quota_system="", publish_date="",
                       effective_date="", file_url="", local_path=""):
        """保存定额文档记录"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            existing = self.conn.execute(
                "SELECT id FROM quota_doc WHERE title=? AND doc_type=?",
                (title, doc_type)
            ).fetchone()

            if existing:
                return 0

            self.conn.execute(
                "INSERT INTO quota_doc (title, doc_type, quota_system, publish_date, effective_date, file_url, local_path, crawl_time) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, doc_type, quota_system, publish_date, effective_date,
                 file_url, local_path, now)
            )
            self.conn.commit()
            return 1

        except sqlite3.IntegrityError:
            self.conn.rollback()
            return 0

    def log_crawl(self, source, task_type, status, found, saved, error_msg=""):
        """记录采集日志"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO crawl_log (source, task_type, status, items_found, items_saved, error_msg, crawl_time) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source, task_type, status, found, saved, error_msg, now)
        )
        self.conn.commit()

    def get_recent_changes(self, days=7):
        """获取最近N天的变更"""
        cutoff = f"datetime('now', '-{days} days')"
        return self.conn.execute(
            "SELECT * FROM change_log WHERE change_time >= datetime('now', ?) ORDER BY change_time DESC",
            (f"-{days} days",)
        ).fetchall()

    def get_latest_labor_rates(self, region=None):
        """获取最新人工单价"""
        if region:
            return self.conn.execute(
                "SELECT * FROM labor_rate WHERE region=? ORDER BY quarter DESC, category",
                (region,)
            ).fetchall()
        return self.conn.execute(
            "SELECT * FROM labor_rate ORDER BY region, quarter DESC, category"
        ).fetchall()

    def close(self):
        """关闭数据库"""
        self.conn.close()
