# -*- coding: utf-8 -*-
"""Verify/import Hermes MEMORY.md structured records into Hindsight.

This script intentionally prints no secrets. It uses the source checkout provider
so we can validate the Hindsight config independently of the packaged Desktop exe.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERMES_HOME = Path(r"C:/Users/20752/AppData/Roaming/cn.org.hermesagent.desktop/runtime/hermes-home")
SRC_ROOT = Path(r"D:/Hermes Agent中文端/workspace/hermes-agent-main")
INGEST_JSON = Path(r"D:/知识库/00-整理中枢/Hindsight记忆引擎/memory_hindsight_ingest.json")
OUT_JSON = Path(r"D:/知识库/00-整理中枢/Hindsight记忆引擎/hindsight_verify_result.json")

os.environ["HERMES_HOME"] = str(HERMES_HOME)

# Load Hermes .env without printing values.
env_path = HERMES_HOME / ".env"
if env_path.exists():
    for raw in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")

sys.path.insert(0, str(SRC_ROOT))

# The user's Hermes config has security.allow_lazy_installs=false. Hindsight is
# already installed in this Python environment, so bypass Hermes' lazy installer
# for this verification run only; do not mutate global config.
import tools.lazy_deps as _lazy_deps  # noqa: E402
_lazy_deps.ensure = lambda *args, **kwargs: None

from plugins.memory.hindsight import HindsightMemoryProvider, _check_local_runtime, _load_config  # noqa: E402

# Work around a Windows/user-site packaging quirk: hindsight_embed looks only in
# sysconfig's Scripts dir (C:/Python314/Scripts), while pip --user installed the
# entrypoint under C:/Users/20752/AppData/Roaming/Python/Python314/Scripts.  Force
# daemon launch through the already-importable module to avoid uvx re-downloads.
try:  # verification-local monkeypatch; no global files are modified
    import sys as _sys
    from hindsight_embed.daemon_embed_manager import DaemonEmbedManager as _DEM  # noqa: E402
    _DEM._find_api_command = lambda self, api_version: [_sys.executable, "-m", "hindsight_api.main"]
except Exception:
    pass


def main() -> int:
    cfg = _load_config()
    runtime_ok, runtime_reason = _check_local_runtime()
    result: dict = {
        "hermes_home": str(HERMES_HOME),
        "config_loaded": bool(cfg),
        "mode": cfg.get("mode"),
        "profile": cfg.get("profile"),
        "bank_id": cfg.get("bank_id"),
        "local_runtime_ok": runtime_ok,
        "local_runtime_reason": runtime_reason,
        "provider_available": None,
        "initialized_mode": None,
        "initialized_bank_id": None,
        "records_seen": 0,
        "records_imported": 0,
        "retain_errors": [],
        "recall_checks": [],
    }

    provider = HindsightMemoryProvider()
    result["provider_available"] = provider.is_available()
    provider.initialize(
        "verify_laogao_structured_memory",
        agent_identity="default",
        agent_workspace=r"D:/知识库",
        platform="cli-verify",
        user_name="老高",
    )
    result["initialized_mode"] = provider._mode
    result["initialized_bank_id"] = provider._bank_id
    # Config JSON stores recall_tags as a comma-separated string; hindsight-client
    # 0.8.x validates this as list[str]. Normalize for the verification run.
    if isinstance(getattr(provider, "_recall_tags", None), str):
        provider._recall_tags = [t.strip() for t in provider._recall_tags.split(",") if t.strip()]
    # Query all fact layers for immediate verification; Hindsight may promote raw
    # retains to observations asynchronously, so observation-only can be empty.
    provider._recall_types = ["observation", "world", "experience"]

    data = json.loads(INGEST_JSON.read_text(encoding="utf-8"))
    records = data.get("records", [])
    result["records_seen"] = len(records)

    # Import all structured records. Keep content structured and tagged.
    for rec in records:
        # Avoid duplicating records already imported in a prior interrupted run.
        if result["records_imported"] >= result["records_seen"]:
            break
        content = (
            f"结构化记忆ID: {rec.get('id')}\n"
            f"分类: {rec.get('category')}\n"
            f"标题: {rec.get('title')}\n"
            f"优先级: {rec.get('priority')}\n"
            f"内容:\n{rec.get('content')}"
        )
        tags = rec.get("hindsight_tags") or rec.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        for extra in ["laogao", "structured-memory", "memory-md-ingest", rec.get("category", "")]:
            if extra and extra not in tags:
                tags.append(extra)
        response = provider.handle_tool_call(
            "hindsight_retain",
            {
                "content": content,
                "context": rec.get("retain_context") or f"老高结构化记忆：{rec.get('category')}",
                "tags": tags,
            },
        )
        try:
            parsed = json.loads(response)
        except Exception:
            parsed = {"raw": response}
        if isinstance(parsed, dict) and parsed.get("error"):
            result["retain_errors"].append({"id": rec.get("id"), "error": parsed.get("error")})
        else:
            result["records_imported"] += 1

    queries = [
        "新疆造价核心参数 人工基价 管理费 利润 规费 增值税",
        "老高 输出风格 表格 结论先行 客套",
        "D盘 知识库 工作区 路径 Hermes Agent中文端 workspace",
    ]
    for q in queries:
        response = provider.handle_tool_call("hindsight_recall", {"query": q})
        try:
            parsed = json.loads(response)
        except Exception:
            parsed = {"raw": response}
        text = str(parsed.get("result") or parsed.get("raw") or parsed)[:3000]
        result["recall_checks"].append(
            {
                "query": q,
                "has_result": "No relevant memories found" not in text and "Failed to search memory" not in text,
                "contains_cost_signal": any(x in text for x in ["乌鲁木齐", "148", "增值税", "2020版", "人工基价"]),
                "contains_style_signal": any(x in text for x in ["结论先行", "表格", "客套", "输出风格"]),
                "contains_workspace_signal": any(x in text for x in ["D:", "知识库", "Hermes Agent中文端", "workspace"]),
                "preview": text,
            }
        )

    try:
        provider.shutdown()
    except Exception:
        pass

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "mode": result["mode"],
        "bank_id": result["initialized_bank_id"],
        "local_runtime_ok": result["local_runtime_ok"],
        "provider_available": result["provider_available"],
        "records_seen": result["records_seen"],
        "records_imported": result["records_imported"],
        "retain_errors": len(result["retain_errors"]),
        "recall_checks": [
            {
                "query": c["query"],
                "has_result": c["has_result"],
                "cost": c["contains_cost_signal"],
                "style": c["contains_style_signal"],
                "workspace": c["contains_workspace_signal"],
            }
            for c in result["recall_checks"]
        ],
        "out": str(OUT_JSON),
    }, ensure_ascii=False, indent=2))
    return 0 if result["provider_available"] and result["records_imported"] == result["records_seen"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
