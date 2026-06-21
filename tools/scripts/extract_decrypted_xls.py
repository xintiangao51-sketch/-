from pathlib import Path
import xlrd, re, json, traceback
ROOT=Path(r'D:/知识库')
OUT=ROOT/'08_项目案例库'/'劳务分包与扩大劳务报价'/'2026-劳务价格与鄯善启创案例'
SRC=OUT/'00_原始附件'/'企业级对下劳务分包单价汇总表2020xls_decrypted.xls'
TXT=OUT/'01_文本抽取'; TAB=OUT/'02_表格抽取'

def clean(v):
    if v is None: return ''
    return str(v).replace('\r\n','\n').replace('\r','\n').strip()
def esc(s): return clean(s).replace('|','\\|').replace('\n','<br>')
info={'file':str(SRC),'password':'2020','sheets':[]}
try:
    wb=xlrd.open_workbook(str(SRC), formatting_info=False, on_demand=True)
    for sh in wb.sheets():
        rec={'name':sh.name,'max_row':sh.nrows,'max_col':sh.ncols,'nonempty_rows':0}
        rows=[]
        for r in range(sh.nrows):
            vals=[clean(sh.cell_value(r,c)) for c in range(sh.ncols)]
            if any(vals):
                rec['nonempty_rows']+=1; rows.append(vals)
        info['sheets'].append(rec)
        safe=re.sub(r'[\\/:*?"<>|\s]+','_', sh.name)[:80]
        with open(TAB/f'企业级对下劳务分包单价汇总表2020xls__{safe}.tsv','w',encoding='utf-8-sig') as f:
            for vals in rows:
                f.write('\t'.join(vals).replace('\x00','')+'\n')
        maxr=min(len(rows),220); maxc=min(max((len(r) for r in rows), default=0),24)
        with open(TXT/f'企业级对下劳务分包单价汇总表2020xls__{safe}_preview.md','w',encoding='utf-8') as f:
            f.write(f'# 企业级对下劳务分包单价汇总表2020xls.xls / {sh.name}\n\n')
            f.write(f'- 解密密码：2020\n- used_rows: {sh.nrows}\n- used_cols: {sh.ncols}\n- nonempty_rows: {rec["nonempty_rows"]}\n\n')
            if maxr and maxc:
                f.write('| '+' | '.join(f'C{i+1}' for i in range(maxc))+' |\n')
                f.write('| '+' | '.join(['---']*maxc)+' |\n')
                for vals in rows[:maxr]:
                    vals=(vals+['']*maxc)[:maxc]
                    f.write('| '+' | '.join(esc(v) for v in vals)+' |\n')
    wb.release_resources(); info['status']='ok'
except Exception as e:
    info['status']='error'; info['error']=repr(e); info['traceback']=traceback.format_exc()
print(json.dumps(info,ensure_ascii=False,indent=2))
(OUT/'encrypted_xls_extract_log.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
