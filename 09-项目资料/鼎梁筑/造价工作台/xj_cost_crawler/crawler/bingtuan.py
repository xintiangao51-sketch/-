"""新疆生产建设兵团爬虫 — 采集兵团定额及各师市信息价"""

from crawler.base import BaseCrawler


class BingtuanCrawler(BaseCrawler):
    """新疆生产建设兵团 http://www.xjbt.gov.cn"""

    # 各师市对应关系
    DIVISIONS = {
        "一师": "阿拉尔",
        "二师": "铁门关",
        "三师": "图木舒克",
        "四师": "可克达拉",
        "五师": "双河",
        "六师": "五家渠",
        "七师": "胡杨河",
        "八师": "石河子",
        "十师": "北屯",
        "十二师": "乌鲁木齐",
    }

    def __init__(self, config, db, source_conf):
        super().__init__(config, db, source_conf)
        self.name = "新疆生产建设兵团"

    def run(self):
        found = 0
        saved = 0

        for path_conf in self.source_conf.get("search_paths", []):
            url = self.base_url + path_conf
            try:
                html = self.fetch_page(url)
                items = self.parse_list_page(html, self.base_url)

                for item in items:
                    found += 1
                    matched, _ = self.match_keywords(item["title"])
                    if matched:
                        # 检测涉及哪个师
                        division = self._detect_division(item["title"])

                        self.db.save_quota_doc(
                            title=item["title"],
                            doc_type="兵团造价信息",
                            quota_system=f"兵团{division}" if division else "兵团",
                            publish_date=item.get("date", ""),
                            source_url=item["url"]
                        )

                        # 下载附件
                        try:
                            detail_html = self.fetch_page(item["url"])
                            if detail_html:
                                sub_dir = f"quota/兵团/{division}" if division else "quota/兵团"
                                self._try_download_attachment(detail_html, item, sub_dir)
                        except:
                            pass
                        saved += 1

            except Exception as e:
                self.logger.error(f"采集页面失败: {url} - {e}")

        self.db.log_crawl(self.name, "daily", "success" if saved > 0 else "partial",
                         found, saved)
        return found, saved

    def _detect_division(self, title):
        """检测涉及的师市"""
        for division, city in self.DIVISIONS.items():
            if division in title or city in title:
                return f"{division}({city})"
        return None

    def _try_download_attachment(self, html, item, sub_dir):
        """下载附件"""
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']):
                file_url = urljoin(self.base_url, href)
                filename = href.split('/')[-1]
                save_dir = self.download_base / sub_dir
                self.download_file(file_url, save_dir, filename)
