#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库脱敏处理器 v1.0
功能：
  1. 手机号脱敏
  2. 身份证号脱敏
  3. 邮箱地址脱敏
  4. 银行卡号脱敏
  5. 固定电话脱敏
  6. 自定义敏感词替换（单位名、人名等）
  7. 生成脱敏报告

用法：
  python desensitize.py [扫描目录] [--dry-run] [--output 报告路径]
  --dry-run  只扫描不修改，生成报告
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============ 配置 ============

# 扫描目录
SCAN_DIR = r"D:\知识库"

# 输出报告
REPORT_PATH = r"D:\知识库\.archive\脱敏扫描报告.md"

# 排除目录
EXCLUDE_DIRS = {".obsidian", ".archive", "node_modules", "__pycache__", ".git", ".tools"}

# 只处理的文件类型（排除JSON等数据文件，减少误报）
TEXT_EXTS = {".md", ".txt", ".csv", ".html", ".htm"}

# 敏感词映射（可扩展）
# 格式: {"原文": "替换后"}
CUSTOM_REPLACEMENTS = {
    # 示例（按需添加）：
    # "中铁二十五局": "[施工单位A]",
    # "高治国": "[姓名A]",
    # "侯佳": "[姓名B]",
}

# 人名检测配置（中文姓名，2-4个字）
# 注意：误报率较高，建议 dry-run 后人工确认
ENABLE_NAME_DETECTION = False  # 默认关闭，误报率高

# ============ 脱敏规则 ============

REPLACEMENT_RULES = [
    # (规则名, 正则, 替换模板, 描述)
    (
        "手机号",
        r"(?<!\d)1[3-9]\d{9}(?!\d)",
        lambda m: m.group()[:3] + "****" + m.group()[-4:],
        "11位手机号码"
    ),
    (
        "身份证号",
        r"(?<!\d)\d{17}[\dXx](?!\d)",
        lambda m: m.group()[:6] + "********" + m.group()[-4:],
        "18位身份证号码"
    ),
    (
        "身份证号15位",
        r"(?<!\d)\d{15}(?!\d)",
        lambda m: m.group()[:6] + "*****" + m.group()[-4:],
        "15位身份证号码（旧版）"
    ),
    (
        "邮箱地址",
        r"[\w.+-]+@[\w-]+\.[\w.]+",
        lambda m: m.group()[:2] + "***@" + m.group().split("@")[1],
        "电子邮箱"
    ),
    (
        "银行卡号",
        r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)",
        lambda m: m.group()[:4] + " **** **** " + m.group()[-4:],
        "16位银行卡号"
    ),
    (
        "银行卡号19位",
        r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3}(?!\d)",
        lambda m: m.group()[:4] + " **** **** **** " + m.group()[-4:],
        "19位银行卡号"
    ),
    (
        "固定电话",
        r"(?<!\d)0\d{2,3}[-\s]\d{7,8}(?!\d)",
        lambda m: m.group()[:4] + "-****" + m.group()[-4:],
        "固定电话号码（含区号-号码格式）"
    ),
    (
        "IP地址",
        r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)",
        lambda m: "***.***.***." + m.group().split(".")[-1],
        "IPv4地址"
    ),
]


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


