"""
三区参数同步脚本 — 知识库（母版）→ 造价工作台（引擎）

功能：
1. 检查知识库→工作台的参数一致性（人工单价、费率依据、价格库路径、定额库路径）
2. 报告差异，可用 --apply 自动同步可安全同步的项
3. 生成同步日志到 logs/sync_log.json

用法：
    python sync_config.py                    # 检查模式（只报告，不修改）
    python sync_config.py --apply            # 同步模式（自动更新config.yaml）
    python sync_config.py --kb-dir "D:\\知识库" --ws-dir "D:\\造价工作台"

注意：
    费率已于2026-06-24按新建标〔2021〕11号填入（安装工程默认值）
    本脚本验证费率依据文号是否一致，以及是否出现写死的28%/18%/22%
"""
import json
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple


# ============================================
# 路径常量
# ============================================
DEFAULT_KB_DIR = r"D:\知识库"
DEFAULT_WS_DIR = r"D:\造价工作台"

# 知识库权威参数源
KB_PRICE_DIR = "11-材料设备价格库"
KB_AGENTS_FILE = "10-索引与导航/AI-Agent五件套/AGENTS.md"
KB_QUOTA_INFO = "01-造价核心"  # 定额参数存放目录

# 工作台配置
WS_CONFIG = "config/config.yaml"
WS_PRICE_DB = "price_db"


