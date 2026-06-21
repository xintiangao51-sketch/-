import os, json, hashlib, time
from pathlib import Path

# ⚠ 原始路径可能不存在，请修改为实际的哈密项目文件路径
# 默认路径以当前知识库项目目录为准
root = Path(r'D:/知识库/09-项目资料/哈密国源综合服务中心')
if not root.exists():
    # 回退到桌面路径
    root = Path(r'C:/Users/20752/Desktop/哈密国源综合服务中心项目/5-7国源电力哈密煤电公司综合能源集控服务中心工程施工公开招标/招标文件/附件')

if not root.exists():
    print(f"❌ 路径不存在: {root}")
    print("请手动设置正确的哈密项目文件路径")
    print("用法: 修改脚本中的 root 变量")
    raise SystemExit(1)

out_root = Path(r'D:/知识库/09-项目资料/哈密国源综合服务中心/原始附件扫描')
records=[]
for p in root.rglob('*'):
    if p.is_file():
        try:
            st=p.stat()
        except Exception as e:
            continue
        rel=str(p.relative_to(root)).replace('\\','/')
        records.append({
            'rel':rel,
            'path':str(p),
            'suffix':p.suffix.lower(),
            'size':st.st_size,
            'mtime':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)),
            'parent':str(p.parent.relative_to(root)).replace('\\','/') if p.parent != root else '.',
        })
records.sort(key=lambda x:x['rel'])
# counts
from collections import Counter,defaultdict
cnt=Counter(r['suffix'] or '<none>' for r in records)
bydir=defaultdict(int)
for r in records: bydir[r['parent']]+=1
print('FILE_COUNT', len(records))
print('EXT_COUNTS')
for k,v in cnt.most_common(): print(k, v)
print('TOP_DIRS')
for k,v in sorted(bydir.items(), key=lambda kv:(kv[0]))[:200]: print(v, k)
# write json/csv/md
(out_root/'file_inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
with (out_root/'file_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
    import csv
    w=csv.DictWriter(f,fieldnames=['rel','suffix','size','mtime','parent','path'])
    w.writeheader(); w.writerows(records)
md=[]
md.append('# 哈密国源原始附件文件清单\n')
md.append(f'- 根路径：`{root}`\n')
md.append(f'- 文件总数：{len(records)}\n')
md.append('\n## 扩展名统计\n')
md.append('| 扩展名 | 数量 |\n|---|---:|\n')
for k,v in cnt.most_common(): md.append(f'| {k} | {v} |\n')
md.append('\n## 文件列表\n')
md.append('| 序号 | 相对路径 | 类型 | 大小KB | 修改时间 |\n|---:|---|---|---:|---|\n')
for i,r in enumerate(records,1): md.append(f"| {i} | `{r['rel']}` | {r['suffix']} | {r['size']/1024:.1f} | {r['mtime']} |\n")
(out_root/'file_inventory.md').write_text(''.join(md),encoding='utf-8')
print('OUT', out_root)
