from pathlib import Path
import tomllib
import json

workspace = Path(r"D:/知识库")
repo = Path(r"C:/Users/20752/Documents/Codex/2026-06-14/gh-repo-clone-msitarzewski-agency-agents/agency-agents")
codex_home = Path(r"C:/Users/20752/.codex/agents")
required = [
    "zk-steward", "document-generator", "executive-summary-generator", "ui-designer", "ux-architect", "frontend-developer",
    "construction-cost-estimator-xinjiang", "construction-budget-specialist", "construction-finance-controller", "construction-legal-contract-reviewer", "construction-civil-engineer-cn", "construction-site-manager", "construction-quantity-surveyor",
    "workflow-architect", "bim-gis-specialist", "supply-chain-strategist", "project-manager-senior", "legal-compliance-checker", "analytics-reporter", "business-strategist", "operations-manager",
]
missing = []
invalid = []
summary = []
for slug in required:
    path = codex_home / f"{slug}.toml"
    if not path.exists():
        missing.append(slug)
        continue
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        ok = all(k in data and str(data[k]).strip() for k in ["name", "description", "developer_instructions"])
        if not ok:
            invalid.append(slug)
        summary.append({"slug": slug, "name": data.get("name"), "desc_len": len(data.get("description", "")), "inst_len": len(data.get("developer_instructions", ""))})
    except Exception as e:
        invalid.append(f"{slug}: {e}")

checks = {
    "soul_exists": (workspace / "soul.md").exists(),
    "library_readme_exists": (workspace / "agent-role-templates" / "README.md").exists(),
    "repo_exists": repo.exists(),
    "codex_agents_total": len(list(codex_home.glob("*.toml"))),
    "required_count": len(required),
    "missing": missing,
    "invalid": invalid,
    "checked": summary,
}
print(json.dumps(checks, ensure_ascii=False, indent=2))
