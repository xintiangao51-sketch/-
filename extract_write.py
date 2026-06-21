import re
from urllib.parse import unquote
import html
import json

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

data = json.loads(content)
html_text = data[0]['text']

def unescape_html_attr(s):
    return s.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

def parse_configtable_props(props_str):
    entries = []
    try:
        data = json.loads(props_str)
        options = data.get("options", [])
        if len(options) >= 2 and isinstance(options[1], list):
            for item in options[1]:
                if isinstance(item, list) and len(item) >= 2:
                    entry_wrapper = item[1]
                    if isinstance(entry_wrapper, dict):
                        def extract_val(d, key):
                            v = d.get(key)
                            if isinstance(v, list) and len(v) >= 2:
                                return html.unescape(str(v[1]))
                            return ""
                        entries.append({
                            "key": extract_val(entry_wrapper, "key"),
                            "type": extract_val(entry_wrapper, "type"),
                            "description": extract_val(entry_wrapper, "description"),
                            "default": extract_val(entry_wrapper, "default"),
                        })
    except Exception as e:
        print(f"  Parse error: {e}")
    return entries

all_entries = {}

# Pattern to find astro-island elements containing ConfigTable
island_pattern = r'<astro-island[^>]*component-export="ConfigTable"[^>]*props="([^"]+)"[^>]*>'
matches = re.findall(island_pattern, html_text)

for idx, raw_props in enumerate(matches):
    unescaped = unescape_html_attr(raw_props)
    entries = parse_configtable_props(unescaped)
    for e in entries:
        if e['key']:
            all_entries[e['key']] = e

# Also check for props before the component-export
island_pattern2 = r'<astro-island[^>]*props="([^"]+)"[^>]*component-export="ConfigTable"[^>]*>'
matches2 = re.findall(island_pattern2, html_text)
for raw_props in matches2:
    unescaped = unescape_html_attr(raw_props)
    entries = parse_configtable_props(unescaped)
    for e in entries:
        if e['key']:
            all_entries[e['key']] = e

# Search for all props containing 'key'
props_blocks = re.findall(r'props="({[^}]{20,})"', html_text)
for raw in props_blocks:
    if '"key"' in raw and '"type"' in raw:
        try:
            unescaped = unescape_html_attr(raw)
            entries = parse_configtable_props(unescaped)
            for e in entries:
                if e['key']:
                    all_entries[e['key']] = e
        except:
            pass

output = []
for key in sorted(all_entries.keys()):
    e = all_entries[key]
    output.append({
        "key": e['key'],
        "type": e['type'],
        "description": e['description'],
        "default": e['default']
    })

with open('/sessions/nifty-fervent-galileo/mnt/知识库/codex_config_keys.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Written {len(output)} entries to codex_config_keys.json")