def write_file_safe(filepath, content):
    """安全写入文件"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"   ⚠ 写入失败 {filepath}: {e}")
        return False


def is_target_file(filepath):
    """判断是否为目标文件"""
    ext = Path(filepath).suffix.lower()
    return ext in TEXT_EXTS


def get_relative_path(filepath, base_dir):
    """获取相对路径"""
    try:
        return os.path.relpath(filepath, base_dir)
    except Exception:
        return filepath


# ============ 脱敏处理器 ============

class Desensitizer:
    def __init__(self, scan_dir, dry_run=True):
        self.scan_dir = scan_dir
        self.dry_run = dry_run
        self.stats = defaultdict(int)  # 各规则命中次数
        self.file_results = []  # 每个文件的处理结果
        self.total_replacements = 0
        self.total_files_scanned = 0
        self.total_files_modified = 0

    def process_text(self, text, filepath=""):
        """对文本进行脱敏处理"""
        modified = False
        new_text = text
        file_replacements = defaultdict(int)

        # 自定义敏感词替换
        for original, replacement in CUSTOM_REPLACEMENTS.items():
            if original in new_text:
                count = new_text.count(original)
                new_text = new_text.replace(original, replacement)
                file_replacements[f"自定义:{original[:10]}"] += count
                modified = True

        # 正则规则替换
        for rule_name, pattern, replacer, desc in REPLACEMENT_RULES:
            matches = list(re.finditer(pattern, new_text))
            if matches:
                count = len(matches)
                new_text = re.sub(pattern, replacer, new_text)
                file_replacements[rule_name] += count
                self.stats[rule_name] += count
                modified = True

        return new_text, modified, file_replacements

    def process_file(self, filepath):
        """处理单个文件"""
        content = read_file_safe(filepath)
        if content is None:
            return None

        self.total_files_scanned += 1
        new_content, modified, replacements = self.process_text(content, filepath)

        if modified:
            self.total_files_modified += 1
            total_count = sum(replacements.values())
            self.total_replacements += total_count

            result = {
                "path": filepath,
                "rel_path": get_relative_path(filepath, self.scan_dir),
                "replacements": dict(replacements),
                "total_count": total_count,
                "size": os.path.getsize(filepath),
            }
            self.file_results.append(result)

            # 如果不是 dry-run，写回文件
            if not self.dry_run:
                # 先备份
                backup_path = filepath + ".bak"
                if not os.path.exists(backup_path):
                    shutil.copy2(filepath, backup_path)
                write_file_safe(filepath, new_content)

            return result

        return None

    def run(self):
        """运行脱敏处理"""
        mode = "🔍 扫描模式（dry-run）" if self.dry_run else "✏️ 处理模式（实际修改）"
        print(f"{mode}")
        print(f"📁 扫描目录: {self.scan_dir}")
        print(f"📄 处理文件类型: {', '.join(TEXT_EXTS)}")
        print()

        file_count = 0
        for root, dirs, files in os.walk(self.scan_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                filepath = os.path.join(root, f)
                if is_target_file(filepath):
                    self.process_file(filepath)
                    file_count += 1
                    if file_count % 100 == 0:
                        print(f"   已扫描 {file_count} 个文件...")

        print(f"\n✅ 扫描完成")
        return self.generate_report()

    def generate_report(self):
        """生成脱敏报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        mode = "扫描模式（dry-run）" if self.dry_run else "处理模式（已修改）"

        lines = [
            f"# 🔒 知识库脱敏扫描报告",
            f"",
            f"> 扫描时间: {now}",
            f"> 扫描目录: {self.scan_dir}",
            f"> 运行模式: {mode}",
            f"",
            f"---",
            f"",
            f"## 📊 统计摘要",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 扫描文件数 | {self.total_files_scanned} |",
            f"| 命中文件数 | {self.total_files_modified} |",
            f"| 替换总数 | {self.total_replacements} |",
            f"",
        ]

        # 各规则命中统计
        if self.stats:
            lines.append("## 📋 规则命中统计")
            lines.append("")
            lines.append("| 规则 | 命中次数 |")
            lines.append("|------|----------|")
            for rule, count in sorted(self.stats.items(), key=lambda x: -x[1]):
                lines.append(f"| {rule} | {count} |")
            lines.append("")

        # 详细文件列表
        if self.file_results:
            lines.append("## 📄 命中文件详情")
            lines.append("")
            for r in sorted(self.file_results, key=lambda x: -x["total_count"]):
                lines.append(f"### `{r['rel_path']}` （{r['total_count']}处）")
                lines.append("")
                for rule, count in r["replacements"].items():
                    lines.append(f"- {rule}: {count}处")
                lines.append("")

            # 简表
            lines.append("## 📋 命中文件汇总表")
            lines.append("")
            lines.append("| 文件 | 替换数 | 大小 |")
            lines.append("|------|--------|------|")
            for r in sorted(self.file_results, key=lambda x: -x["total_count"]):
                lines.append(f"| `{r['rel_path']}` | {r['total_count']} | {r['size']}B |")
            lines.append("")

        if not self.file_results:
            lines.append("## ✅ 未发现敏感信息")
            lines.append("")
            lines.append("知识库文件中未检测到手机号、身份证号、邮箱等敏感信息。")
            lines.append("")

        if not self.dry_run and self.file_results:
            lines.append("## ⚠️ 备份说明")
            lines.append("")
            lines.append("已修改的文件均创建了 `.bak` 备份。如需恢复：")
            lines.append("```bash")
            lines.append("# 恢复单个文件")
            lines.append("cp file.md.bak file.md")
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append(f"*报告由 desensitize.py 自动生成 · {now}*")

        report = "\n".join(lines)

        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 报告已生成: {REPORT_PATH}")
        return report


# ============ 主程序 ============

if __name__ == "__main__":
    scan_dir = SCAN_DIR
    dry_run = True
    output_path = REPORT_PATH

    # 解析参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--dry-run":
            dry_run = True
        elif args[i] == "--execute":
            dry_run = False
        elif args[i] == "--output" and i + 1 < len(args):
            i += 1
            output_path = args[i]
        elif not args[i].startswith("--"):
            scan_dir = args[i]
        i += 1

    # 安全确认
    if not dry_run:
        print("⚠️  即将以【执行模式】修改文件！")
        print(f"   目录: {scan_dir}")
        confirm = input("   确认执行？(输入 yes): ")
        if confirm.lower() != "yes":
            print("已取消。")
            sys.exit(0)

    desensitizer = Desensitizer(scan_dir, dry_run=dry_run)
    desensitizer.run()

    # 打印摘要
    print("\n" + "=" * 50)
    print("🔒 脱敏处理摘要")
    print("=" * 50)
    print(f"  扫描文件: {desensitizer.total_files_scanned}")
    print(f"  命中文件: {desensitizer.total_files_modified}")
    print(f"  替换总数: {desensitizer.total_replacements}")
    print(f"  运行模式: {'dry-run（仅扫描）' if dry_run else '已执行修改'}")
    print("=" * 50)
