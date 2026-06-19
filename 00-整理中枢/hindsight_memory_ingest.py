from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\知识库")
HERMES_HOME = Path(r"C:\Users\20752\AppData\Roaming\cn.org.hermesagent.desktop\runtime\hermes-home")
MEMORY_MD = HERMES_HOME / "memories" / "MEMORY.md"
USER_MD = HERMES_HOME / "memories" / "USER.md"
OUT_DIR = ROOT / "00-整理中枢" / "Hindsight记忆引擎"
OUT_DIR.mkdir(parents=True, exist_ok=True)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

def split_blocks(text: str):
    blocks = [b.strip() for b in re.split(r"\n?§\n?", text) if b.strip()]
    return blocks

def classify(block: str) -> tuple[str, str, list[str], int]:
    s = block.lower()
    if "新疆造价核心参数" in block or "定额" in block or "人工基价" in block or "费率" in block:
        return "cost_parameters", "新疆造价核心参数", ["新疆造价", "定额", "费率", "人工单价"], 100
    if "输出风格" in block or "结论先行" in block or "禁止" in block:
        return "output_preferences", "输出风格与沟通偏好", ["输出偏好", "沟通风格"], 95
    if "D盘资料" in block or "知识库" in block or "造价工作台" in block:
        return "workspace_assets", "本地资料与工作区", ["D盘", "知识库", "造价工作台"], 90
    if "Claude Code" in block or "技能" in block:
        return "tooling", "Claude Code与技能系统", ["Claude Code", "技能"], 80
    if "execute_code" in block or "沙箱" in block or "pip" in block:
        return "tooling_quirks", "执行环境与工具注意事项", ["execute_code", "Python", "工具约束"], 85
    if "新疆启创" in block or "鄯善启创" in block or "直接费" in block or "人材机" in block:
        return "project_case", "新疆启创/鄯善启创项目经验", ["项目案例", "鄯善启创", "人材机"], 88
    if "直接费表重构经验" in block or "重构处理" in block:
        return "workflow_experience", "直接费表重构经验", ["工作流", "Excel", "人材机拆分"], 88
    if "active workspace" in block or "D:\\知识库" in block or "D:/知识库" in block:
        return "workspace_root", "长期活动工作区", ["workspace", "知识库"], 100
    if "agency-agents" in block or "Codex" in block:
        return "agent_system", "工程行业代理人系统", ["Codex", "agent", "角色模板"], 82
    return "general_memory", "通用记忆", ["记忆"], 60

records = []
for source_name, path, store in [("MEMORY.md", MEMORY_MD, "memory"), ("USER.md", USER_MD, "user")]:
    text = read(path)
    for i, block in enumerate(split_blocks(text), 1):
        category, title, tags, priority = classify(block)
        records.append({
            "id": f"{store}-{i:03d}",
            "source_file": str(path),
            "source_name": source_name,
            "store": store,
            "category": category,
            "title": title,
            "priority": priority,
            "tags": tags,
            "retain_context": f"老高结构化记忆/{category}/{title}",
            "hindsight_tags": ["laogao", "structured-memory", category] + tags,
            "content": block,
        })

payload = {
    "engine": "Hindsight",
    "bank_id": "laogao-structured-memory",
    "generated_at": now,
    "workspace_root": str(ROOT),
    "source_files": [str(MEMORY_MD), str(USER_MD)],
    "record_count": len(records),
    "records": records,
}

(OUT_DIR / "memory_hindsight_ingest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

md = [
    "---",
    "tags: [Hindsight, 结构化记忆, Hermes, 老高]",
    "type: memory-engine-index",
    f"created: {now}",
    "---",
    "",
    "# Hindsight 结构化记忆引擎索引",
    "",
    f"- 记忆库：`laogao-structured-memory`",
    f"- 工作区：`{ROOT}`",
    f"- 来源：`{MEMORY_MD}`、`{USER_MD}`",
    f"- 结构化记录数：**{len(records)}**",
    "",
    "## 记忆分层",
    "",
    "|层级|用途|Hindsight标签|",
    "|---|---|---|",
    "|身份/偏好|稳定身份、输出风格、禁用话术|`user`, `output_preferences`|",
    "|造价核心|定额、人工、费率、核验红线|`cost_parameters`|",
    "|项目经验|鄯善启创、直接费表、人材机拆分等|`project_case`, `workflow_experience`|",
    "|环境路径|D盘工作区、知识库、工具安装位置|`workspace_assets`, `workspace_root`|",
    "|工具约束|execute_code沙箱、Claude/Codex代理系统|`tooling`, `tooling_quirks`, `agent_system`|",
    "",
    "## 结构化记录",
    "",
    "|ID|类别|标题|优先级|标签|",
    "|---|---|---|---:|---|",
]
for r in records:
    md.append(f"|{r['id']}|{r['category']}|{r['title']}|{r['priority']}|{', '.join(r['hindsight_tags'])}|")
md += [
    "",
    "## 接入方式",
    "",
    "1. Hermes 配置 `memory.provider=hindsight`。",
    "2. Hindsight 配置文件：`C:/Users/20752/AppData/Roaming/cn.org.hermesagent.desktop/runtime/hermes-home/hindsight/config.json`。",
    "3. 批量导入源：`memory_hindsight_ingest.json`。每条记录带 `retain_context` 与 `hindsight_tags`，可用 `hindsight_retain` 写入。",
]
(OUT_DIR / "Hindsight结构化记忆索引.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(json.dumps({"out_dir": str(OUT_DIR), "records": len(records)}, ensure_ascii=False))
