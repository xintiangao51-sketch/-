import re
from urllib.parse import unquote
import html

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the HTML part
html_match = re.search(r'"text":\s*"(.+)"\s*\}?$', content, re.DOTALL)
html = html_match.group(1).encode().decode('unicode_escape')

# Find all ConfigTable occurrences with full surrounding context
for i, match in enumerate(re.finditer(r'ConfigTable', html)):
    start = match.start()
    end = min(len(html), start + 100)
    print(f"\n=== Occurrence {i+1} at char {start} ===")
    # Extract the astro-island element containing this ConfigTable
    # Go backwards to find the opening <astro-island
    search_start = max(0, start - 300)
    search_end = min(len(html), start + 300)
    chunk = html[search_start:search_end]
    print(chunk)
    print()

# Now let's find the actual props in the HTML more carefully
# They are HTML attributes on astro-island elements
print("\n\n=== Searching for props= attributes in astro-island ===")
# Find all astro-island elements
island_pattern = r'<astro-island[^>]+>'
islands = re.findall(island_pattern, html)
print(f"Found {len(islands)} astro-island elements")
for idx, island in enumerate(islands):
    if 'ConfigTable' in island:
        props_match = re.search(r'props=\\?"([^"]+)\\"', island)
        if props_match:
            raw = props_match.group(1)
            print(f"\n--- Island {idx+1} ---")
            print(f"Raw props length: {len(raw)}")
            print(f"Raw props first 300: {raw[:300]}")
            print(f"Raw props last 100: {raw[-100:]}")
