from __future__ import annotations

from pathlib import Path
import json
import re

HERMES_HOME = Path(r"C:\Users\20752\AppData\Roaming\cn.org.hermesagent.desktop\runtime\hermes-home")
CFG_DIR = HERMES_HOME / "hindsight"
CFG_DIR.mkdir(parents=True, exist_ok=True)
CFG_PATH = CFG_DIR / "config.json"
ENV_PATH = HERMES_HOME / ".env"

config = {
    "mode": "local_embedded",
    "profile": "laogao-structured-memory",
    "bank_id": "laogao-structured-memory",
    "bank_id_template": "",
    "bank_mission": "老高/昕田的长期结构化记忆库：服务新疆工程造价、知识库整理、项目案例复用、工具环境约束与输出偏好保持。",
    "bank_retain_mission": "优先提取稳定事实、长期偏好、工程造价参数、项目经验、路径约定、工具限制；忽略一次性过程日志；不把待核实数据当作确定事实，保留⚠待核实标记。",
    "memory_mode": "hybrid",
    "recall_budget": "high",
    "recall_prefetch_method": "recall",
    "recall_max_tokens": 4096,
    "recall_max_input_chars": 1200,
    "recall_prompt_preamble": "# 老高结构化记忆（Hindsight）\n以下为跨会话长期记忆。优先遵循高优先级、已核实、带⚠待核实标记的事实；不要把待核实项说成已确认。",
    "recall_tags": "laogao,structured-memory",
    "recall_tags_match": "any",
    "recall_types": "observation,world,experience",
    "auto_recall": True,
    "auto_retain": True,
    "retain_async": True,
    "retain_every_n_turns": 1,
    "retain_context": "老高与Hermes的长期工作记忆",
    "retain_tags": "laogao,structured-memory,hermes-memory",
    "retain_source": "Hermes MEMORY.md / USER.md / D:/知识库",
    "retain_user_prefix": "老高",
    "retain_assistant_prefix": "Hermes",
    "timeout": 180,
    "idle_timeout": 600,
    "llm_provider": "openai_compatible",
    "llm_model": "ark-code-latest",
    "llm_base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
}
CFG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

# Safely update .env: copy existing ARK_CODING_API_KEY/ARK_API_KEY into HINDSIGHT_LLM_API_KEY without printing secrets.
lines = []
if ENV_PATH.exists():
    lines = ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
kv = {}
for line in lines:
    if line.strip() and not line.lstrip().startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        kv[k.strip()] = v.strip()

updates = {
    "HINDSIGHT_MODE": "local_embedded",
    "HINDSIGHT_BANK_ID": "laogao-structured-memory",
    "HINDSIGHT_BUDGET": "high",
    "HINDSIGHT_API_LLM_BASE_URL": "https://ark.cn-beijing.volces.com/api/coding/v3",
    "HINDSIGHT_TIMEOUT": "180",
    "HINDSIGHT_IDLE_TIMEOUT": "600",
    "HINDSIGHT_RETAIN_TAGS": "laogao,structured-memory,hermes-memory",
    "HINDSIGHT_RETAIN_SOURCE": "Hermes MEMORY.md / USER.md / D:/知识库",
}
if not kv.get("HINDSIGHT_LLM_API_KEY"):
    source_key = kv.get("ARK_CODING_API_KEY") or kv.get("ARK_API_KEY")
    if source_key:
        updates["HINDSIGHT_LLM_API_KEY"] = source_key

seen = set()
new_lines = []
for line in lines:
    if line.strip() and not line.lstrip().startswith("#") and "=" in line:
        k = line.split("=", 1)[0].strip()
        if k in updates:
            new_lines.append(f"{k}={updates[k]}")
            seen.add(k)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)
for k, v in updates.items():
    if k not in seen:
        new_lines.append(f"{k}={v}")
ENV_PATH.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")

print(json.dumps({
    "config_path": str(CFG_PATH),
    "env_path": str(ENV_PATH),
    "hindsight_llm_key_set": bool(updates.get("HINDSIGHT_LLM_API_KEY") or kv.get("HINDSIGHT_LLM_API_KEY")),
    "mode": config["mode"],
    "bank_id": config["bank_id"],
}, ensure_ascii=False))
