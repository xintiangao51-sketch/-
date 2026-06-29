#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提交前日志校验器 v1.0
功能：检查 commit message 与日志行数是否匹配，确保变更与记录一致
用法：python check_log.py [--auto-commit]
"""

import os
import re
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("D:/知识库")
LOG_PATH = VAULT_PATH / "00-工作台/日志.md"
COMMIT_MSG_PATH = VAULT_PATH / ".git/COMMIT_EDITMSG"


def count_log_entries(log_path):
    """统计日志中的条目数"""
    if not log_path.exists():
        return 0, []

    content = log_path.read_text(encoding='utf-8')
    # 匹配日志条目（以 - 或 * 开头的行）
    entries = re.findall(r'^\s*[-*]\s+(.+)$', content, re.MULTILINE)
    return len(entries), entries


def read_commit_msg(commit_msg_path):
    """读取最近的 commit message"""
    if not commit_msg_path or not Path(commit_msg_path).exists():
        # 尝试从 git log 读取
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%s'],
                capture_output=True,
                text=True,
                cwd=str(VAULT_PATH)
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""

    return Path(commit_msg_path).read_text(encoding='utf-8').strip()


def check_consistency(log_count, commit_msg):
    """检查日志条目数与 commit message 是否一致"""
    # 简单启发式：commit message 应该反映日志中的变更
    # 如果日志有 N 条，commit message 应该包含相关信息

    issues = []

    if log_count == 0 and commit_msg:
        issues.append("⚠️ 有 commit 但日志为空")
    elif log_count > 0 and not commit_msg:
        issues.append("⚠️ 有日志记录但无 commit message")
    elif log_count > 5 and len(commit_msg) < 20:
        issues.append(f"⚠️ 日志有 {log_count} 条但 commit message 过短")

    return issues


def suggest_commit_msg(log_entries):
    """根据日志条目建议 commit message"""
    if not log_entries:
        return "chore: 日常更新"

    # 提取关键词
    keywords = []
    for entry in log_entries[:3]:  # 只看前3条
        # 提取动作
        if '新增' in entry or '添加' in entry:
            keywords.append('feat')
        elif '修复' in entry or '修正' in entry:
            keywords.append('fix')
        elif '更新' in entry or '修改' in entry:
            keywords.append('update')
        elif '删除' in entry or '归档' in entry:
            keywords.append('refactor')

    if not keywords:
        keywords = ['update']

    # 生成建议
    freq = max(set(keywords), key=keywords.count)
    summary = log_entries[0][:30] if log_entries else '日常更新'

    return f"{freq}: {summary}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description='提交前日志校验器')
    parser.add_argument('--auto-commit', action='store_true', help='自动生成 commit message')
    args = parser.parse_args()

    print("[CheckLog] v1.0 启动...")

    # 统计日志
    log_count, log_entries = count_log_entries(LOG_PATH)
    print(f"[CheckLog] 日志条目数: {log_count}")

    if log_count > 0:
        print("[CheckLog] 最近日志:")
        for entry in log_entries[-3:]:
            print(f"  - {entry[:50]}")

    # 读取 commit message
    commit_msg = read_commit_msg(COMMIT_MSG_PATH)
    if commit_msg:
        print(f"[CheckLog] Commit: {commit_msg[:50]}")

    # 检查一致性
    issues = check_consistency(log_count, commit_msg)

    if issues:
        print("[CheckLog] ⚠️ 发现问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("[CheckLog] ✅ 日志与 commit 一致")

    # 建议 commit message
    suggested = suggest_commit_msg(log_entries)
    print(f"[CheckLog] 建议 commit message: {suggested}")

    if args.auto_commit:
        print(f"[CheckLog] 自动提交...")
        import subprocess
        try:
            subprocess.run(['git', 'add', '-A'], cwd=str(VAULT_PATH))
            subprocess.run(['git', 'commit', '-m', suggested], cwd=str(VAULT_PATH))
            print("[CheckLog] ✅ 提交完成")
        except Exception as e:
            print(f"[CheckLog] ❌ 提交失败: {e}")

    print("[CheckLog] DONE")


if __name__ == '__main__':
    main()
