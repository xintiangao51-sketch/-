"""
采集成果回流脚本 — 鼎梁筑工作站采集数据 → 知识库16-运营数据

功能：
1. 扫描鼎梁筑采集数据/目录中的文件
2. 按文件类型和内容分类，映射到知识库16-运营数据/对应子目录
3. 复制（不移动）文件到知识库，保留原文件
4. 生成回流索引清单

用法：
    python backflow_leads.py                    # 检查模式（只报告）
    python backflow_leads.py --apply            # 执行复制
    python backflow_leads.py --station-dir "D:\\鼎梁筑·AI造价工作服务" --kb-dir "D:\\知识库"

回流规则：
- MD分析报告 → 16-运营数据/市场采集/
- JSON结构化数据 → 16-运营数据/市场采集/
- 营销素材（话术/脚本/分发包）→ 16-运营数据/营销素材/
- 战报 → 16-运营数据/市场采集/
- 周度分析报告 → 16-运营数据/市场采集/
"""
import json
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple

DEFAULT_STATION_DIR = r"D:\鼎梁筑·AI造价工作服务"
DEFAULT_KB_DIR = r"D:\知识库"
SOURCE_DIR_NAME = "采集数据"
TARGET_BASE = "16-运营数据"


# 文件分类规则
FILE_MAPPINGS = {
    # 营销素材类
    "营销素材": {
        "patterns": ["短视频脚本", "朋友圈", "微信群", "私聊", "话术", "分发"],
        "target_subdir": "营销素材",
    },
    # 市场采集类（报告+数据+战报）
    "市场采集": {
        "patterns": ["战报", "采集", "需求信号", "招标", "周度", "分析报告", "深度查询"],
        "target_subdir": "市场采集",
    },
}


def classify_file(filename: str) -> str:
    """根据文件名分类到目标子目录"""
    for category, config in FILE_MAPPINGS.items():
        for pattern in config["patterns"]:
            if pattern in filename:
                return config["target_subdir"]
    # 默认归入市场采集
    return "市场采集"


def scan_source(source_dir: Path) -> List[Dict[str, Any]]:
    """扫描采集数据目录"""
    files = []
    if not source_dir.exists():
        return files

    for f in source_dir.iterdir():
        if f.is_file() and not f.name.startswith("."):
            files.append({
                "filename": f.name,
                "source_path": str(f),
                "size": f.stat().st_size,
                "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "target_subdir": classify_file(f.name),
                "ext": f.suffix.lower(),
            })

    return files


def check_existing(target_path: Path) -> bool:
    """检查目标文件是否已存在"""
    return target_path.exists()


def copy_file(source: Path, target: Path) -> bool:
    """复制文件到目标路径"""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(target))
        return True
    except Exception as e:
        print(f"  [错误] 复制失败: {e}")
        return False


def generate_index(files: List[Dict], kb_dir: Path) -> Path:
    """在16-运营数据生成回流索引"""
    index_path = kb_dir / TARGET_BASE / "市场采集" / "_回流索引.md"

    lines = [
        "---",
        "tags: [索引, 运营, 采集]",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "type: index",
        "---",
        "",
        "# 📡 采集成果回流索引",
        "",
        f"> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 来源：D:\\鼎梁筑·AI造价工作服务\\采集数据\\",
        f"> 回流脚本：D:\\知识库\\tools\\backflow_leads.py",
        "",
        "## 文件清单",
        "",
        "| 文件名 | 类型 | 大小 | 目标位置 | 最后修改 |",
        "|--------|------|------|----------|----------|",
    ]

    for f in files:
        size_str = f"{f['size']/1024:.1f}KB" if f['size'] < 1024*1024 else f"{f['size']/1024/1024:.1f}MB"
        target_path = f"[[{TARGET_BASE}/{f['target_subdir']}/{f['filename']}|{f['filename']}]]"
        mtime_short = f['mtime'][:10]
        lines.append(f"| {f['filename']} | {f['ext']} | {size_str} | {target_path} | {mtime_short} |")

    lines.extend([
        "",
        "## 分类说明",
        "",
        "| 子目录 | 内容 |",
        "|--------|------|",
        "| 市场采集 | 招标信息、需求信号、战报、周度分析报告 |",
        "| 营销素材 | 短视频脚本、朋友圈/群分发素材、私聊话术 |",
        "",
        "## 回流规则",
        "",
        "1. 源文件保留在鼎梁筑工作站不动（复制不移动）",
        "2. 同名文件覆盖更新",
        "3. 超过90天的文件建议归档至99-归档库",
        "",
        f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])

    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def main():
    parser = argparse.ArgumentParser(description="采集成果回流 — 鼎梁筑→知识库")
    parser.add_argument("--station-dir", default=DEFAULT_STATION_DIR, help="鼎梁筑工作站目录")
    parser.add_argument("--kb-dir", default=DEFAULT_KB_DIR, help="知识库目录")
    parser.add_argument("--apply", action="store_true", help="执行复制")
    args = parser.parse_args()

    station_dir = Path(args.station_dir)
    kb_dir = Path(args.kb_dir)
    source_dir = station_dir / SOURCE_DIR_NAME

    print(f"工作站: {station_dir}")
    print(f"知识库: {kb_dir}")
    print(f"采集源: {source_dir}")

    if not source_dir.exists():
        print(f"\n[错误] 采集数据目录不存在: {source_dir}")
        sys.exit(1)

    # 扫描
    files = scan_source(source_dir)
    print(f"\n扫描到 {len(files)} 个文件")

    # 检查+复制
    new_count = 0
    update_count = 0
    skip_count = 0
    error_count = 0

    for f in files:
        target_dir = kb_dir / TARGET_BASE / f["target_subdir"]
        target_path = target_dir / f["filename"]
        exists = check_existing(target_path)

        if not args.apply:
            # 检查模式
            if exists:
                # 比较修改时间
                target_mtime = datetime.fromtimestamp(target_path.stat().st_mtime)
                source_mtime = datetime.fromisoformat(f["mtime"])
                if source_mtime > target_mtime:
                    status = "🔄需更新"
                    update_count += 1
                else:
                    status = "✅已同步"
                    skip_count += 1
            else:
                status = "🆕新文件"
                new_count += 1

            size_str = f"{f['size']/1024:.1f}KB" if f['size'] < 1024*1024 else f"{f['size']/1024/1024:.1f}MB"
            print(f"  {status} {f['filename']} ({size_str}) → {f['target_subdir']}/")
        else:
            # 执行模式
            source_path = Path(f["source_path"])
            if copy_file(source_path, target_path):
                if exists:
                    print(f"  🔄 [更新] {f['filename']} → {f['target_subdir']}/")
                    update_count += 1
                else:
                    print(f"  🆕 [新增] {f['filename']} → {f['target_subdir']}/")
                    new_count += 1
            else:
                error_count += 1

    # 生成索引
    if args.apply or new_count > 0 or update_count > 0:
        index_path = generate_index(files, kb_dir)
        print(f"\n回流索引: {index_path}")

    # 汇总
    print("\n" + "-" * 50)
    print(f"  汇总: 🆕{new_count} | 🔄{update_count} | ✅{skip_count} | ❌{error_count}")

    if not args.apply and (new_count > 0 or update_count > 0):
        print("  运行 --apply 执行回流")
    elif args.apply and error_count == 0:
        print("  ✅ 回流完成")
    elif args.apply and error_count > 0:
        print(f"  ⚠ {error_count}个文件复制失败")


if __name__ == "__main__":
    main()
