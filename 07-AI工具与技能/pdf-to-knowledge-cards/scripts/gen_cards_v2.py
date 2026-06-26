"""
知识卡片生成器 v2 - 修复文件索引bug，强制两位数
"""
import re, json
from pathlib import Path
from datetime import datetime

base = Path(r'D:\知识库\00-工作台\inbox\ddc_extract')
out_dir = Path(r'D:\知识库\00-工作台\inbox\ddc_cards')
out_dir.mkdir(exist_ok=True)

PARTS = [
    {"id":"I","title_zh":"从泥板到数字革命：信息如何在建筑业中演变","pages":"34-60","theme":"历史演进","core_concept":"信息载体从泥板→纸张→数字"},
    {"id":"II","title_zh":"建筑业如何淹没在混乱的数据中","pages":"61-88","theme":"数据孤岛","core_concept":"HiPPO、数据质量、业务流程断点"},
    {"id":"III","title_zh":"建筑业务流程中的数据框架","pages":"89-160","theme":"数据分类+LLM","core_concept":"结构化/非结构化数据、LLM、RAG"},
    {"id":"IV","title_zh":"数据质量：组织、结构化、建模","pages":"161-231","theme":"数据治理","core_concept":"分类法、数据模型、RegEx验证"},
    {"id":"V","title_zh":"成本和时间计算：将数据纳入施工流程","pages":"232-294","theme":"造价与工期","core_concept":"QTO、BIM成本、ETL单价库、估算方法"},
    {"id":"VI","title_zh":"CAD和BIM：市场、现实和建筑设计数据的未来","pages":"295-349","theme":"BIM生态","core_concept":"IFC/DWG/RVT开放格式、CAD-BIM转换"},
    {"id":"VII","title_zh":"数据驱动决策、分析、自动化和机器学习","pages":"350-416","theme":"决策自动化","core_concept":"KPI、ETL管道、Airflow、ChatGPT分析"},
    {"id":"VIII","title_zh":"建筑数据的存储和管理","pages":"417-445","theme":"数据存储","core_concept":"DWH、Data Lake、Data Lakehouse"},
    {"id":"IX","title_zh":"大数据、机器学习和预测","pages":"446-497","theme":"大数据+ML","core_concept":"预测模型、k-NN、回归、AutoML"},
    {"id":"X","title_zh":"数字时代的建筑业：机遇与挑战","pages":"498-532","theme":"转型路径","core_concept":"数字成熟度、转型路线图"},
]

IDX_MAP = {'I':4,'II':5,'III':6,'IV':7,'V':8,'VI':9,'VII':10,'VIII':11,'IX':12,'X':13}

def get_part_file(part_id):
    files = sorted(base.glob('part*.txt'))
    target_name = f"part{IDX_MAP[part_id]:02d}_"
    for f in files:
        if f.name.startswith(target_name):
            return f
    raise FileNotFoundError(f'part file not found for {part_id} -> {target_name}')

def extract_summary(part_id):
    part_file = get_part_file(part_id)
    text = part_file.read_text(encoding='utf-8')
    text = re.sub(r'----- PAGE \d+ -----', ' ', text)
    text = re.sub(r'^# .+\n', '', text, flags=re.MULTILINE)
    paras = [p.strip() for p in re.split(r'\n{2,}', text) if len(p.strip()) > 80]
    head = paras[0][:400] if paras else ''
    middle = paras[len(paras)//3][:400] if len(paras) > 2 else (paras[-1][:400] if paras else '')
    end = paras[-1][:400] if len(paras) > 1 else ''
    return head, middle, end, paras[:8]

with open(Path(r'D:\知识库\00-工作台\inbox\ddc_keywords\zh_keywords.json'), encoding='utf-8') as f:
    zh_kw = json.load(f)
with open(Path(r'D:\知识库\00-工作台\inbox\ddc_keywords\en_keywords.json'), encoding='utf-8') as f:
    en_kw = json.load(f)

for part in PARTS:
    head, middle, end, paras = extract_summary(part['id'])
    pf = get_part_file(part['id'])
    md = []
    md.append(f'# 卡片 {part["id"]}：{part["title_zh"]}')
    md.append('')
    md.append(f'> **来源**：《DDC数字驱动建设》第二版（中文版）')
    md.append(f'> **部分**：{part["id"]}部分 / 页码 p{part["pages"]}')
    md.append(f'> **核心概念**：{part["core_concept"]}')
    md.append(f'> **主题分类**：{part["theme"]}')
    md.append(f'> **生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    md.append(f'> **证据等级**：B级（机器抽取摘要，需人工交叉验证后升A级）')
    md.append(f'> **抽取源文件**：`00-工作台/inbox/ddc_extract/{pf.name}`')
    md.append('')
    md.append('## 一、章节摘要')
    md.append('')
    md.append('**开篇导语**：')
    md.append(f'> {head}')
    md.append('')
    md.append('**中段核心**：')
    md.append(f'> {middle}')
    md.append('')
    md.append('**结尾展望**：')
    md.append(f'> {end}')
    md.append('')
    md.append('## 二、关键段落摘录（前8段）')
    md.append('')
    for i, p in enumerate(paras, 1):
        md.append(f'### 摘录 {i}')
        md.append(f'>{p[:500]}')
        md.append('')
    md.append('## 三、高频关键词（自动统计）')
    md.append('')
    md.append('**中文高频**：')
    for kw in zh_kw[:15]:
        md.append(f'- {kw["word"]} ({kw["count"]}次)')
    md.append('')
    md.append('**英文高频**：')
    for kw in en_kw[:15]:
        md.append(f'- {kw["word"]} ({kw["count"]}次)')
    md.append('')
    md.append('## 四、与其他部分的关系')
    md.append('')
    md.append('（待人工补充）')
    md.append('')
    md.append('## 五、⚠待人工确认')
    md.append('')
    md.append('- [ ] 摘要是否准确反映该部分核心思想')
    md.append('- [ ] 是否需要补充原文图表/数据点')
    md.append('- [ ] 与本知识库其他文档（造价核心/AI工具）的关联点')
    md.append('')
    md.append('---')
    md.append('')
    out_path = out_dir / f'card_{part["id"]}_{part["theme"]}.md'
    out_path.write_text('\n'.join(md), encoding='utf-8')
    print(f'  生成: {out_path.name}  ({out_path.stat().st_size:,} bytes)')

print('\nDONE v2. 10张部分级主题卡片（修复版）。')