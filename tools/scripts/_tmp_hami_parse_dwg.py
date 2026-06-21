import os, re, json, csv, time, subprocess, sys
from pathlib import Path
from collections import Counter, defaultdict

root = Path(r'D:/知识库/09-项目资料/哈密国源综合服务中心')
if not root.exists() or not any(root.rglob('*.dwg')):
    root = Path(r'C:/Users/20752/Desktop/哈密国源综合服务中心项目/5-7国源电力哈密煤电公司综合能源集控服务中心工程施工公开招标/招标文件/附件/工程量清单、项目招标图纸等/国网能源哈密煤电有限公司综合能源集控服务中心项目（招标图）20260320')
if not root.exists():
    print(f"❌ 路径不存在: {root}")
    print("请修改脚本中的 root 变量为实际路径")
    raise SystemExit(1)
print(f"✅ 扫描路径: {root}")
out_root = Path(r'D:/知识库/09-项目资料/哈密国源综合服务中心/原始附件扫描')
out_root.mkdir(parents=True, exist_ok=True)

keywords = ['图纸目录','设计说明','建筑面积','地上','地下','耐火','抗震','设防','框架','剪力墙','基础','筏板','桩','混凝土','钢筋','消火栓','喷淋','给水','排水','消防','水箱','水泵','空气源','热泵','风机','排烟','新风','空调','电梯','配电箱','低压','电缆','桥架','弱电','监控','停车场','充电桩','围墙','道路','室外','集控','调度','明珠','新能源']

# binary printable extraction: ascii + utf-16le Chinese-ish fragments
ascii_re = re.compile(rb'[\x20-\x7e]{4,}')
# Chinese UTF-16LE rough: sequences of printable ascii or CJK chars encoded little-endian, extract by decoding whole bytes ignoring errors at even offsets

def extract_texts(data):
    texts=[]
    for m in ascii_re.finditer(data):
        s=m.group().decode('latin1','ignore').strip()
        if len(s)>=4: texts.append(s)
    for off in [0,1]:
        try:
            dec=data[off:].decode('utf-16le','ignore')
        except Exception:
            continue
        # split on controls
        parts=re.split(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ufffd]+', dec)
        for s in parts:
            s=s.strip()
            # keep meaningful Chinese or CAD texts
            if len(s)>=2 and (re.search(r'[\u4e00-\u9fff]',s) or re.search(r'[A-Za-z]{3,}',s)):
                # trim very long garbage
                if len(s)>300: s=s[:300]
                texts.append(s)
    # normalize, filter obvious binary garbage
    norm=[]; seen=set()
    for s in texts:
        s=re.sub(r'\s+',' ',s).strip()
        if len(s)<2: continue
        # ratio readable
        cjk=len(re.findall(r'[\u4e00-\u9fff]',s)); alnum=len(re.findall(r'[A-Za-z0-9]',s))
        if cjk==0 and alnum<4: continue
        if s not in seen:
            seen.add(s); norm.append(s)
    return norm

records=[]
all_keywords=[]
for p in sorted(root.rglob('*.dwg')):
    rel=str(p.relative_to(root)).replace('\\','/')
    data=p.read_bytes()
    header=data[:64].decode('latin1','ignore')
    texts=extract_texts(data)
    hit_counts={k:0 for k in keywords}
    hit_samples=[]
    for t in texts:
        for k in keywords:
            if k.lower() in t.lower():
                hit_counts[k]+=1
                if len(hit_samples)<80:
                    hit_samples.append(t)
    nonzero={k:v for k,v in hit_counts.items() if v}
    # likely title/date/version from filename/path and text samples
    professional=p.parent.name
    rec={
        '专业':professional,
        '文件名':p.name,
        '相对路径':rel,
        '大小MB':round(p.stat().st_size/1024/1024,2),
        '修改时间':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p.stat().st_mtime)),
        'DWG版本头':header[:12],
        '可提取文本片段数':len(texts),
        '关键词命中':'; '.join(f'{k}:{v}' for k,v in nonzero.items()),
        '样本文本': ' || '.join(hit_samples[:20])
    }
    records.append(rec)
    (out_root / f"dwg_text_{professional}_{p.stem[:50]}.txt").write_text('\n'.join(texts[:5000]), encoding='utf-8', errors='ignore')

# CSV/JSON
(out_root/'dwg_parse_summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
with (out_root/'dwg_parse_summary.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(records[0].keys()) if records else [])
    if records: w.writeheader(); w.writerows(records)
# XLSX
try:
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title='DWG图纸批量解析'
    headers=list(records[0].keys()) if records else []
    ws.append(headers)
    for r in records: ws.append([r.get(h,'') for h in headers])
    for col in ws.columns:
        letter=col[0].column_letter
        ws.column_dimensions[letter].width=min(max(12,max(len(str(c.value or '')) for c in col[:100])+2),80)
    wb.save(out_root/'哈密国源预审图纸DWG批量解析.xlsx')
except Exception as e:
    print('XLSX_WRITE_ERROR',e)
# markdown
md=[]
md.append('# 哈密国源预审图纸DWG批量解析报告\n\n')
md.append(f'- 图纸根路径：`{root}`\n')
md.append(f'- DWG文件数：{len(records)}\n')
md.append('- 说明：当前环境无 AutoCAD/ODA 转换器，已执行DWG二进制可读文本抽取；能识别版本头、文件体系、部分图内文字，不能替代CAD打开后的几何算量。\n\n')
md.append('## 专业统计\n\n| 专业 | 张数 |\n|---|---:|\n')
for k,v in Counter(r['专业'] for r in records).items(): md.append(f'| {k} | {v} |\n')
md.append('\n## 图纸文件与关键词命中\n\n| 序号 | 专业 | 图纸 | 大小MB | DWG版本 | 文本片段 | 关键词命中摘要 |\n|---:|---|---|---:|---|---:|---|\n')
for i,r in enumerate(records,1):
    md.append(f"| {i} | {r['专业']} | `{r['文件名']}` | {r['大小MB']} | {r['DWG版本头']} | {r['可提取文本片段数']} | {r['关键词命中'][:180]} |\n")
md.append('\n## 解析限制与下一步\n\n')
md.append('- 若需提取轴网尺寸、构件工程量、设备表完整内容，需要安装 AutoCAD/浩辰/ODA File Converter 将DWG批量转PDF/DXF，再做OCR/矢量解析。\n')
md.append('- 本次已把每张DWG可读文本导出为 `dwg_text_*.txt`，可用于快速检索图纸说明和设备关键词。\n')
(out_root/'预审图纸DWG批量解析报告.md').write_text(''.join(md),encoding='utf-8')
print('DWG_FILES',len(records))
for r in records:
    print(r['专业'], r['文件名'], r['大小MB'], r['DWG版本头'], r['可提取文本片段数'], r['关键词命中'][:120])
print('REPORT', out_root/'哈密国源预审图纸DWG批量解析.xlsx')
