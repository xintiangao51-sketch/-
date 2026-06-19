"""自治区交通运输厅爬虫 — 采集公路造价信息"""

from crawler.base import BaseCrawler


class JTYSTCrawler(BaseCrawler):
    """自治区交通运输厅 https://jtyst.xinjiang.gov.cn"""

    def __init__(self, config, db, source_conf):
        super().__init__(config, db, source_conf)
        self.name = "自治区交通运输厅"

    def run(self):
        found = 0
        saved = 0

        # 额外搜索公路造价关键词
        extra_keywords = ["公路造价", "材料价", "补充定额", "计价依据"]

        for path_conf in self.source_conf.get("search_paths", []):
            url = self.base_url + path_conf
            try:
                html = self.fetch_page(url)
                items = self.parse_list_page(html, self.base_url)

                for item in items:
                    found += 1
                    # 公路体系关键词匹配
                    title = item["title"]
                    if any(kw in title for kw in extra_keywords):
                        matched = True
                    else:
                        matched, _ = self.match_keywords(title)

                    if matched:
                        self.db.save_quota_doc(
                            title=title,
                            doc_type="公路造价",
                            quota_system="公路",
                            publish_date=item.get("date", ""),
                            source_url=item["url"]
                        )

                        # 下载附件
                        try:
                            detail_html = self.fetch_page(item["url"])
                            if detail_html:
                                self._try_download_attachment(detail_html, item, "quota/公路")
                        except:
                            pass
                        saved += 1

            except Exception as e:
                self.logger.error(f"采集页面失败: {url} - {e}")

        self.db.log_crawl(self.name, "daily", "success" if saved > 0 else "partial",
                         found, saved)
        return found, saved

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
