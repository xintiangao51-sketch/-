import fitz, re
from pathlib import Path

pdf_path = Path(r'D:\知识库\06-参考文档\DDC_2ndEdition_Chinese.pdf')
out_dir = Path(r'D:\知识库\00-工作台\inbox\ddc_extract')
out_dir.mkdir(parents=True, exist_ok=True)

doc = fitz.open(pdf_path)
print(f'PAGES: {len(doc)}')

# 1) 整本转文本（带页码分隔符）
full_path = out_dir / 'ddc_fulltext.txt'
with open(full_path, 'w', encoding='utf-8') as f:
    f.write('# DDC 2nd Edition Chinese - Full Text Extract\n')
    f.write(f'# SOURCE: DDC_2ndEdition_Chinese.pdf\n')
    f.write(f'# TOTAL_PAGES: {len(doc)}\n\n')
    for i, page in enumerate(doc):
        f.write(f'\n\n===== PAGE {i+1} =====\n')
        f.write(page.get_text('text'))
print(f'FULL TEXT: {full_path} ({full_path.stat().st_size:,} bytes)')

# 2) 按L1部分切片
toc = doc.get_toc(simple=False)
# 抓出所有L1的页码位置
l1_pages = [(title, page-1) for level, title, page, *r in toc if level == 1]
# 加上末尾哨兵
end_page = len(doc)
l1_with_end = []
for idx, (title, page) in enumerate(l1_pages):
    next_page = l1_pages[idx+1][1] if idx+1 < len(l1_pages) else end_page
    l1_with_end.append((title, page, next_page))

print('\nPARTS TO SLICE:')
for title, s, e in l1_with_end:
    print(f'  p{s+1}-p{e}  {title}')

for idx, (title, s, e) in enumerate(l1_with_end, 1):
    safe = re.sub(r'[^\w\-_\.]', '_', title).strip('_')[:60]
    part_path = out_dir / f'part{idx:02d}_{safe}.txt'
    with open(part_path, 'w', encoding='utf-8') as f:
        f.write(f'# {title}\n')
        f.write(f'# PAGES: {s+1} - {e}\n\n')
        for p in range(s, e):
            f.write(f'\n----- PAGE {p+1} -----\n')
            f.write(doc[p].get_text('text'))
    size = part_path.stat().st_size
    print(f'  -> {part_path.name}  ({size:,} bytes)')

doc.close()
print('\nDONE.')
