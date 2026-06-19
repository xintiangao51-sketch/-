#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库维护工具集入口
用法：
  python run_tools.py dedup      # 运行去冗扫描
  python run_tools.py scan       # 运行脱敏扫描（dry-run）
  python run_tools.py desensitize # 运行脱敏执行（修改文件）
  python run_tools.py all        # 全部扫描
"""

import sys
import os

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
SCAN_DIR = r"D:\知识库"

def run_dedup():
    """运行去冗扫描"""
    print("=" * 60)
    print("🧹 去冗扫描器")
    print("=" * 60)
    sys.argv = ["dedup_scanner.py", SCAN_DIR]
    exec(open(os.path.join(TOOLS_DIR, "dedup_scanner.py"), encoding="utf-8").read())

def run_desensitize_scan():
    """运行脱敏扫描（dry-run）"""
    print("=" * 60)
    print("🔒 脱敏扫描（dry-run 模式，不修改文件）")
    print("=" * 60)
    sys.argv = ["desensitize.py", SCAN_DIR, "--dry-run"]
    exec(open(os.path.join(TOOLS_DIR, "desensitize.py"), encoding="utf-8").read())

def run_desensitize_execute():
    """运行脱敏执行"""
    print("=" * 60)
    print("🔒 脱敏执行（将修改文件！）")
    print("=" * 60)
    sys.argv = ["desensitize.py", SCAN_DIR, "--execute"]
    exec(open(os.path.join(TOOLS_DIR, "desensitize.py"), encoding="utf-8").read())

def run_essence():
    """运行精华提炼"""
    print("=" * 60)
    print("💎 精华提炼器")
    print("=" * 60)
    sys.argv = ["essence_extractor.py", SCAN_DIR]
    exec(open(os.path.join(TOOLS_DIR, "essence_extractor.py"), encoding="utf-8").read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "dedup":
        run_dedup()
    elif cmd == "scan":
        run_desensitize_scan()
    elif cmd == "desensitize":
        run_desensitize_execute()
    elif cmd == "essence":
        run_essence()
    elif cmd == "all":
        run_dedup()
        print("\n")
        run_desensitize_scan()
        print("\n")
        run_essence()
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
