#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库精华提炼器 v1.0
功能：
  1. 按文件夹扫描 MD 文件
  2. 提取关键词（jieba TF-IDF）
  3. 提取核心句（TextRank 算法）
  4. 生成每个文件夹的「精华摘要.md」
  5. 自动链接回原文

用法：
  python essence_extractor.py [扫描目录]
"""

import os
import sys
import re
import math
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# ============ 配置 ============

SCAN_DIR = r"D:\知识库"
EXCLUDE_DIRS = {".obsidian", ".archive", "node_modules", "__pycache__", ".git", ".tools"}
OUTPUT_FILENAME = "_精华摘要.md"
MIN_FILE_LENGTH = 100  # 最小文件长度（字符），太短的跳过
TOP_KEYWORDS = 15      # 提取关键词数量
TOP_SENTENCES = 8      # 提取核心句数量
MAX_SUMMARY_LEN = 200  # 单文件摘要最大长度

# ============ 中文停用词 ============

STOP_WORDS = set("""
的 了 在 是 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有
过 对 自己 这 里 后 来 把 那 好 能 做 他 她 它 们 些 之 与 及 等 但 如 所 以
而 于 中 为 对 从 被 其 这个 那个 这些 那些 什么 怎么 哪个 每个 各个
可以 已经 或者 因为 所以 如果 虽然 但是 然后 因此 通过 进行 使用
根据 按照 关于 以及 并且 同时 其中 包括 由于 为了 除了 至于
文件 附件 通知 办法 规定 标准 要求 管理 工程 项目 施工 建设
单位 人员 部门 情况 问题 工作 方面 内容 相关 应当 不得
""".split())

# 工程造价领域关键词（提升权重）
DOMAIN_KEYWORDS = {
    "定额", "清单", "综合单价", "取费", "材料费", "人工费", "机械费",
    "变更", "索赔", "签证", "结算", "预算", "决算", "审计",
    "合同", "招标", "投标", "中标", "评标", "开标",
    "市政", "房建", "公路", "水利", "铁路", "隧道", "桥梁",
    "新疆", "乌鲁木齐", "喀什", "伊犁", "石河子",
    "混凝土", "钢筋", "模板", "土石方", "桩基", "防水",
    "安全", "质量", "进度", "成本", "利润", "规费", "税金",
    "施工组织", "施工方案", "技术交底", "竣工验收",
}

# ============ 工具函数 ============

def read_file_safe(filepath):
    """安全读取文件"""
    try:
        import chardet
        with open(filepath, "rb") as f:
            raw = f.read()
        detected = chardet.detect(raw)
        encoding = detected.get("encoding", "utf-8") or "utf-8"
        try:
            return raw.decode(encoding, errors="ignore")
        except Exception:
            return raw.decode("utf-8", errors="ignore")
    except Exception:
        return None


def clean_text(text):
    """清理文本（去除Markdown标记、HTML等）"""
    # 去除 YAML frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 去除 Markdown 标记
    text = re.sub(r"```[\s\S]*?```", "", text)  # 代码块
    text = re.sub(r"`[^`]+`", "", text)  # 行内代码
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # 链接/图片
    text = re.sub(r"[#*_~>|=-]+", "", text)  # 格式符号
    # 去除 Dataview 查询块
    text = re.sub(r"```dataview[\s\S]*?```", "", text)
    # 去除多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def split_sentences(text):
    """中文分句"""
    # 按中文标点和换行分句
    sentences = re.split(r"[。！？\n；;]+", text)
    # 过滤太短的句子
    return [s.strip() for s in sentences if len(s.strip()) >= 10]


def get_relative_path(filepath, base_dir):
    """获取相对路径"""
    try:
        return os.path.relpath(filepath, base_dir)
    except Exception:
        return filepath


# ============ 核心算法 ============

class EssenceExtractor:
    def __init__(self, scan_dir):
        self.scan_dir = scan_dir
        self.folder_data = {}  # {folder_path: [file_info, ...]}

    def collect_files(self):
        """收集所有 MD 文件，按文件夹分组"""
        for root, dirs, files in os.walk(self.scan_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            md_files = []
            for f in files:
                if not f.endswith(".md") or f.startswith("_精华") or f.startswith("_index"):
                    continue
                filepath = os.path.join(root, f)
                content = read_file_safe(filepath)
                if content and len(content) >= MIN_FILE_LENGTH:
                    md_files.append({
                        "path": filepath,
                        "rel_path": get_relative_path(filepath, self.scan_dir),
                        "name": f,
                        "content": content,
                        "clean_content": clean_text(content),
                        "size": os.path.getsize(filepath),
                    })
            if md_files:
                self.folder_data[root] = md_files

    def extract_keywords(self, texts, top_n=TOP_KEYWORDS):
        """提取关键词（TF-IDF）"""
        try:
            import jieba
            import jieba.analyse
        except ImportError:
            return []

        combined = "\n".join(texts)
        keywords = jieba.analyse.extract_tags(
            combined,
            topK=top_n,
            withWeight=True,
            allowPOS=("ns", "n", "vn", "v", "nr", "nt", "nz")
        )
        # 提升领域关键词权重
        result = []
        for word, weight in keywords:
            if word in DOMAIN_KEYWORDS:
                weight *= 1.5
            result.append((word, round(weight, 4)))
        result.sort(key=lambda x: -x[1])
        return result[:top_n]

    def extract_key_sentences(self, texts, top_n=TOP_SENTENCES):
        """提取核心句（TextRank 变体）"""
        # 合并所有文本并分句
        all_sentences = []
        for text in texts:
            all_sentences.extend(split_sentences(text))

        if len(all_sentences) < 3:
            return all_sentences[:top_n]

        # 简化版 TextRank：基于关键词重叠度的句子重要性评分
        try:
            import jieba
        except ImportError:
            # 无 jieba 时用简单方法
            return sorted(all_sentences, key=len, reverse=True)[:top_n]

        # 获取所有词
        all_words = []
        for s in all_sentences:
            words = [w for w in jieba.cut(s) if len(w) >= 2 and w not in STOP_WORDS]
            all_words.extend(words)
        word_freq = Counter(all_words)

        # 句子评分
        scored = []
        for s in all_sentences:
            words = [w for w in jieba.cut(s) if len(w) >= 2 and w not in STOP_WORDS]
            if not words:
                continue
            # 得分 = 包含的关键词频率之和 / 句子长度（归一化）
            score = sum(word_freq.get(w, 0) for w in words) / (len(words) ** 0.5)
            # 领域关键词加分
            domain_hits = sum(1 for w in words if w in DOMAIN_KEYWORDS)
            score += domain_hits * 2
            scored.append((s, score))

        scored.sort(key=lambda x: -x[1])
        # 去重（相似句只保留得分最高的）
        result = []
        seen = set()
        for s, score in scored:
            # 简单去重：前20字相同则认为重复
            key = s[:20]
            if key not in seen:
                seen.add(key)
                result.append(s)
            if len(result) >= top_n:
                break

        return result

    def summarize_file(self, file_info):
        """生成单文件摘要"""
        content = file_info["clean_content"]
        # 提取标题
        title_match = re.search(r"^#\s+(.+)", file_info["content"], re.MULTILINE)
        title = title_match.group(1) if title_match else file_info["name"].replace(".md", "")

        # 提取前几行作为摘要
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
        summary_lines = []
        total_len = 0
        for line in lines:
            if total_len + len(line) > MAX_SUMMARY_LEN:
                break
            summary_lines.append(line)
            total_len += len(line)

        return {
            "title": title,
            "summary": " ".join(summary_lines)[:MAX_SUMMARY_LEN],
        }

    def generate_folder_summary(self, folder_path, files):
        """生成文件夹精华摘要"""
        # 提取关键词
        texts = [f["clean_content"] for f in files]
        keywords = self.extract_keywords(texts)

        # 提取核心句
        key_sentences = self.extract_key_sentences(texts)

        # 生成各文件摘要
        file_summaries = []
        for f in files:
            summary = self.summarize_file(f)
            file_summaries.append({**f, **summary})

        # 文件夹名称
        folder_name = os.path.basename(folder_path)
        rel_folder = get_relative_path(folder_path, self.scan_dir)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 生成 Markdown
        lines = [
            f"---",
            f"tags: [精华, auto-generated]",
            f"created: {datetime.now().strftime('%Y-%m-%d')}",
            f"type: essence-summary",
            f"---",
            f"",
            f"# 💎 {folder_name} · 精华摘要",
            f"",
            f"> 自动生成于 {now}",
            f"> 文件数: {len(files)} | 返回 [[🏠 知识库首页]]",
            f"",
            f"---",
            f"",
        ]

        # 关键词
        if keywords:
            lines.append("## 🏷️ 核心关键词")
            lines.append("")
            keyword_tags = " ".join([f"`{w}`" for w, _ in keywords[:10]])
            lines.append(keyword_tags)
            lines.append("")
            lines.append("| 关词 | 权重 |")
            lines.append("|------|------|")
            for w, weight in keywords:
                lines.append(f"| {w} | {weight} |")
            lines.append("")

        # 核心句
        if key_sentences:
            lines.append("## 💡 核心要点")
            lines.append("")
            for i, s in enumerate(key_sentences, 1):
                # 截断过长的句子
                display = s[:150] + ("..." if len(s) > 150 else "")
                lines.append(f"{i}. {display}")
            lines.append("")

        # 文件摘要
        lines.append("## 📄 文件摘要")
        lines.append("")
        for fs in file_summaries:
            lines.append(f"### [[{fs['rel_path']}|{fs['title']}]]")
            lines.append("")
            if fs["summary"]:
                lines.append(f"> {fs['summary'][:200]}")
            lines.append("")

        # 相关链接
        lines.append("---")
        lines.append("")
        lines.append("## 🔗 相关索引")
        lines.append("")
        lines.append(f"- [[{rel_folder}/_index|📁 {folder_name} 文件索引]]")
        lines.append(f"- [[🏠 知识库首页|🏠 返回首页]]")
        lines.append(f"- [[🏷️ 标签体系|🏷️ 标签规范]]")
        lines.append("")
        lines.append("---")
        lines.append(f"*精华摘要自动生成 · {now}*")

        return "\n".join(lines)

    def run(self):
        """运行精华提炼"""
        print(f"💎 知识库精华提炼器")
        print(f"📁 扫描目录: {self.scan_dir}")
        print()

        self.collect_files()
        print(f"📂 发现 {len(self.folder_data)} 个含 MD 文件的目录")
        print()

        generated = 0
        for folder_path, files in sorted(self.folder_data.items()):
            rel = get_relative_path(folder_path, self.scan_dir)
            print(f"  📝 处理: {rel} ({len(files)} 个文件)")

            summary = self.generate_folder_summary(folder_path, files)
            output_path = os.path.join(folder_path, OUTPUT_FILENAME)

            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(summary)
                generated += 1
            except Exception as e:
                print(f"    ⚠ 写入失败: {e}")

        print()
        print(f"✅ 完成! 生成了 {generated} 个精华摘要文件")
        return generated


# ============ 主程序 ============

if __name__ == "__main__":
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else SCAN_DIR
    extractor = EssenceExtractor(scan_dir)
    extractor.run()
