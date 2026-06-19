from pathlib import Path
import json, re

repo = Path(r"C:/Users/20752/Documents/Codex/2026-06-14/gh-repo-clone-msitarzewski-agency-agents/agency-agents")
codex_repo_dir = repo / "integrations" / "codex" / "agents"
codex_home = Path(r"C:/Users/20752/.codex/agents")
opencode_repo_dir = repo / "integrations" / "opencode" / "agents"

items = {
    "legal-compliance-checker": repo / "support" / "support-legal-compliance-checker.md",
    "analytics-reporter": repo / "support" / "support-analytics-reporter.md",
    "business-strategist": repo / "specialized" / "business-strategist.md",
    "operations-manager": repo / "specialized" / "operations-manager.md",
    "project-manager-senior": repo / "project-management" / "project-manager-senior.md",
}

color_map = {"red":"#DC2626","teal":"#008080","indigo":"#4F46E5","blue":"#0066CC","gray":"#888888","green":"#2E7D32","orange":"#F97316","purple":"#7B2CBF"}

def parse_md(path):
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        fm = text[3:end].strip().splitlines()
        body = text[end+4:].lstrip()
    else:
        fm, body = [], text
    meta = {}
    for line in fm:
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body

created = []
for slug, path in items.items():
    meta, body = parse_md(path)
    name = meta.get("name", slug.replace("-", " ").title())
    description = meta.get("description", "")
    toml = "name = " + json.dumps(name, ensure_ascii=False) + "\n" + \
           "description = " + json.dumps(description, ensure_ascii=False) + "\n" + \
           "developer_instructions = " + json.dumps(body.strip() + "\n", ensure_ascii=False) + "\n"
    for dst in [codex_repo_dir / f"{slug}.toml", codex_home / f"{slug}.toml"]:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(toml, encoding="utf-8", newline="\n")
        created.append(str(dst))
    op = f"---\nname: {name}\ndescription: {description}\nmode: subagent\ncolor: \"{color_map.get(meta.get('color','gray'), '#888888')}\"\n---\n\n{body.strip()}\n"
    opencode_repo_dir.mkdir(parents=True, exist_ok=True)
    (opencode_repo_dir / f"{slug}.md").write_text(op, encoding="utf-8", newline="\n")
    created.append(str(opencode_repo_dir / f"{slug}.md"))

print(json.dumps({"created": created, "codex_home_count": len(list(codex_home.glob('*.toml')))}, ensure_ascii=False, indent=2))
