#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lingtai_xj.py — 新疆造价工程师版 知识库初始化 CLI

【来源】克隆自 灵台项目 scripts/lingtai.py
【改造点】
    1. 路径默认指向 D:\知识库（造价工程师工作区）
    2. 新增 engineer 模板（造价工作台 17 个目录）
    3. 保留原 3 模板（creator/programmer/business）供扩展
    4. 增加 --vault-root 参数兼容 bash sandbox

用法：
    python D:\知识库\.scripts\lingtai_xj.py init --template=engineer
    python D:\知识库\.scripts\lingtai_xj.py check
    python D:\知识库\.scripts\lingtai_xj.py help
    python D:\知识库\.scripts\lingtai_xj.py init --template=custom --domains="00-工作台,01-造价核心"
    python D:\知识库\.scripts\lingtai_xj.py init --template=engineer --name "昕田"
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ========== 路径探测（兼容 Windows / bash sandbox）==========
DEFAULT_VAULT_WIN = r'D:\知识库'
DEFAULT_VAULT_BASH = '/sessions/elegant-sweet-heisenberg/mnt/知识库'


def detect_vault():
    if os.path.isdir(DEFAULT_VAULT_WIN):
        return DEFAULT_VAULT_WIN
    if os.path.isdir(DEFAULT_VAULT_BASH):
        return DEFAULT_VAULT_BASH
    return os.getcwd()


# 解析 --vault-root 参数
def parse_vault():
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg.startswith('--vault-root='):
            return arg.split('=', 1)[1]
        if arg == '--vault-root' and i + 1 < len(args):
            return args[i + 1]
    return detect_vault()


VAULT_ROOT = Path(parse_vault()).resolve()


# ── 职业模板（灵台 3 + 新疆造价工程师 1）─────────────────────
TEMPLATES = {
    "engineer": {
        "name": "新疆造价工程师",
        "description": "新疆工程造价工程师工作台，覆盖定额/清单/合同/签证/投标/施工/AI工具",
        "domains": [
            ("00-工作台", "驾驶舱/项目跟踪/常用参数/费率速查"),
            ("01-造价核心", "定额/清单/取费/工程量/变更签证"),
            ("02-业务中台", "业务能力沉淀"),
            ("03-合同与法务", "合同/法规/索赔"),
            ("04-施工方案", "施组/方案/进度"),
            ("05-投标报价", "投标/报价策略/商务标"),
            ("06-参考文档", "参考资料"),
            ("07-AI工具与技能", "AI 工具/Skill"),
            ("08-参考规范", "国标/行标/地标原文"),
            ("09-项目资料", "项目档案/合同原件/签证单/图纸"),
            ("10-索引与导航", "总索引/五件套/KC 编号"),
            ("11-材料设备价格库", "材料/设备价格"),
            ("12-项目案例库", "复盘案例"),
            ("13-工程图纸", "图纸归档"),
            ("14-标准模板", "合同/清单/报告/签证模板"),
            ("15-数据资产", "Excel/CSV 数据库"),
            ("16-运营数据", "经营分析"),
            ("17-知识库引擎", "自动化脚本/RAG 入口"),
            ("98-原子知识库", "最小知识单元"),
            ("99-归档库", "已结项目归档"),
        ],
        "scripts": ["lint_xinjiang.py", "log_draft.py", "semantic_scan_xj.py"],
    },
    "creator": {
        "name": "内容创作者（灵台原版）",
        "domains": [
            ("00-思考与认知", "追问/O与π/独立思考/认知升级"),
            ("01-内容创作", "公众号/短视频/小红书/选题/爆款/文案"),
            ("02-成长与日常", "个人成长/日常反思/自律"),
            ("03-社会观察", "社会批判/规训/叙事消费"),
            ("04-哲学与思想", "易经/道家/权力/文明"),
            ("05-商业与投资", "创业/变现/副业/商业模式"),
            ("06-工具与AI", "AI工具/Obsidian/编程"),
            ("07-教育", "教育/学习/费曼/育儿"),
        ],
    },
    "programmer": {
        "name": "程序员（灵台原版）",
        "domains": [
            ("00-编程语言", "Python/JavaScript/Rust/Go/语法/特性"),
            ("01-框架与工具", "React/Vue/Django/Spring/工具链"),
            ("02-系统设计", "架构/分布式/微服务/高并发"),
            ("03-数据结构与算法", "排序/搜索/图/动态规划/复杂度"),
            ("04-数据库", "MySQL/Redis/MongoDB/Postgres/ES"),
            ("05-DevOps", "Docker/K8s/CI-CD/监控/部署"),
            ("06-安全", "认证/加密/漏洞/审计"),
            ("07-产品思维", "需求/用户体验/项目管理"),
        ],
    },
    "business": {
        "name": "商业/管理（灵台原版）",
        "domains": [
            ("00-行业洞察", "趋势/政策/竞争格局/报告"),
            ("01-商业模式", "盈利模式/定价/GMV/单位经济"),
            ("02-市场与营销", "获客/品牌/渠道/增长"),
            ("03-财务与风控", "成本/现金流/融资/审计"),
            ("04-组织与人才", "管理/招聘/激励/文化建设"),
            ("05-战略与决策", "定位/杠杆/判断/复盘"),
            ("06-政策与法规", "合规/税务/合同/知识产权"),
            ("07-认知与判断", "思维模型/决策偏误/学习"),
        ],
    },
}


