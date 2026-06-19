"""乌鲁木齐住建局爬虫 — 重点采集人工单价季度通知"""

from crawler.base import BaseCrawler


class WLMQCrawler(BaseCrawler):
    """乌鲁木齐住建局 https://zjj.wulumuqi.gov.cn"""

    def __init__(self, config, db, source_conf):
        super().__init__(config, db, source_conf)
        self.name = "乌鲁木齐住建局"

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
                    matched, _ = self.match_keywords(item["title"])
                    if matched:
                        # 乌鲁木齐是人工单价首发站，重点处理
                        saved += self._process_item(item)

            except Exception as e:
                self.logger.error(f"采集页面失败: {url} - {e}")

        self.db.log_crawl(self.name, "daily", "success" if saved > 0 else "partial",
                         found, saved)
        return found, saved

    def _process_item(self, item):
        """处理单条记录"""
        try:
            html = self.fetch_page(item["url"])
            if not html:
                return 0

            # 下载附件
            self._try_download_attachment(html, item, "labor/乌鲁木齐")

            # 保存文档记录
            self.db.save_quota_doc(
                title=item["title"],
                doc_type="人工单价通知",
                quota_system="全体系",
                publish_date=item.get("date", ""),
                source_url=item["url"]
            )
            return 1

        except Exception as e:
            self.logger.error(f"处理失败: {item['title']} - {e}")
            return 0

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
