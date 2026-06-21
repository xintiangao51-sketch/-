import re
from urllib.parse import unquote
import html

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

# Find all ConfigTable props - they are in astro-island elements with URL-encoded JSON
# The props are in the format: props="{...URL-encoded JSON...}"
props_pattern = r'props=\\"([^"]+)\\"'
matches = re.findall(props_pattern, html)
print(f"Found {len(matches)} ConfigTable props blocks")

all_keys = []
for idx, raw_props in enumerate(matches):
    try:
        # URL decode the props
        decoded = unquote(raw_props)
        # Parse the JSON (it's encoded as HTML attributes)
        # The format is: {"options":[1,[[0,{...}],[0,{...}],...]]}
        # We need to extract key, type, description, default from each inner object

        # Find all individual entry blocks: [0,{...}]
        entry_pattern = r'\[0,\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\]'

        # Simpler: find all "key":[0,"value"] patterns within each props block
        key_pat = r'"key":\s*\[\s*0\s*,\s*"([^"]*)"'
        type_pat = r'"type":\s*\[\s*0\s*,\s*"([^"]*)"'
        desc_pat = r'"description":\s*\[\s*0\s*,\s*"([^"]*)"'
        def_pat = r'"default":\s*\[\s*0\s*,\s*"([^"]*)"'

        keys = re.findall(key_pat, decoded)
        types = re.findall(type_pat, decoded)
        descs = re.findall(desc_pat, decoded)
        defs = re.findall(def_pat, decoded)

        print(f"\n--- Props block {idx+1}: {len(keys)} entries ---")
        for i, k in enumerate(keys):
            t = types[i] if i < len(types) else ""
            d = descs[i] if i < len(descs) else ""
            dv = defs[i] if i < len(defs) else ""
            # Unescape HTML entities
            d = html.unescape(d)
            dv = html.unescape(dv)
            all_keys.append((k, t, d, dv))
            print(f"  KEY: {k}")
            print(f"  TYPE: {t}")
            print(f"  DESC: {d[:100]}{'...' if len(d)>100 else ''}")
            print(f"  DEFAULT: {dv[:100]}{'...' if len(dv)>100 else ''}")
            print()

    except Exception as e:
        print(f"Error parsing block {idx+1}: {e}")

print(f"\n\n=== TOTAL: {len(all_keys)} config keys found ===")
