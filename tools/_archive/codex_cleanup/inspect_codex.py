import re

filepath = "/sessions/nifty-fervent-galileo/mnt/.claude/projects/C--Users-20752-AppData-Local-Claude-3p-local-agent-mode-sessions-0bdec786-00000000-local-28be0778-8a98-44cc-b06d-d2be71c8d263-outputs/b46d5483-d31e-499e-9c9a-286835099293/tool-results/call_function_8kk9vxjo4h2g_1.json"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Print first 5000 chars to understand structure
print("=== FIRST 5000 CHARS ===")
print(content[:5000])
print("\n=== SEARCHING FOR CONFIG-LIKE PATTERNS ===")

# Search for common patterns
patterns = ['model', 'config', 'key', 'ConfigTable', 'props', '{[0,"']
for p in patterns:
    count = content.count(p)
    print(f"'{p}' appears {count} times")

# Look for HTML script tags that might contain the data
script_matches = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"\nFound {len(script_matches)} script blocks")
for i, s in enumerate(script_matches[:3]):
    print(f"\n--- Script {i} (first 500 chars) ---")
    print(s[:500])
