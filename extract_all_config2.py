import re
from urllib.parse import unquote
import html
import json

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the HTML part (strip the JSON wrapper)
html_match = re.search(r'"text":\s*"(.+)"\s*\}?$', content, re.DOTALL)
if html_match:
    html = html_match.group(1)
    # Unescape JSON string
    html = html.encode().decode('unicode_escape')
else:
    html = content

print(f"HTML length: {len(html)}")

# Find all ConfigTable props - they are in astro-island elements
# The props are in the format: props="{...URL-encoded JSON...}"
props_pattern = r'props=\\"([^"]+)\\"'
matches = re.findall(props_pattern, html)
print(f"Found {len(matches)} ConfigTable props blocks")

all_entries = []

for idx, raw_props in enumerate(matches):
    try:
        # URL decode the props
        decoded = unquote(raw_props)
        # The JSON has been escaped for HTML attributes - need to unescape quotes
        # It's like: {&quot;options&quot;:[1,...]}
        decoded = decoded.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        # Parse as JSON
        data = json.loads(decoded)
        # Structure: {"options":[1,[[0,{key,type,description,default}], [0,{...}], ...]]}
        entries = data.get("options", [[]])[1] if len(data.get("options", [])) > 1 else []

        for entry_wrapper in entries:
            if isinstance(entry_wrapper, list) and len(entry_wrapper) >= 2:
                entry = entry_wrapper[1]
                key = entry.get("key", [""])[1] if isinstance(entry.get("key"), list) else entry.get("key", "")
                typ = entry.get("type", [""])[1] if isinstance(entry.get("type"), list) else entry.get("type", "")
                desc = entry.get("description", [""])[1] if isinstance(entry.get("description"), list) else entry.get("description", "")
                default = entry.get("default", [""])[1] if isinstance(entry.get("default"), list) else entry.get("default", "")

                all_entries.append({
                    "key": key,
                    "type": typ,
                    "description": desc,
                    "default": default
                })

        print(f"  Block {idx+1}: parsed {len(entries)} entries")

    except json.JSONDecodeError as e:
        print(f"  Block {idx+1}: JSON parse error: {e}")
        # Try to debug
        print(f"    First 200 chars: {raw_props[:200]}")
    except Exception as e:
        print(f"  Block {idx+1}: Error: {e}")

print(f"\n\n=== TOTAL: {len(all_entries)} config keys found ===\n")
for e in all_entries:
    print(f"KEY: {e['key']}")
    print(f"TYPE: {e['type']}")
    print(f"DESCRIPTION: {e['description']}")
    print(f"DEFAULT: {e['default']}")
    print()