def run(cmd, silent=False):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(VAULT_ROOT))
        if not silent and result.stderr:
            print(f"  ⚠ {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"  ❌ 命令失败: {' '.join(cmd)} — {e}")
        return ""


def check_env():
    print("🔍 检查环境...")
    ok = True
    py = shutil.which("python3") or shutil.which("python")
    if py:
        print(f"  ✅ Python: {run([py, '--version'], silent=True)}")
    else:
        print("  ❌ Python 未找到，请安装 Python 3.10+")
        ok = False

    git = shutil.which("git")
    if git:
        print(f"  ✅ Git: {run(['git', '--version'], silent=True)}")
    else:
        print("  ⚠ Git 未找到")

    if (VAULT_ROOT / "10-索引与导航" / "AI-Agent五件套" / "SOUL.md").exists():
        print(f"  ✅ 五件套完整: {VAULT_ROOT}")
    else:
        print(f"  ⚠ 未检测到五件套，请确认路径正确")
        ok = False

    return ok


def show_templates():
    print("\n📋 可选模板：")
    for key, tmpl in TEMPLATES.items():
        names = ", ".join(d[0] for d in tmpl["domains"][:5])
        more = f" +{len(tmpl['domains'])-5}" if len(tmpl["domains"]) > 5 else ""
        print(f"  [{key:12s}] {tmpl['name']} — {names}{more}")


def create_domains(domains):
    created = skipped = 0
    print("\n📁 创建知识库目录...")
    for domain, desc in domains:
        d = VAULT_ROOT / domain
        if not d.exists():
            d.mkdir(parents=True)
            print(f"  +  {domain}  （{desc}）")
            created += 1
        else:
            skipped += 1
    return created, skipped


def create_common(template_key):
    created = 0

    # 原料目录
    yuanliao = VAULT_ROOT / "09-项目资料"
    if not yuanliao.exists():
        yuanliao.mkdir(parents=True)
        print("  +  09-项目资料/")
        created += 1

    # 脚本目录
    scripts_dir = VAULT_ROOT / ".scripts"
    if not scripts_dir.exists():
        scripts_dir.mkdir(parents=True)
        print("  +  .scripts/  （运行 .scripts\\lint_xinjiang.py 体检）")
        created += 1

    # 索引文件占位
    index_file = VAULT_ROOT / "知识库总索引.md"
    if not index_file.exists():
        index_file.write_text(
            "# 知识库总索引\n\n> 由 AI 增量维护。每次新建/改名页面后追加一行。\n\n## 目录\n\n",
            encoding="utf-8",
        )
        print("  +  知识库总索引.md（占位）")
        created += 1

    # 日志文件占位
    log_file = VAULT_ROOT / "日志.md"
    if not log_file.exists():
        log_file.write_text(
            "# 知识库操作日志\n\n> 倒序排列。每次有产出后追加一行。\n\n",
            encoding="utf-8",
        )
        print("  +  日志.md（占位）")
        created += 1

    # .gitignore
    gitignore = VAULT_ROOT / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# 用户私有\n.workbuddymemory/\n.obsidian/workspace.json\n.obsidian/workspace-mobile.json\n\n# 临时\noutputs/\ninbox/\n__pycache__/\n*.pyc\n.cache/\n",
            encoding="utf-8",
        )
        print("  +  .gitignore")
        created += 1

    # 工程师模板额外：复制画像模板
    if template_key == "engineer":
        portrait_dst = VAULT_ROOT / "00-工作台" / "灵台用户画像·造价版.md"
        if not portrait_dst.exists():
            portrait_dst.write_text(
                "---\n标题: 灵台用户画像（造价版）\n日期: 2026-06-25\n主标签: #方法 #画像\ntype: 模板\ntags: [方法, 画像, 模板]\n---\n\n# 灵台用户画像·造价版\n\n> 复制本文件并填写。填了 AI 会更懂你。\n\n## 我是谁\n- 身份：\n- 知识领域：\n- 正在做的事：\n\n## 我怎么工作\n- 决策风格（谨慎 / 果断）：\n- 信息偏好（高密度 / 简洁）：\n- 沟通风格（直接 / 温和 / 极简）：\n- 工作时间段：\n\n## 我踩过的坑\n- 经常在什么类型的决策上反复纠结？\n- 有什么\"知道该做但总是拖着不做\"的事？\n- 知识管理上的坏习惯？\n",
                encoding="utf-8",
            )
            print("  +  00-工作台/灵台用户画像·造价版.md")
            created += 1

    return created


