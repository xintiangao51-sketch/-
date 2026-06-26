import re

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

# Find ConfigTable occurrences with context
for i, match in enumerate(re.finditer(r'ConfigTable', html)):
    start = max(0, match.start() - 200)
    end = min(len(html), match.end() + 2000)
    print(f"\n=== ConfigTable occurrence {i+1} (chars {match.start()}-{match.end()}) ===")
    print(html[start:end])
    print("---")
