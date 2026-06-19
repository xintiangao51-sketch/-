#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库去冗扫描器 v1.0
功能：
  1. 相似文件名检测（模糊匹配）
  2. 相同文件名检测（完全重复）
  3. 内容相似度检测（TF-IDF + 余弦相似度）
  4. 空文件检测
  5. 临时/垃圾文件检测
  6. 生成扫描报告

用法：python dedup_scanner.py [扫描目录] [输出报告路径]
"""

import os
import sys
import hashlib
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

# ============ 配置 ============

# 扫描目录
SCAN_DIR = r"D:\知识库"

# 输出报告
REPORT_PATH = r"D:\知识库\.archive\去冗扫描报告.md"

# 排除目录（不扫描）
EXCLUDE_DIRS = {".obsidian", ".archive", "node_modules", "__pycache__", ".git"}

# 排除文件扩展名（二进制大文件，不做内容比对）
BINARY_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".dwg", ".zip", ".rar",
               ".7z", ".mp4", ".mp3", ".avi", ".mov", ".pptx", ".ppt", ".exe",
               ".dll", ".so", ".bin", ".dat", ".db", ".sqlite", ".bak"}

# 临时/垃圾文件模式
JUNK_PATTERNS = [
    r"^~\$",              # Office 临时文件 ~$xxx.docx
    r"\.tmp$",            # .tmp 文件
    r"\.bak$",            # .bak 备份
    r"^\.DS_Store$",      # macOS
    r"Thumbs\.db$",       # Windows
    r"\.swp$",            # vim swap
    r"^Untitled\s",       # Obsidian 未命名文件
    r"\.crdownload$",     # Chrome 下载中
    r"\.part$",           # 部分下载
]

# 文件名相似度阈值（0-1，越高越严格）
NAME_SIMILARITY_THRESHOLD = 0.75

# 内容相似度阈值（TF-IDF 余弦相似度）
CONTENT_SIMILARITY_THRESHOLD = 0.85

# 最小文件大小（字节），低于此值视为空文件
EMPTY_FILE_THRESHOLD = 10

# ============ 工具函数 ============

def get_file_hash(filepath, block_size=65536):
    """计算文件 MD5"""
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                h.update(block)
        return h.hexdigest()
    except Exception:
        return None


def read_text_file(filepath, max_chars=50000):
    """读取文本文件内容（用于内容比对）"""
    try:
        import chardet
        with open(filepath, "rb") as f:
            raw = f.read(min(os.path.getsize(filepath), max_chars + 1024))
        detected = chardet.detect(raw)
        encoding = detected.get("encoding", "utf-8") or "utf-8"
        try:
            return raw.decode(encoding, errors="ignore")[:max_chars]
        except Exception:
            return raw.decode("utf-8", errors="ignore")[:max_chars]
    except Exception:
        return None


def normalize_filename(name):
    """标准化文件名（去除序号、日期、版本号等干扰项）"""
    name = Path(name).stem
    # 去除常见前缀序号：01-、02-、1.、2.
    name = re.sub(r"^\d+[\.\-_\s]+", "", name)
    # 去除日期：2024-01-01、20240101、2024.01.01
    name = re.sub(r"\d{4}[\-\.]?\d{2}[\-\.]?\d{2}", "", name)
    # 去除版本：v1、V2.0、(1)、(2)
    name = re.sub(r"[vV]\d+(\.\d+)?", "", name)
    name = re.sub(r"\(\d+\)", "", name)
    # 去除常见后缀词
    for suffix in ["副本", "备份", "copy", "Copy", "最终版", "修改版", "定稿", "初稿", "修订"]:
        name = name.replace(suffix, "")
    return name.strip().lower()


def is_junk_file(filename):
    """判断是否为垃圾/临时文件"""
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def get_relative_path(filepath, base_dir):
    """获取相对路径"""
    try:
        return os.path.relpath(filepath, base_dir)
    except Exception:
        return filepath


# ============ 扫描器 ============

class DedupScanner:
    def __init__(self, scan_dir):
        self.scan_dir = scan_dir
        self.all_files = []
        self.md_files = []
        self.results = {
            "duplicate_names": [],      # 完全同名文件
            "similar_names": [],        # 相似文件名
            "empty_files": [],          # 空文件
            "junk_files": [],           # 垃圾/临时文件
            "similar_content": [],      # 内容相似文件
            "hash_duplicates": [],      # MD5 完全相同
        }

    def scan_files(self):
        """扫描所有文件"""
        print(f"🔍 扫描目录: {self.scan_dir}")
        for root, dirs, files in os.walk(self.scan_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                filepath = os.path.join(root, f)
                ext = Path(f).suffix.lower()
                size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                file_info = {
                    "path": filepath,
                    "rel_path": get_relative_path(filepath, self.scan_dir),
                    "name": f,
                    "ext": ext,
                    "size": size,
                    "dir": root,
                }
                self.all_files.append(file_info)
                if ext == ".md":
                    self.md_files.append(file_info)

        print(f"   扫描完成: {len(self.all_files)} 个文件, {len(self.md_files)} 个 Markdown 文件")

    def check_empty_files(self):
        """检测空文件"""
        print("🔍 检测空文件...")
        for f in self.all_files:
            if f["size"] <= EMPTY_FILE_THRESHOLD and f["ext"] not in BINARY_EXTS:
                self.results["empty_files"].append(f)
        print(f"   发现 {len(self.results['empty_files'])} 个空文件")

    def check_junk_files(self):
        """检测垃圾/临时文件"""
        print("🔍 检测垃圾文件...")
        for f in self.all_files:
            if is_junk_file(f["name"]):
                self.results["junk_files"].append(f)
        print(f"   发现 {len(self.results['junk_files'])} 个垃圾/临时文件")

    def check_duplicate_names(self):
        """检测完全同名文件"""
        print("🔍 检测同名文件...")
        name_groups = defaultdict(list)
        for f in self.all_files:
            name_groups[f["name"].lower()].append(f)
        for name, files in name_groups.items():
            if len(files) > 1:
                self.results["duplicate_names"].append({
                    "name": name,
                    "files": files,
                    "count": len(files),
                })
        print(f"   发现 {len(self.results['duplicate_names'])} 组同名文件")

    def check_similar_names(self):
        """检测相似文件名"""
        print("🔍 检测相似文件名...")
        # 只对 MD 文件做相似名检测
        normalized = []
        for f in self.md_files:
            norm = normalize_filename(f["name"])
            if len(norm) >= 3:  # 太短的跳过
                normalized.append((f, norm))

        checked = set()
        for i, (f1, n1) in enumerate(normalized):
            for j, (f2, n2) in enumerate(normalized):
                if i >= j:
                    continue
                key = tuple(sorted([f1["path"], f2["path"]]))
                if key in checked:
                    continue
                checked.add(key)
                # 排除同目录下同名（已由 duplicate_names 处理）
                if f1["dir"] == f2["dir"] and f1["name"].lower() == f2["name"].lower():
                    continue
                ratio = SequenceMatcher(None, n1, n2).ratio()
                if ratio >= NAME_SIMILARITY_THRESHOLD and ratio < 1.0:
                    self.results["similar_names"].append({
                        "similarity": round(ratio, 2),
                        "file1": f1,
                        "file2": f2,
                    })
        # 按相似度降序
        self.results["similar_names"].sort(key=lambda x: -x["similarity"])
        print(f"   发现 {len(self.results['similar_names'])} 对相似文件名")

    def check_hash_duplicates(self):
        """检测 MD5 完全相同的文件"""
        print("🔍 检测内容完全相同的文件...")
        hash_groups = defaultdict(list)
        for f in self.all_files:
            if f["ext"] in BINARY_EXTS:
                h = get_file_hash(f["path"])
                if h:
                    hash_groups[h].append(f)
        for h, files in hash_groups.items():
            if len(files) > 1:
                total_size = sum(f["size"] for f in files)
                self.results["hash_duplicates"].append({
                    "hash": h,
                    "files": files,
                    "count": len(files),
                    "total_size": total_size,
                })
        print(f"   发现 {len(self.results['hash_duplicates'])} 组完全重复文件")

    def check_similar_content(self):
        """检测内容相似的 MD 文件（TF-IDF）"""
        print("🔍 检测内容相似的 Markdown 文件...")
        if len(self.md_files) < 2:
            print("   MD 文件太少，跳过")
            return

        try:
            import jieba
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            print("   ⚠ 缺少 jieba 或 sklearn，跳过内容相似度检测")
            return

        # 读取内容
        contents = []
        valid_files = []
        for f in self.md_files:
            text = read_text_file(f["path"])
            if text and len(text) >= 50:  # 太短的跳过
                # jieba 分词
                words = " ".join(jieba.cut(text))
                contents.append(words)
                valid_files.append(f)

        if len(contents) < 2:
            print("   有效内容文件太少，跳过")
            return

        print(f"   正在计算 {len(contents)} 个文件的 TF-IDF 相似度...")
        try:
            vectorizer = TfidfVectorizer(max_features=5000, token_pattern=r"(?u)\b\w+\b")
            tfidf_matrix = vectorizer.fit_transform(contents)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except Exception as e:
            print(f"   ⚠ TF-IDF 计算失败: {e}")
            return

        checked = set()
        for i in range(len(valid_files)):
            for j in range(i + 1, len(valid_files)):
                sim = sim_matrix[i][j]
                if sim >= CONTENT_SIMILARITY_THRESHOLD:
                    key = tuple(sorted([valid_files[i]["path"], valid_files[j]["path"]]))
                    if key not in checked:
                        checked.add(key)
                        self.results["similar_content"].append({
                            "similarity": round(float(sim), 3),
                            "file1": valid_files[i],
                            "file2": valid_files[j],
                        })

        self.results["similar_content"].sort(key=lambda x: -x["similarity"])
        print(f"   发现 {len(self.results['similar_content'])} 对内容相似文件")

    def run_all(self):
        """运行全部检测"""
        self.scan_files()
        self.check_empty_files()
        self.check_junk_files()
        self.check_duplicate_names()
        self.check_similar_names()
        self.check_hash_duplicates()
        self.check_similar_content()
        return self.results


# ============ 报告生成 ============

def generate_report(results, output_path):
    """生成 Markdown 报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 📋 知识库去冗扫描报告",
        f"",
        f"> 扫描时间: {now}",
        f"> 扫描目录: {SCAN_DIR}",
        f"",
        f"---",
        f"",
        f"## 📊 扫描统计",
        f"",
        f"| 类别 | 数量 |",
        f"|------|------|",
        f"| 空文件 | {len(results['empty_files'])} |",
        f"| 垃圾/临时文件 | {len(results['junk_files'])} |",
        f"| 完全同名文件 | {len(results['duplicate_names'])} 组 |",
        f"| 相似文件名 | {len(results['similar_names'])} 对 |",
        f"| MD5完全重复 | {len(results['hash_duplicates'])} 组 |",
        f"| 内容相似文件 | {len(results['similar_content'])} 对 |",
        f"",
    ]

    # 空文件
    if results["empty_files"]:
        lines.append("## 🗑️ 空文件（建议清理）")
        lines.append("")
        lines.append("| 文件 | 大小 |")
        lines.append("|------|------|")
        for f in results["empty_files"]:
            lines.append(f"| `{f['rel_path']}` | {f['size']}B |")
        lines.append("")

    # 垃圾文件
    if results["junk_files"]:
        lines.append("## 🗑️ 垃圾/临时文件（建议清理）")
        lines.append("")
        lines.append("| 文件 | 大小 | 原因 |")
        lines.append("|------|------|------|")
        for f in results["junk_files"]:
            reason = "临时文件" if f["name"].startswith("~$") else "垃圾文件"
            lines.append(f"| `{f['rel_path']}` | {f['size']}B | {reason} |")
        lines.append("")

    # 同名文件
    if results["duplicate_names"]:
        lines.append("## ⚠️ 完全同名文件（需人工确认保留哪个）")
        lines.append("")
        for group in results["duplicate_names"]:
            lines.append(f"### `{group['name']}` （{group['count']}个）")
            lines.append("")
            for f in group["files"]:
                lines.append(f"- `{f['rel_path']}` ({f['size']}B)")
            lines.append("")

    # 相似文件名
    if results["similar_names"]:
        lines.append("## ⚠️ 相似文件名（可能是同一内容的不同版本）")
        lines.append("")
        lines.append("| 相似度 | 文件1 | 文件2 |")
        lines.append("|--------|-------|-------|")
        for item in results["similar_names"][:50]:  # 最多显示50条
            lines.append(f"| {item['similarity']} | `{item['file1']['rel_path']}` | `{item['file2']['rel_path']}` |")
        lines.append("")

    # MD5 完全重复
    if results["hash_duplicates"]:
        lines.append("## 🔴 完全重复文件（内容100%相同，建议删除副本）")
        lines.append("")
        for group in results["hash_duplicates"]:
            lines.append(f"### MD5: `{group['hash'][:12]}...` （{group['count']}个，共 {group['total_size']}B）")
            lines.append("")
            for f in group["files"]:
                lines.append(f"- `{f['rel_path']}` ({f['size']}B)")
            lines.append("")

    # 内容相似
    if results["similar_content"]:
        lines.append("## 🟡 内容相似文件（TF-IDF 相似度 ≥ 0.85）")
        lines.append("")
        lines.append("| 相似度 | 文件1 | 文件2 |")
        lines.append("|--------|-------|-------|")
        for item in results["similar_content"][:50]:
            lines.append(f"| {item['similarity']} | `{item['file1']['rel_path']}` | `{item['file2']['rel_path']}` |")
        lines.append("")

    # 无问题
    total_issues = (len(results["empty_files"]) + len(results["junk_files"]) +
                    len(results["duplicate_names"]) + len(results["similar_names"]) +
                    len(results["hash_duplicates"]) + len(results["similar_content"]))
    if total_issues == 0:
        lines.append("## ✅ 未发现问题")
        lines.append("")
        lines.append("知识库文件状态良好，无需去冗处理。")
        lines.append("")

    lines.append("---")
    lines.append(f"*报告由 dedup_scanner.py 自动生成 · {now}*")

    report = "\n".join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 报告已生成: {output_path}")
    return report


# ============ 主程序 ============

if __name__ == "__main__":
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else SCAN_DIR
    report_path = sys.argv[2] if len(sys.argv) > 2 else REPORT_PATH

    scanner = DedupScanner(scan_dir)
    results = scanner.run_all()
    generate_report(results, report_path)

    # 打印摘要
    print("\n" + "=" * 50)
    print("📊 扫描完成摘要")
    print("=" * 50)
    print(f"  空文件:         {len(results['empty_files'])}")
    print(f"  垃圾文件:       {len(results['junk_files'])}")
    print(f"  同名文件组:     {len(results['duplicate_names'])}")
    print(f"  相似文件名对:   {len(results['similar_names'])}")
    print(f"  MD5重复组:      {len(results['hash_duplicates'])}")
    print(f"  内容相似对:     {len(results['similar_content'])}")
    print("=" * 50)
