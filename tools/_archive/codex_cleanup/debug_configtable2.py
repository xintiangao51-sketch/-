import re
from urllib.parse import unquote
import html

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)}")
print(f"First 200: {repr(content[:200])}")

# The file is a JSON array with a single object containing "type" and "text"
# Extract the text field
import json
data = json.loads(content)
html_text = data[0]['text']
print(f"\nHTML text length: {len(html_text)}")
print(f"HTML first 200: {repr(html_text[:200])}")

# Now search for ConfigTable
for i, match in enumerate(re.finditer(r'ConfigTable', html_text)):
    start = match.start()
    print(f"\n=== Occurrence {i+1} at char {start} ===")
    chunk = html_text[max(0,start-100):min(len(html_text),start+5000)]
    print(chunk)
    print()
    if i >= 2:
        break