def load_yaml(path: Path) -> Dict[str, Any]:
    """简易YAML读取（不依赖PyYAML，只处理config.yaml的缩进结构）"""
    try:
        import yaml
    except ImportError:
        # 回退到json方式读取（config.yaml非标准YAML时）
        return _parse_yaml_fallback(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_yaml_fallback(path: Path) -> Dict[str, Any]:
    """回退YAML解析（使用Python内置）"""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-c", f"import yaml; print(yaml.safe_load(open(r'{path}', encoding='utf-8')))"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        import ast
        return ast.literal_eval(result.stdout.strip())
    return {}


def save_yaml(path: Path, data: Dict[str, Any]):
    """保存YAML"""
    try:
        import yaml
    except ImportError:
        print("[错误] 需要安装PyYAML: pip install pyyaml")
        return False
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return True


def check_labor_prices(kb_dir: Path, ws_dir: Path) -> List[Dict]:
    """检查人工单价一致性"""
    findings = []
    
    # 知识库JSON
    kb_labor = ws_dir / WS_PRICE_DB / "labor_prices_xinjiang.json"
    if not kb_labor.exists():
        findings.append({
            "item": "人工单价JSON",
            "status": "missing",
            "message": f"工作台缺少 {kb_labor.name}，需运行 import_from_knowledge_base.py",
        })
        return findings
    
    with open(kb_labor, "r", encoding="utf-8") as f:
        labor_data = json.load(f)
    
    # 读取config.yaml中的人工单价
    config_path = ws_dir / WS_CONFIG
    config = load_yaml(config_path)
    ws_labor = config.get("pricing", {}).get("labor_price", {})
    
    # 比对关键地区
    key_regions = {
        "urumqi": "乌鲁木齐",
        "yili": "伊犁",
        "kashi": "喀什",
        "kezhou": "克州",
        "hetian": "和田",
    }
    
    kb_regions = labor_data.get("regions", {})
    for en_key, cn_name in key_regions.items():
        kb_price = kb_regions.get(en_key, {}).get("class_2", 0)
        ws_price = ws_labor.get(en_key, {}).get("class_2", 0) if isinstance(ws_labor.get(en_key), dict) else 0
        
        if kb_price == 0:
            findings.append({
                "item": f"人工单价-{cn_name}",
                "status": "warning",
                "message": f"知识库中{cn_name}二类工单价缺失",
            })
        elif ws_price == 0:
            findings.append({
                "item": f"人工单价-{cn_name}",
                "status": "warning",
                "message": f"工作台config.yaml中{cn_name}人工单价缺失",
            })
        elif abs(kb_price - ws_price) > 0.5:
            findings.append({
                "item": f"人工单价-{cn_name}",
                "status": "mismatch",
                "message": f"知识库={kb_price}元/工日，工作台={ws_price}元/工日——不一致",
                "kb_value": kb_price,
                "ws_value": ws_price,
            })
        else:
            findings.append({
                "item": f"人工单价-{cn_name}",
                "status": "ok",
                "message": f"{cn_name}二类工={kb_price}元/工日——一致",
            })
    
    return findings


def check_fee_rates(kb_dir: Path, ws_dir: Path) -> List[Dict]:
    """检查费率参数"""
    findings = []
    
    config_path = ws_dir / WS_CONFIG
    config = load_yaml(config_path)
    rates = config.get("pricing", {}).get("rates", {})
    
    # 检查费率是否为null
    mgmt = rates.get("management_fee")
    profit = rates.get("profit")
    reg = rates.get("regulatory_fee")
    tax = rates.get("tax", 0.09)
    
    if mgmt is None and profit is None and reg is None:
        findings.append({
            "item": "费率状态",
            "status": "warning",
            "message": "管理费/利润/规费均为null——费率未核定，需按新建标〔2021〕11号查表填入",
            "action_required": "人工查费率表后填入config.yaml",
        })
    elif mgmt is not None and profit is not None and reg is not None:
        findings.append({
            "item": "费率状态",
            "status": "ok",
            "message": f"管理费={mgmt}，利润={profit}，规费={reg}，税金={tax}——已核定",
        })
    else:
        findings.append({
            "item": "费率状态",
            "status": "warning",
            "message": f"费率部分核定: 管理={mgmt}，利润={profit}，规费={reg}——需补全",
        })
    
    # 检查费率依据
    rate_source = rates.get("rate_source", "")
    rate_basis = rates.get("rate_basis", "")
    
    if "新建标〔2021〕11号" in rate_source:
        findings.append({
            "item": "费率依据",
            "status": "ok",
            "message": f"文号: {rate_source} | 定额: {rate_basis}——正确",
        })
    else:
        findings.append({
            "item": "费率依据",
            "status": "mismatch",
            "message": f"费率文号异常: {rate_source}——应为'新建标〔2021〕11号'",
        })
    
    # 检查是否有写死的28%/18%/22%
    if mgmt == 0.28 or profit == 0.18 or reg == 0.22:
        findings.append({
            "item": "费率红线",
            "status": "error",
            "message": "🔴 检测到写死的28%/18%/22%——违反铁律，必须改为null或查表值",
        })
    
    return findings


def check_price_db(ws_dir: Path) -> List[Dict]:
    """检查价格库文件"""
    findings = []
    price_db = ws_dir / WS_PRICE_DB
    
    expected_files = {
        "material_prices_top100.json": "材料价格库Top100",
        "labor_prices_xinjiang.json": "人工价格库",
        "machinery_prices_top50.json": "机械台班价格库",
        "region_coefficients.json": "地区系数库",
    }
    
    for filename, desc in expected_files.items():
        fpath = price_db / filename
        if fpath.exists():
            size = fpath.stat().st_size
            findings.append({
                "item": f"价格库-{desc}",
                "status": "ok",
                "message": f"{filename} ({size/1024:.1f}KB)——存在",
            })
        else:
            findings.append({
                "item": f"价格库-{desc}",
                "status": "missing",
                "message": f"{filename}——缺失，需运行 import_from_knowledge_base.py",
            })
    
    # 检查config.yaml是否指向
    config_path = ws_dir / WS_CONFIG
    config = load_yaml(config_path)
    pricing = config.get("pricing", {})
    
    db_paths = {
        "material_price_db": "material_prices_top100.json",
        "labor_price_db": "labor_prices_xinjiang.json",
        "machinery_price_db": "machinery_prices_top50.json",
        "region_coefficients_db": "region_coefficients.json",
    }
    
    for config_key, expected_file in db_paths.items():
        actual = pricing.get(config_key)
        if actual and expected_file in str(actual):
            findings.append({
                "item": f"config-{config_key}",
                "status": "ok",
                "message": f"→ {actual}",
            })
        elif actual is None or actual == "null":
            findings.append({
                "item": f"config-{config_key}",
                "status": "warning",
                "message": f"config.yaml中{config_key}为null——需指向price_db/{expected_file}",
            })
        else:
            findings.append({
                "item": f"config-{config_key}",
                "status": "warning",
                "message": f"config.yaml中{config_key}={actual}——建议指向price_db/{expected_file}",
            })
    
    return findings


def check_quota_db(ws_dir: Path) -> List[Dict]:
    """检查定额库"""
    findings = []
    config_path = ws_dir / WS_CONFIG
    config = load_yaml(config_path)
    quota_path = config.get("pricing", {}).get("quota_db_path", "")
    
    if quota_path:
        full_path = ws_dir / quota_path
        if full_path.exists():
            size = full_path.stat().st_size
            findings.append({
                "item": "定额库",
                "status": "ok",
                "message": f"{quota_path} ({size/1024:.1f}KB)——存在",
            })
            
            # 检查定额条数
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                count = len(data) if isinstance(data, list) else len(data.get("quotas", data.get("records", [])))
                findings.append({
                    "item": "定额条数",
                    "status": "ok" if count >= 100 else "warning",
                    "message": f"当前{count}条" + ("——需扩至300+" if count < 100 else ""),
                })
            except Exception:
                pass
        else:
            findings.append({
                "item": "定额库",
                "status": "missing",
                "message": f"{quota_path}——文件不存在",
            })
    else:
        findings.append({
            "item": "定额库",
            "status": "warning",
            "message": "config.yaml中quota_db_path未配置",
        })
    
    return findings


def check_agent_consistency(kb_dir: Path, ws_dir: Path) -> List[Dict]:
    """检查Agent体系一致性"""
    findings = []
    
    # 知识库AGENTS.md
    kb_agents = kb_dir / KB_AGENTS_FILE
    if kb_agents.exists():
        content = kb_agents.read_text(encoding="utf-8")
        has_4agent = "Workbuddy" in content or "沃巴迪" in content
        has_2020 = "2020" in content and "版" in content
        has_2024 = "2024版消耗量" in content
        
        findings.append({
            "item": "知识库-AGENTS.md",
            "status": "ok" if (has_4agent and has_2020 and not has_2024) else "warning",
            "message": f"4Agent={'✅' if has_4agent else '❌'}, 2020版定额={'✅' if has_2020 else '❌'}, 无2024版={'✅' if not has_2024 else '❌'}",
        })
    else:
        findings.append({
            "item": "知识库-AGENTS.md",
            "status": "missing",
            "message": f"{kb_agents}——不存在",
        })
    
    # 鼎梁筑AGENTS.md
    dz_agents = Path(r"D:\鼎梁筑·AI造价工作服务\AGENTS.md")
    if dz_agents.exists():
        content = dz_agents.read_text(encoding="utf-8")
        has_4agent = "Workbuddy" in content or "沃巴迪" in content
        has_2020 = "2020" in content and "版" in content
        has_2024 = "2024版消耗量" in content
        
        findings.append({
            "item": "鼎梁筑-AGENTS.md",
            "status": "ok" if (has_4agent and has_2020 and not has_2024) else "warning",
            "message": f"4Agent={'✅' if has_4agent else '❌'}, 2020版定额={'✅' if has_2020 else '❌'}, 无2024版={'✅' if not has_2024 else '❌'}",
        })
    
    return findings


def sync_labor_prices(kb_dir: Path, ws_dir: Path) -> bool:
    """同步人工单价：重新运行import脚本"""
    print("\n[同步] 重新导入价格数据...")
    import_script = ws_dir / WS_PRICE_DB / "import_from_knowledge_base.py"
    if not import_script.exists():
        print(f"  [错误] 导入脚本不存在: {import_script}")
        return False
    
    import subprocess
    result = subprocess.run(
        [sys.executable, str(import_script)],
        capture_output=True, text=True, cwd=str(ws_dir)
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  [错误] {result.stderr}")
        return False
    return True


def generate_sync_log(findings: List[Dict], ws_dir: Path):
    """生成同步日志"""
    log_dir = ws_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log = {
        "timestamp": datetime.now().isoformat(),
        "findings": findings,
        "summary": {
            "total": len(findings),
            "ok": len([f for f in findings if f["status"] == "ok"]),
            "warning": len([f for f in findings if f["status"] == "warning"]),
            "error": len([f for f in findings if f["status"] == "error"]),
            "missing": len([f for f in findings if f["status"] == "missing"]),
            "mismatch": len([f for f in findings if f["status"] == "mismatch"]),
        },
    }
    
    log_path = log_dir / "sync_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    
    return log_path


def print_report(findings: List[Dict]):
    """打印检查报告"""
    status_icons = {
        "ok": "✅",
        "warning": "⚠️",
        "error": "🔴",
        "missing": "❌",
        "mismatch": "🔀",
    }
    
    print("\n" + "=" * 70)
    print("  三区参数同步检查报告")
    print("=" * 70)
    
    current_category = ""
    for f in findings:
        icon = status_icons.get(f["status"], "?")
        item = f["item"]
        msg = f["message"]
        print(f"  {icon} [{item}] {msg}")
    
    # 汇总
    summary = {
        "ok": len([f for f in findings if f["status"] == "ok"]),
        "warning": len([f for f in findings if f["status"] == "warning"]),
        "error": len([f for f in findings if f["status"] == "error"]),
        "missing": len([f for f in findings if f["status"] == "missing"]),
        "mismatch": len([f for f in findings if f["status"] == "mismatch"]),
    }
    
    print("\n" + "-" * 70)
    print(f"  汇总: ✅{summary['ok']} | ⚠️{summary['warning']} | 🔴{summary['error']} | ❌{summary['missing']} | 🔀{summary['mismatch']}")
    
    if summary["error"] > 0:
        print("  ⚠ 存在错误项，必须修复后才能使用引擎")
    elif summary["missing"] > 0 or summary["mismatch"] > 0:
        print("  ⚠ 存在缺失/不一致项，建议运行 --apply 同步")
    elif summary["warning"] > 0:
        print("  ⚠ 存在警告项，需人工确认")
    else:
        print("  ✅ 全部检查通过，三区参数一致")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="三区参数同步脚本 — 知识库→工作台")
    parser.add_argument("--kb-dir", default=DEFAULT_KB_DIR, help="知识库目录")
    parser.add_argument("--ws-dir", default=DEFAULT_WS_DIR, help="造价工作台目录")
    parser.add_argument("--apply", action="store_true", help="自动同步可安全同步的项")
    args = parser.parse_args()
    
    kb_dir = Path(args.kb_dir)
    ws_dir = Path(args.ws_dir)
    
    print(f"知识库: {kb_dir}")
    print(f"工作台: {ws_dir}")
    
    if not kb_dir.exists():
        print(f"[错误] 知识库目录不存在: {kb_dir}")
        sys.exit(1)
    if not ws_dir.exists():
        print(f"[错误] 工作台目录不存在: {ws_dir}")
        sys.exit(1)
    
    # 执行检查
    findings = []
    print("\n[检查] 人工单价...")
    findings.extend(check_labor_prices(kb_dir, ws_dir))
    
    print("[检查] 费率参数...")
    findings.extend(check_fee_rates(kb_dir, ws_dir))
    
    print("[检查] 价格库文件...")
    findings.extend(check_price_db(ws_dir))
    
    print("[检查] 定额库...")
    findings.extend(check_quota_db(ws_dir))
    
    print("[检查] Agent体系一致性...")
    findings.extend(check_agent_consistency(kb_dir, ws_dir))
    
    # 打印报告
    print_report(findings)
    
    # 生成日志
    log_path = generate_sync_log(findings, ws_dir)
    print(f"\n同步日志: {log_path}")
    
    # 应用同步
    if args.apply:
        needs_sync = any(f["status"] in ("missing", "mismatch") for f in findings)
        if needs_sync:
            print("\n[应用] 开始同步...")
            if sync_labor_prices(kb_dir, ws_dir):
                print("  [OK] 价格数据已重新导入")
            else:
                print("  [失败] 价格数据导入失败")
        else:
            print("\n[应用] 无需同步的项")
        
        # 注意：费率不会自动填入
        has_fee_warning = any("费率" in f["item"] and f["status"] == "warning" for f in findings)
        if has_fee_warning:
            print("\n  ⚠ 费率（管理费/利润/规费）不会自动填入——必须人工查新建标〔2021〕11号费率表后填入config.yaml")


if __name__ == "__main__":
    main()
