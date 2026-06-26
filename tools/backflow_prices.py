"""
价格数据回流脚本 — 造价工作台price_db → 知识库11-材料设备价格库

功能：
1. 读取price_db/中的4个JSON价格文件
2. 与知识库MD源文件比对，检测变更
3. 将变更写回知识库MD（追加更新日志段落）
4. 生成回流日志到 logs/backflow_log.json

用法：
    python backflow_prices.py                    # 检查模式（只报告变更）
    python backflow_prices.py --apply            # 回流模式（更新MD文件）
    python backflow_prices.py --kb-dir "D:\\知识库" --ws-dir "D:\\造价工作台"

设计原则：
- 知识库MD是母版，JSON是派生数据
- 回流时只在MD末尾追加"工作台更新日志"段落，不覆盖原始数据
- 原始MD数据保持不变，追加的日志记录工作台的计算结果或价格更新
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple

DEFAULT_KB_DIR = r"D:\知识库"
DEFAULT_WS_DIR = r"D:\造价工作台"
KB_PRICE_DIR = "11-材料设备价格库"
WS_PRICE_DB = "price_db"


def check_json_vs_md(
    json_path: Path, md_path: Path, json_key: str
) -> Dict[str, Any]:
    """检查JSON与MD的时间戳和内容差异"""
    if not json_path.exists():
        return {"status": "missing_json", "json": str(json_path)}
    if not md_path.exists():
        return {"status": "missing_md", "md": str(md_path)}

    json_mtime = datetime.fromtimestamp(json_path.stat().st_mtime)
    md_mtime = datetime.fromtimestamp(md_path.stat().st_mtime)

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_count = _count_records(json_data, json_key)

    return {
        "status": "ok",
        "json_path": str(json_path),
        "md_path": str(md_path),
        "json_mtime": json_mtime.isoformat(),
        "md_mtime": md_mtime.isoformat(),
        "json_newer": json_mtime > md_mtime,
        "json_count": json_count,
    }


def _count_records(data: Dict, key: str) -> int:
    """统计JSON中的记录数"""
    if key == "records":
        return len(data.get("records", []))
    elif key == "regions":
        return len(data.get("regions", {}))
    return 0


def generate_backflow_section(
    json_name: str, json_data: Dict, check_result: Dict
) -> str:
    """生成追加到MD末尾的回流日志段落"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    count = check_result.get("json_count", 0)

    section = f"""

---

## 📡 工作台数据回流日志

> 以下数据由造价工作台price_db自动回流，最后同步时间：{ts}

### 数据文件状态

| 指标 | 值 |
|------|-----|
| JSON文件 | `{json_name}` |
| 记录数 | {count}条 |
| JSON最后更新 | {check_result.get("json_mtime", "—")} |
| MD最后更新 | {check_result.get("md_mtime", "—")} |
| 同步状态 | {"JSON较新，需回流" if check_result.get("json_newer") else "已同步"} |

### 回流规则

1. 本段落由 `D:\\知识库\\tools\\backflow_prices.py` 自动生成
2. 原始MD数据（上方）为人工维护的母版，不自动覆盖
3. 工作台JSON为派生数据，当JSON比MD新时触发回流提醒
4. 如需更新母版数据，请人工编辑上方表格后重新运行 `import_from_knowledge_base.py`
"""
    return section


def backflow_material_prices(
    kb_dir: Path, ws_dir: Path, apply: bool = False
) -> List[Dict]:
    """材料价格回流"""
    findings = []
    json_path = ws_dir / WS_PRICE_DB / "material_prices_top100.json"
    md_path = kb_dir / KB_PRICE_DIR / "常用材料价格库_Top100.md"

    result = check_json_vs_md(json_path, md_path, "records")
    findings.append({**result, "item": "材料价格Top100"})

    if apply and result["status"] == "ok" and result.get("json_newer"):
        # 追加回流日志到MD
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        section = generate_backflow_section("material_prices_top100.json", json_data, result)
        _append_section(md_path, section)
        findings[-1]["action"] = "已追加回流日志"

    return findings


def backflow_labor_prices(
    kb_dir: Path, ws_dir: Path, apply: bool = False
) -> List[Dict]:
    """人工价格回流"""
    findings = []
    json_path = ws_dir / WS_PRICE_DB / "labor_prices_xinjiang.json"
    md_path = kb_dir / KB_PRICE_DIR / "新疆各地州人工价格汇总.md"

    result = check_json_vs_md(json_path, md_path, "regions")
    findings.append({**result, "item": "人工价格16地区"})

    if apply and result["status"] == "ok" and result.get("json_newer"):
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        section = generate_backflow_section("labor_prices_xinjiang.json", json_data, result)
        _append_section(md_path, section)
        findings[-1]["action"] = "已追加回流日志"

    return findings