def init_vault(template_key=None, name=None):
    print(f"\n🏗️  初始化知识库...")
    print(f"   Vault: {VAULT_ROOT}\n")

    if template_key and template_key in TEMPLATES:
        tmpl = TEMPLATES[template_key]
        print(f"  模板：{tmpl['name']}")
        domains = tmpl["domains"]
    elif template_key == "custom":
        print(f"  自定义模板")
        domains = []
        for arg in sys.argv:
            if arg.startswith("--domains="):
                domains_str = arg.split("=", 1)[1]
                domains = [(d.strip(), "用户自定义") for d in domains_str.split(",")]
                break
    elif template_key:
        print(f"  ❌ 未知模板 '{template_key}'，可选：{', '.join(TEMPLATES.keys())}")
        return
    else:
        show_templates()
        print()
        while True:
            choice = input("  选择模板 (engineer/creator/programmer/business/custom): ").strip().lower()
            if choice in TEMPLATES:
                tmpl = TEMPLATES[choice]
                print(f"  已选：{tmpl['name']}")
                domains = tmpl["domains"]
                break
            elif choice == "custom":
                print("  自定义：稍后由 AI 引导创建")
                domains = []
                break
            else:
                print(f"  无效选项，请重选")

    created_d, skipped_d = create_domains(domains)
    created_c = create_common(template_key)

    total = created_d + created_c
    print(f"\n📊 新建 {total} 项，已存在 {skipped_d} 项")

    tname = tmpl["name"] if template_key and template_key in TEMPLATES else ""
    name_str = f"，{name}" if name else ""
    title = f"知识库已就绪{name_str}（{tname}）" if tname else f"知识库已就绪{name_str}"
    print(f"""
{'='*60}
  {title}

  下一步:
  1. 用 Obsidian 打开本文件夹
  2. 体检：python .scripts\\lint_xinjiang.py
  3. 放入原料：将造价资料丢入 09-项目资料/
  4. 填写画像：编辑 00-工作台\\灵台用户画像·造价版.md（可选）
  5. 对老高说：提炼
{'='*60}

  老高会读取 SOUL.md + AGENTS.md 自动启动协议。
""")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd in ("help", "-h", "--help"):
        print(__doc__)
        return

    if cmd == "check":
        check_env()
        return

    if cmd == "init":
        name = None
        template_key = None
        for arg in sys.argv[2:]:
            if arg.startswith("--name="):
                name = arg.split("=", 1)[1]
            elif arg.startswith("--template="):
                template_key = arg.split("=", 1)[1]
        init_vault(template_key, name)
        return

    print(f"未知命令: {cmd}\n")
    print(__doc__)


if __name__ == "__main__":
    main()
