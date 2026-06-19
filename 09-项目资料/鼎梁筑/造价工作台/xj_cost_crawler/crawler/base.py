"""基础爬虫类，所有站点爬虫继承此类"""

import os
import re
import time
import logging
import hashlib
import requests
import urllib3
from pathlib import Path
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 禁用SSL警告（部分政府网站使用自签名或过期证书）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseCrawler(ABC):
    """新疆造价信息采集基础爬虫"""

    def __init__(self, config, db, source_conf):
        self.config = config
        self.db = db
        self.source_conf = source_conf
        self.name = source_conf["name"]
        self.base_url = source_conf["url"]
        self.keywords = config["keywords"]
        self.logger = logging.getLogger(self.name)

        # 请求配置
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config["crawl"]["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        # 针对政府网站SSL兼容性问题
        self.verify_ssl = True
        self.timeout = config["crawl"]["page_timeout_seconds"]
        self.delay = config["crawl"]["request_delay_seconds"]
        self.retry_count = config["crawl"]["retry_count"]
        self.retry_delay = config["crawl"]["retry_delay_seconds"]

        # 下载目录
        self.download_base = Path(config["download"]["base_dir"]) / "downloads"
        self.max_file_size = config["download"]["max_file_size_mb"] * 1024 * 1024

    @abstractmethod
    def run(self):
        """执行采集，返回 (found_count, saved_count)"""
        pass

    def fetch_page(self, url, encoding=None):
        """获取页面内容，自动处理SSL/TLS兼容性问题"""
        last_error = None
        for attempt in range(self.retry_count + 1):
            try:
                self.logger.debug(f"请求: {url} (尝试 {attempt+1})")
                resp = self.session.get(url, timeout=self.timeout, verify=self.verify_ssl)
                resp.raise_for_status()

                if encoding:
                    resp.encoding = encoding
                else:
                    # 自动检测编码
                    if resp.apparent_encoding and 'gb' in resp.apparent_encoding.lower():
                        resp.encoding = 'gb2312'
                    else:
                        resp.encoding = resp.apparent_encoding or 'utf-8'

                time.sleep(self.delay)
                return resp.text

            except requests.exceptions.SSLError as e:
                last_error = e
                self.logger.warning(f"SSL错误: {url} - 尝试关闭验证")
                self.verify_ssl = False  # 后续请求关闭SSL验证
                # 立即重试
                try:
                    resp = self.session.get(url, timeout=self.timeout, verify=False)
                    resp.raise_for_status()
                    if encoding:
                        resp.encoding = encoding
                    elif resp.apparent_encoding and 'gb' in resp.apparent_encoding.lower():
                        resp.encoding = 'gb2312'
                    else:
                        resp.encoding = resp.apparent_encoding or 'utf-8'
                    time.sleep(self.delay)
                    return resp.text
                except Exception as e2:
                    last_error = e2
                    self.logger.warning(f"SSL关闭后仍失败: {url} - {e2}")

            except requests.RequestException as e:
                last_error = e
                self.logger.warning(f"请求失败: {url} - {e}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)

        self.logger.error(f"请求最终失败: {url}")
        raise last_error or RuntimeError(f"请求失败: {url}")

    def fetch_json(self, url, params=None):
        """获取JSON API数据"""
        for attempt in range(self.retry_count):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                time.sleep(self.delay)
                return resp.json()
            except Exception as e:
                self.logger.warning(f"JSON请求失败: {url} - {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def download_file(self, url, save_dir, filename=None):
        """下载文件到本地"""
        try:
            resp = self.session.get(url, timeout=self.timeout, stream=True)
            resp.raise_for_status()

            # 检查文件大小
            content_length = int(resp.headers.get('content-length', 0))
            if content_length > self.max_file_size:
                self.logger.warning(f"文件过大({content_length/1024/1024:.1f}MB): {url}")
                return None

            # 生成文件名
            if not filename:
                cd = resp.headers.get('content-disposition', '')
                if 'filename' in cd:
                    filename = re.findall(r'filename[*]?=["\']?([^"\';\s]+)', cd)
                    filename = filename[0] if filename else None
                if not filename:
                    filename = urlparse(url).path.split('/')[-1]
                    if not filename or '.' not in filename:
                        filename = hashlib.md5(url.encode()).hexdigest()[:12] + '.pdf'

            # 清理文件名
            filename = re.sub(r'[\\/:*?"<>|]', '_', filename)

            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            full_path = save_path / filename

            # 已存在则跳过
            if full_path.exists():
                self.logger.debug(f"文件已存在: {full_path}")
                return str(full_path)

            with open(full_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"下载完成: {full_path}")
            time.sleep(self.delay)
            return str(full_path)

        except Exception as e:
            self.logger.error(f"下载失败: {url} - {e}")
            return None

    def match_keywords(self, text, category="all"):
        """检查文本是否匹配关键词"""
        if not text:
            return False, []
        text = text.lower()
        matched = []
        categories = [category] if category != "all" else self.keywords.keys()

        for cat in categories:
            if cat in self.keywords:
                for kw in self.keywords[cat]:
                    if kw.lower() in text:
                        matched.append((cat, kw))

        return len(matched) > 0, matched

    def parse_list_page(self, html, base_url):
        """通用列表页解析，提取标题和链接"""
        soup = BeautifulSoup(html, "html.parser")
        items = []

        # 常见政府网站列表结构
        selectors = [
            "ul.list li a",           # 常见列表
            "div.list-box li a",      # 列表盒子
            "table.list_table a",     # 表格列表
            "div.news-list li a",     # 新闻列表
            "ul.zwxl li a",          # 政务列表
            "div.main-content li a",  # 主内容区
            ".content-list li a",     # 内容列表
        ]

        for selector in selectors:
            links = soup.select(selector)
            if links:
                for link in links:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    if not title or not href:
                        continue
                    full_url = urljoin(base_url, href)
                    # 过滤无关链接
                    if any(skip in full_url for skip in ['javascript:', 'mailto:', '#']):
                        continue
                    # 提取日期（常见格式）
                    date_text = self._extract_date_from_text(title) or self._extract_date_from_sibling(link)
                    items.append({
                        "title": title,
                        "url": full_url,
                        "date": date_text
                    })
                break  # 找到匹配的选择器就停止

        # 备用：查找所有含href的<a>标签
        if not items:
            for link in soup.find_all("a", href=True):
                title = link.get_text(strip=True)
                href = link["href"]
                if len(title) < 4:  # 太短不像标题
                    continue
                full_url = urljoin(base_url, href)
                if any(skip in full_url for skip in ['javascript:', 'mailto:', '#']):
                    continue
                matched, _ = self.match_keywords(title)
                if matched:
                    items.append({
                        "title": title,
                        "url": full_url,
                        "date": self._extract_date_from_text(title)
                    })

        return items

    def _extract_date_from_text(self, text):
        """从文本中提取日期"""
        patterns = [
            r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?',
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        return None

    def _extract_date_from_sibling(self, tag):
        """从相邻元素提取日期"""
        parent = tag.parent
        if parent:
            parent_text = parent.get_text()
            return self._extract_date_from_text(parent_text)
        return None
