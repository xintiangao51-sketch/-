#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excalidraw 索赔时间线自动生成 v1.0
扫描项目变更签证目录，提取事件信息，生成 .excalidraw 文件
用法：python auto_claim_timeline.py [--dry]
"""
import re
import sys
import json
from datetime import datetime
from pathlib import Path

VAULT = Path("D:/知识库")
PROJECTS_DIR = VAULT / "09-项目资料"

def scan_claim_docs():
    """扫描所有有变更/签证/索赔/策略目录的项目"""
    results = []
    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        proj_name = proj_dir.name

        # 查找变更/策略目录
        claim_dirs = []
        for sub in proj_dir.iterdir():
            if sub.is_dir() and any(kw in sub.name for kw in ["变更", "签证", "索赔", "策略"]):
                claim_dirs.append(sub)

        for cd in claim_dirs:
            for md in cd.glob("*.md"):
                if "总览" in md.stem:
                    continue
                text = md.read_text(encoding='utf-8')
                if len(text) < 100:
                    continue
                # Extract dates + events
                events = []
                for m in re.finditer(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})[：:]\s*(.+)', text):
                    events.append({"date": m.group(1), "desc": m.group(2)[:80]})
                for m in re.finditer(r'(\d{1,2}月\d{1,2}日)[：:，,]\s*(.+)', text):
                    events.append({"date": m.group(1), "desc": m.group(2)[:80]})

                results.append({
                    "project": proj_name,
                    "doc": md.stem,
                    "dir": cd.name,
                    "events": events,
                    "path": str(md.relative_to(VAULT)),
                })
    return results


def build_excalidraw(project, doc_name, events, output_path):
    """生成简单的 Excalidraw 时间线 JSON"""
    elements = []
    y = 100
    x_start = 200
    spacing = 130

    # Title
    elements.append({
        "type": "text", "x": x_start, "y": 40, "width": 600, "height": 35,
        "text": f"索赔时间线: {doc_name}", "fontSize": 20, "strokeColor": "#1e1e1e",
    })

    # Timeline bar
    n = min(len(events), 12)
    elements.append({
        "type": "rectangle", "x": x_start, "y": y + 12, "width": n * spacing, "height": 4,
        "strokeColor": "#2f80ed", "backgroundColor": "#2f80ed", "fillStyle": "solid",
    })

    for i, ev in enumerate(events[:12]):
        x = x_start + i * spacing
        # Node
        elements.append({
            "type": "ellipse", "x": x - 6, "y": y + 5, "width": 18, "height": 18,
            "strokeColor": "#eb5757", "backgroundColor": "#eb5757", "fillStyle": "solid",
        })
        # Date
        elements.append({
            "type": "text", "x": x - 40, "y": y + 28, "width": 100, "height": 18,
            "text": ev["date"][:10], "fontSize": 10, "strokeColor": "#828282",
        })
        # Desc
        desc = ev["desc"][:35]
        elements.append({
            "type": "text", "x": x - 50, "y": y + 48, "width": 250, "height": 20,
            "text": desc, "fontSize": 11, "strokeColor": "#1e1e1e",
        })

    drawing = {
        "type": "excalidraw",
        "version": 2,
        "source": "auto_claim_timeline v1.0",
        "elements": elements,
        "appState": {"viewBackgroundColor": "#ffffff"},
    }
    return json.dumps(drawing, ensure_ascii=False, indent=2)


def main(dry_run=False):
    print(f"[{datetime.now():%H:%M}] auto_claim_timeline v1.0")
    docs = scan_claim_docs()
    print(f"  scanned: {len(docs)} claim docs")

    generated = 0
    for item in docs:
        if not item["events"]:
            continue
        if dry_run:
            print(f"  [DRY] {item['project']}/{item['doc']}: {len(item['events'])} events")
        else:
            # Output next to source doc
            src = VAULT / item["path"]
            out_path = src.parent / f"索赔时间线_{item['doc'][:30]}.excalidraw.json"
            json_str = build_excalidraw(item["project"], item["doc"], item["events"], str(out_path))
            out_path.write_text(json_str, encoding='utf-8')
            print(f"  [OK] {out_path.relative_to(VAULT)}")
            generated += 1

    print(f"  {'DRY RUN' if dry_run else 'DONE'}: {generated} timelines")
    return generated


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    main(dry_run=dry)
