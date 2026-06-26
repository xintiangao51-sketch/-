#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投标分析自动化 v1.0
功能：扫描招标文件目录，自动提取评分规则、清单构成、竞争对手信息，
      生成结构化投标分析笔记
用法：python auto_bid_analyzer.py [project_dir]
"""
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path("D:/知识库")
PROJECTS_DIR = VAULT / "09-项目资料"


def extract_bid_info(md_path):
    """从招标分析笔记中提取关键信息"""
    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception:
        return None

    info = {"file": str(md_path.relative_to(VAULT))}

    # 项目名称
    m = re.search(r'project:\s*(.+)', text)
    if m:
        info["project"] = m.group(1).strip()

    # 评标方法
    if '综合评估法' in text:
        info["method"] = "综合评估法"
    elif '经评审的最低投标价法' in text:
        info["method"] = "经评审的最低投标价法"
    else:
        info["method"] = "未识别"

    # 最优报价区间
    m = re.search(r'K\s*=\s*[-]?\d+%\s*~\s*[-]?\d+%', text)
    if m:
        info["optimal_range"] = m.group(0)

    # 商务/技术/价格分值
    scores = {}
    for m in re.finditer(r'(商务|技术|价格)部分[：:]\s*(\d+)\s*分[，,\s]*(\d+)%', text):
        part = m.group(1)
        score = int(m.group(2))
        weight = int(m.group(3))
        scores[part] = f"{score}分({weight}%)"
    if scores:
        info["scores"] = scores

    # 金额信息
    for m in re.finditer(r'(中标金额|招标控制价|合同金额|投标报价)[：:]\s*([\d,.]+)\s*万', text):
        info[m.group(1)] = m.group(2) + "万"

    # 总建筑面积
    m = re.search(r'总建筑面积[：:]\s*([\d,.]+)\s*[㎡m2]', text)
    if m:
        info["area"] = m.group(1) + "㎡"

    # 单方造价
    m = re.search(r'单方造价[：:]\s*([\d,.]+)\s*元', text)
    if m:
        info["unit_cost"] = m.group(1) + "元/㎡"

    # 竞争对手
    competitors = re.findall(r'中标单位[：:]\s*(.+)', text)
    if competitors:
        info["winner"] = competitors[0].strip()

    # 风险关键词
    risks = []
    for kw in ["不平衡报价", "低于成本", "围标", "串标", "废标", "流标",
               "资产负债率", "背靠背", "资金风险"]:
        if kw in text:
            risks.append(kw)
    if risks:
        info["risks"] = risks

    return info


def generate_analysis_note(project_info, bid_data):
    """生成投标分析笔记"""
    today = datetime.now().strftime("%Y-%m-%d")
    project = project_info.get("name", "未知项目")
    method = bid_data.get("method", "未识别")

    lines = []
    lines.append("---")
    lines.append(f"tags: [投标, 投标/分析, 自动生成]")
    lines.append(f"created: {today}")
    lines.append(f"project: {project}")
    lines.append("type: analysis")
    lines.append("---")
    lines.append("")
    lines.append(f"# 投标分析: {project}")
    lines.append("")
    lines.append(f"> [AUTO] 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 评标方式")
    lines.append(f"- 评标方法: **{method}**")
    if "optimal_range" in bid_data:
        lines.append(f"- 最优报价区间: `{bid_data['optimal_range']}`")
    lines.append("")

    if "scores" in bid_data:
        lines.append("## 评分权重")
        lines.append("| 评分部分 | 分值 |")
        lines.append("|:---------|:---:|")
        for part, val in bid_data["scores"].items():
            lines.append(f"| {part}部分 | {val} |")
        lines.append("")

    if "winner" in bid_data:
        lines.append(f"## 中标信息")
        lines.append(f"- 中标单位: {bid_data['winner']}")
        lines.append("")

    if "area" in bid_data:
        lines.append(f"- 总建筑面积: {bid_data['area']}")
    if "unit_cost" in bid_data:
        lines.append(f"- 单方造价: {bid_data['unit_cost']}")
    lines.append("")

    if "risks" in bid_data:
        lines.append("## 风险提示")
        for r in bid_data["risks"]:
            lines.append(f"- [ ] {r}")
        lines.append("")

    lines.append("## 策略建议")
    lines.append("待人工分析")
    lines.append("")
    lines.append("## 关联笔记")
    if "file" in bid_data:
        lines.append(f"- 原始分析: [[{bid_data['file'].replace('.md', '')}]]")
    lines.append(f"- 投标策略: [[01-造价核心/投标报价策略库]]")
    lines.append("")
    lines.append("---")
    lines.append("[[知识库首页]]")

    return "\n".join(lines)


def scan_projects():
    """扫描所有项目，找出有招投标分析的项目"""
    results = []
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue

        # 查找招标文件/策略分析 目录
        bid_dirs = []
        for pattern in ["01-招标文件", "02-投标报价", "04-策略分析", "*招标*", "*投标*"]:
            for d in proj_dir.glob(pattern):
                if d.is_dir():
                    bid_dirs.append(d)

        if not bid_dirs:
            continue

        for bd in bid_dirs:
            for md in bd.glob("*.md"):
                if "总览" in md.stem or "体系框架" in md.stem:
                    continue
                info = extract_bid_info(md)
                if info:
                    info["project_dir"] = str(proj_dir.relative_to(VAULT))
                    results.append(info)

    return results


def main(dry_run=False):
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now():%H:%M}] auto_bid_analyzer v1.0")

    results = scan_projects()
    print(f"  scanned: {len(results)} bid analyses found")

    # 按项目分组
    from collections import defaultdict
    by_project = defaultdict(list)
    for r in results:
        by_project[r.get("project", "unknown")].append(r)

    generated = 0
    for project, items in by_project.items():
        summary = generate_analysis_note(
            {"name": project},
            items[0] if items else {}
        )
        if dry_run:
            print(f"  [DRY] {project}: {len(items)} sources")
        else:
            out_dir = VAULT / "05-投标报价/投标分析"
            out_dir.mkdir(parents=True, exist_ok=True)
            safe_name = project.replace("/", "-").replace("\\", "-")
            out_path = out_dir / f"投标分析_{safe_name}_{today}.md"
            out_path.write_text(summary, encoding='utf-8')
            print(f"  [OK] {out_path.relative_to(VAULT)}")
            generated += 1

    print(f"  {'DRY RUN' if dry_run else 'DONE'}: {generated} notes")
    return generated


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