def backflow_machinery_prices(
    kb_dir: Path, ws_dir: Path, apply: bool = False
) -> List[Dict]:
    """机械台班回流"""
    findings = []
    json_path = ws_dir / WS_PRICE_DB / "machinery_prices_top50.json"
    md_path = kb_dir / KB_PRICE_DIR / "机械台班价格库.md"

    result = check_json_vs_md(json_path, md_path, "records")
    findings.append({**result, "item": "机械台班Top50"})

    if apply and result["status"] == "ok" and result.get("json_newer"):
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        section = generate_backflow_section("machinery_prices_top50.json", json_data, result)
        _append_section(md_path, section)
        findings[-1]["action"] = "已追加回流日志"

    return findings


def backflow_region_coefficients(
    kb_dir: Path, ws_dir: Path, apply: bool = False
) -> List[Dict]:
    """地区系数回流"""
    findings = []
    json_path = ws_dir / WS_PRICE_DB / "region_coefficients.json"
    md_path = kb_dir / KB_PRICE_DIR / "各地州材料价格系数速查.md"

    result = check_json_vs_md(json_path, md_path, "regions")
    findings.append({**result, "item": "地区系数109地区"})

    if apply and result["status"] == "ok" and result.get("json_newer"):
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        section = generate_backflow_section("region_coefficients.json", json_data, result)
        _append_section(md_path, section)
        findings[-1]["action"] = "已追加回流日志"

    return findings


def _append_section(md_path: Path, section: str):
    """追加段落到MD文件末尾"""
    content = md_path.read_text(encoding="utf-8")
    # 避免重复追加
    if "📡 工作台数据回流日志" in content:
        # 替换已有段落
        idx = content.find("\n---\n\n## 📡 工作台数据回流日志")
        if idx > 0:
            content = content[:idx]
    content = content.rstrip() + section
    md_path.write_text(content, encoding="utf-8")


def generate_backflow_log(findings: List[Dict], ws_dir: Path) -> Path:
    """生成回流日志"""
    log_dir = ws_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    log = {
        "timestamp": datetime.now().isoformat(),
        "direction": "work台 → 知识库",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "need_backflow": len([f for f in findings if f.get("json_newer")]),
            "missing_json": len([f for f in findings if f["status"] == "missing_json"]),
            "missing_md": len([f for f in findings if f["status"] == "missing_md"]),
            "synced": len([f for f in findings if f["status"] == "ok" and not f.get("json_newer")]),
        },
    }

    log_path = log_dir / "backflow_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    return log_path


def print_report(findings: List[Dict]):
    """打印回流报告"""
    print("\n" + "=" * 70)
    print("  价格数据回流检查报告（工作台 → 知识库）")
    print("=" * 70)

    for f in findings:
        item = f.get("item", "?")
        status = f.get("status", "?")
        if status == "ok":
            newer = f.get("json_newer", False)
            count = f.get("json_count", 0)
            if newer:
                print(f"  🔄 [{item}] JSON较新，{count}条——需回流")
            else:
                print(f"  ✅ [{item}] 已同步，{count}条")
            if f.get("action"):
                print(f"      → {f['action']}")
        elif status == "missing_json":
            print(f"  ❌ [{item}] JSON文件缺失")
        elif status == "missing_md":
            print(f"  ❌ [{item}] 知识库MD文件缺失")
        else:
            print(f"  ? [{item}] 未知状态: {status}")

    summary = {
        "need_backflow": len([f for f in findings if f.get("json_newer")]),
        "synced": len([f for f in findings if f["status"] == "ok" and not f.get("json_newer")]),
        "missing": len([f for f in findings if f["status"] in ("missing_json", "missing_md")]),
    }

    print("\n" + "-" * 70)
    if summary["need_backflow"] > 0:
        print(f"  🔄 {summary['need_backflow']}项需回流——运行 --apply 执行")
    elif summary["missing"] > 0:
        print(f"  ❌ {summary['missing']}项文件缺失——需检查")
    else:
        print(f"  ✅ 全部同步，无需回流")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="价格数据回流 — 工作台→知识库")
    parser.add_argument("--kb-dir", default=DEFAULT_KB_DIR, help="知识库目录")
    parser.add_argument("--ws-dir", default=DEFAULT_WS_DIR, help="造价工作台目录")
    parser.add_argument("--apply", action="store_true", help="执行回流（更新MD）")
    args = parser.parse_args()

    kb_dir = Path(args.kb_dir)
    ws_dir = Path(args.ws_dir)

    print(f"知识库: {kb_dir}")
    print(f"工作台: {ws_dir}")

    findings = []
    findings.extend(backflow_material_prices(kb_dir, ws_dir, args.apply))
    findings.extend(backflow_labor_prices(kb_dir, ws_dir, args.apply))
    findings.extend(backflow_machinery_prices(kb_dir, ws_dir, args.apply))
    findings.extend(backflow_region_coefficients(kb_dir, ws_dir, args.apply))

    print_report(findings)

    log_path = generate_backflow_log(findings, ws_dir)
    print(f"\n回流日志: {log_path}")


if __name__ == "__main__":
    main()
