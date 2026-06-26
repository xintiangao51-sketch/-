import fitz
from pathlib import Path

doc = fitz.open(Path(r'D:\知识库\06-参考文档\DDC_2ndEdition_Chinese.pdf'))
toc = doc.get_toc(simple=False)
print('=== V部分章节结构（p232-294）===')
for level, title, page, *rest in toc:
    if 232 <= page <= 294:
        if level == 2:
            print(f'L2 p{page}: {title}')
        elif level == 3:
            print(f'  L3 p{page}: {title}')

print()
print('=== III部分章节结构（p89-160, 含LLM）===')
for level, title, page, *rest in toc:
    if 89 <= page <= 160:
        if level == 2:
            print(f'L2 p{page}: {title}')
        elif level == 3:
            print(f'  L3 p{page}: {title}')

print()
print('=== VI部分章节结构（p295-349, BIM生态）===')
for level, title, page, *rest in toc:
    if 295 <= page <= 349:
        if level == 2:
            print(f'L2 p{page}: {title}')
        elif level == 3:
            print(f'  L3 p{page}: {title}')
doc.close()