import re
from urllib.parse import unquote
import html
import json

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

data = json.loads(content)
html_text = data[0]['text']

# The JSON props in HTML attributes are escaped as:
# props="{&quot;options&quot;:[1,[[0,{&quot;key&quot;:[0,&quot;value&quot;]},...]]]}"

def unescape_html_attr(s):
    return s.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

def parse_configtable_props(props_str):
    """Parse the ConfigTable JSON props format."""
    # The format is: {"options":[1,[[0,{entry}],[0,{entry}],...]]}
    # Each entry has: key, type, description, default (all as [0, value] pairs)
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

# Find all ConfigTable occurrences and extract their props
# They are inside astro-island elements
all_entries = {}

# Pattern to find astro-island elements containing ConfigTable
island_pattern = r'<astro-island[^>]*component-export="ConfigTable"[^>]*props="([^"]+)"[^>]*>'

matches = re.findall(island_pattern, html_text)
print(f"Found {len(matches)} ConfigTable astro-island elements\n")

for idx, raw_props in enumerate(matches):
    try:
        unescaped = unescape_html_attr(raw_props)
        entries = parse_configtable_props(unescaped)
        print(f"Block {idx+1}: {len(entries)} entries")
        for e in entries:
            if e['key']:
                all_entries[e['key']] = e
    except Exception as e:
        print(f"Block {idx+1}: Error processing: {e}")

# Also check for props before the component-export
island_pattern2 = r'<astro-island[^>]*props="([^"]+)"[^>]*component-export="ConfigTable"[^>]*>'
matches2 = re.findall(island_pattern2, html_text)
print(f"Found {len(matches2)} more ConfigTable astro-island elements (props before export)")

for idx, raw_props in enumerate(matches2):
    try:
        unescaped = unescape_html_attr(raw_props)
        entries = parse_configtable_props(unescaped)
        print(f"Block {idx+1} (alt): {len(entries)} entries")
        for e in entries:
            if e['key']:
                all_entries[e['key']] = e
    except Exception as e:
        print(f"Block {idx+1} (alt): Error processing: {e}")

# Also search for props in the raw HTML that might not match the island pattern
# Look for all props= that contain "key"
print(f"\nSearching for all props containing 'key'...")
props_blocks = re.findall(r'props="({[^}]{20,})"', html_text)
for idx, raw in enumerate(props_blocks):
    if '"key"' in raw and '"type"' in raw:
        try:
            unescaped = unescape_html_attr(raw)
            entries = parse_configtable_props(unescaped)
            if entries:
                print(f"  Extra block {idx+1}: {len(entries)} entries")
                for e in entries:
                    if e['key']:
                        all_entries[e['key']] = e
        except:
            pass

print(f"\n\n=== TOTAL UNIQUE CONFIG KEYS: {len(all_entries)} ===\n")
for key in sorted(all_entries.keys()):
    e = all_entries[key]
    print(f"KEY: {e['key']}")
    print(f"TYPE: {e['type']}")
    print(f"DESCRIPTION: {e['description']}")
    print(f"DEFAULT: {e['default']}")
    print()
