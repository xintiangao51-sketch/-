import re, json, sys

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The ConfigTable component uses JSON props like:
# {"key":[0,"model_name"],"type":[0,"string"],"description":[0,"..."],"default":[0,"..."]}
# Let's extract all such entries

# First, find all JSON objects that contain "key" and look like ConfigTable entries
# Pattern: {"key":[0,"..."],"type":[0,"..."],"description":[0,"..."],"default":[0,"..."]}

# Find all distinct key values
key_pattern = r'"key":\s*\[\s*0\s*,\s*"([^"]+)"'
keys = re.findall(key_pattern, content)
print(f"Found {len(keys)} key occurrences")
for k in sorted(set(keys)):
    print(k)
