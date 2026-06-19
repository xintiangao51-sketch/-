"""自治区住建厅爬虫 — 采集定额、人工单价、信息价、勘误"""

import re
import logging
from pathlib import Path
from crawler.base import BaseCrawler


class ZJTCrawler(BaseCrawler):
    """自治区住建厅 https://zjt.xinjiang.gov.cn"""

    def __init__(self, config, db, source_conf):
        super().__init__(config, db, source_conf)
        self.name = "自治区住建厅"

    def run(self):
        found = 0
        saved = 0

        for path_conf in self.source_conf.get("search_paths", []):
            url = self.base_url + path_conf
            try:
                html = self.fetch_page(url)
                items = self.parse_list_page(html, self.base_url)
                self.logger.info(f"页面 {url} 发现 {len(items)} 条记录")

                for item in items:
                    found += 1
                    matched, matched_kws = self.match_keywords(item["title"])

                    if not matched:
                        continue

                    # 分类处理
                    categories = set(cat for cat, _ in matched_kws)
                    if "labor" in categories:
                        s = self._process_labor(item)
                    elif "material" in categories:
                        s = self._process_material(item)
                    elif "quota" in categories or "errata" in categories:
                        s = self._process_quota(item, categories)
                    elif "policy" in categories:
                        s = self._process_policy(item)
                    else:
                        s = self._save_doc(item, "其他")

                    saved += s

            except Exception as e:
                self.logger.error(f"采集页面失败: {url} - {e}")

        self.db.log_crawl(self.name, "daily", "success" if saved > 0 else "partial",
                         found, saved)
        return found, saved

    def _process_labor(self, item):
        """处理人工单价通知"""
        try:
            html = self.fetch_page(item["url"])
            if not html:
                return 0

            # 提取人工单价信息
            # 匹配模式：一类/二类/三类 + 数字 + 元/工日
            price_pattern = r'(一类|二类|三类|综合)\s*[：:]*\s*(\d+)\s*元[/每]工日'
            matches = re.findall(price_pattern, html)

            if not matches:
                # 备用模式：表格中的价格
                price_pattern2 = r'(\d{2,3})\s*元[/每]工日'
                matches2 = re.findall(price_pattern2, html)
                if not matches2:
                    # 尝试下载PDF解析
                    return self._save_doc(item, "人工单价")

            saved = 0
            for category, price in matches:
                # 确定季度
                quarter = self._guess_quarter(item["title"], item.get("date"))

                saved += self.db.save_labor_rate(
                    region="乌鲁木齐",
                    category=category,
                    price=float(price),
                    effective_date=item.get("date", ""),
                    quarter=quarter,
                    source_url=item["url"]
                )

            # 同时下载原文
            self._try_download_attachment(html, item, "labor/乌鲁木齐")

            return 1 if saved > 0 else 0

        except Exception as e:
            self.logger.error(f"处理人工单价失败: {item['title']} - {e}")
            return 0

    def _process_material(self, item):
        """处理材料信息价"""
        try:
            html = self.fetch_page(item["url"])
            if not html:
                return 0

            saved = self._save_doc(item, "材料信息价")
            self._try_download_attachment(html, item, "material/乌鲁木齐")

            return saved

        except Exception as e:
            self.logger.error(f"处理材料信息价失败: {item['title']} - {e}")
            return 0

    def _process_quota(self, item, categories):
        """处理定额文件"""
        doc_type = "勘误" if "errata" in categories else "定额"
        try:
            html = self.fetch_page(item["url"])
            if not html:
                return 0

            quota_system = self._detect_quota_system(item["title"])
            saved = self.db.save_quota_doc(
                title=item["title"],
                doc_type=doc_type,
                quota_system=quota_system,
                publish_date=item.get("date", ""),
                source_url=item["url"]
            )

            # 下载附件
            sub_dir = f"quota/{quota_system}" if quota_system else "quota/其他"
            self._try_download_attachment(html, item, sub_dir)

            return 1 if saved else 0

        except Exception as e:
            self.logger.error(f"处理定额文件失败: {item['title']} - {e}")
            return 0

    def _process_policy(self, item):
        """处理政策法规"""
        return self._save_doc(item, "政策法规")

    def _save_doc(self, item, doc_type):
        """通用文档保存"""
        quota_system = self._detect_quota_system(item["title"])
        saved = self.db.save_quota_doc(
            title=item["title"],
            doc_type=doc_type,
            quota_system=quota_system,
            publish_date=item.get("date", ""),
            source_url=item["url"]
        )
        return 1 if saved else 0

    def _try_download_attachment(self, html, item, sub_dir):
        """尝试下载页面中的附件"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # 查找附件链接
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            # 只下载PDF/Word/Excel附件
            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                from urllib.parse import urljoin
                file_url = urljoin(self.base_url, href)
                filename = href.split('/')[-1]
                save_dir = self.download_base / sub_dir
                self.download_file(file_url, save_dir, filename)

    def _guess_quarter(self, title, date_str):
        """从标题或日期推断季度"""
        # 先从标题提取
        q_match = re.search(r'(\d{4})\s*年第?([一二三四1-4])\s*季度', title)
        if q_match:
            year = q_match.group(1)
            q_map = {'一': 'Q1', '二': 'Q2', '三': 'Q3', '四': 'Q4',
                     '1': 'Q1', '2': 'Q2', '3': 'Q3', '4': 'Q4'}
            return f"{year}{q_map.get(q_match.group(2), 'Q?')}"

        # 从日期推断
        if date_str and len(date_str) >= 7:
            year = date_str[:4]
            month = int(date_str[5:7])
            q = (month - 1) // 3 + 1
            return f"{year}Q{q}"

        return ""

    def _detect_quota_system(self, title):
        """检测定额体系"""
        systems = {
            "房建": ["房建", "建筑", "装饰", "土建"],
            "市政": ["市政", "道路", "桥涵", "管网", "给排水"],
            "安装": ["安装", "电气", "管道", "消防", "通风"],
            "公路": ["公路", "路基", "路面", "桥涵"],
            "钢结构": ["钢结构", "钢构"],
            "装配式": ["装配式", "PC"],
        }
        for system, keywords in systems.items():
            if any(kw in title for kw in keywords):
                return system
        return "其他"
