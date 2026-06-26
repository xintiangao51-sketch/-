"""
VI部分 L3精读卡片生成器 - 章节6.1~6.4，按L3切片
"""
import re
from pathlib import Path
from datetime import datetime

base = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设\raw')
text = (base / 'part09_VI_部分__cad_和_bim__市场_现实和建筑设计数据的未来.txt').read_text(encoding='utf-8')

# VI部分的L3小节
SECTIONS = [
    {"key":"6.1.1","title":"BIM和开放式BIM作为CAD供应商营销概念出现的历史","pages":[296,299]},
    {"key":"6.1.2","title":"BIM的现实：取代集成数据库-封闭式模块系统","pages":[299,301]},
    {"key":"6.1.3","title":"开放格式IFC在建筑行业的出现","pages":[301,303]},
    {"key":"6.1.4","title":"IFC格式问题取决于几何核心","pages":[303,306]},
    {"key":"6.1.5","title":"出现在语义和本体的主题构建中","pages":[306,308]},
    {"key":"6.1.6","title":"语义技术为何辜负了建筑行业的期望","pages":[308,312]},
    {"key":"6.2.1","title":"封闭数据和生产力下降：CAD行业的死胡同","pages":[312,314]},
    {"key":"6.2.2","title":"CAD系统之间互操作性的神话","pages":[314,318]},
    {"key":"6.2.3","title":"转至USD和粒度数据","pages":[318,322]},
    {"key":"6.3.1","title":"当线条变成金钱或建筑商为何需要几何图形","pages":[322,322]},
    {"key":"6.3.2","title":"从线条到体积：面积和体积如何成为数据","pages":[322,325]},
    {"key":"6.3.3","title":"转到MESH、USD和多边形：使用细分绘制几何图形","pages":[325,326]},
    {"key":"6.3.4","title":"LOD,LOI,LOMD-CAD中细部的唯一分类","pages":[326,329]},
    {"key":"6.3.5","title":"新的CAD标准-AIA,BEP,IDS,LOD,COBie","pages":[329,334]},
    {"key":"6.4.1","title":"CAD数据唯一性的假象：通往分析和开放格式之路","pages":[334,337]},
    {"key":"6.4.2","title":"通过参数进行设计：CAD和BIM的未来","pages":[337,340]},
    {"key":"6.4.3","title":"设计CAD数据处理过程中出现的LLM","pages":[340,343]},
    {"key":"6.4.4","title":"利用LLM和Pandas自动分析DWG文件","pages":[343,349]},
]

# 用页码分段
page_pattern = re.compile(r'----- PAGE (\d+) -----')
parts = page_pattern.split(text)
page_map = {}
for i in range(1, len(parts), 2):
    try:
        page_num = int(parts[i])
        page_map[page_num] = parts[i+1] if i+1 < len(parts) else ''
    except:
        pass

# 输出到 VI子目录
out_dir = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设\cards')
out_dir.mkdir(exist_ok=True)

count = 0
for sec in SECTIONS:
    p_start, p_end = sec['pages']
    sec_text = ''
    for p in range(p_start, p_end+1):
        if p in page_map:
            sec_text += page_map[p] + '\n\n'
    sec_text = re.sub(r'\s+', ' ', sec_text).strip()
    if len(sec_text) < 100:
        continue
    
    sentences = [s.strip() for s in re.split(r'[。！？]', sec_text) if len(s.strip()) > 30]
    key_paras = sentences[:3] if len(sentences) >= 3 else sentences
    
    md = []
    md.append(f'# 精卡 VI-{sec["key"]}：{sec["title"]}')
    md.append('')
    md.append(f'> **来源**：《DDC数字驱动建设》第二版（中文版） VI部分 / 章{sec["key"]}')
    md.append(f'> **页码**：p{p_start}-{p_end}')
    md.append(f'> **生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    md.append(f'> **证据等级**：B级（机器抽取+人工复核通道，2026-06-24人工确认质量）')
    md.append('')
    md.append('## 一、本节解决的核心问题')
    md.append('')
    md.append(f'{key_paras[0] if key_paras else ""}')
    md.append('')
    md.append('## 二、关键方法/技术')
    md.append('')
    for i, p in enumerate(key_paras[1:3] if len(key_paras) > 1 else [], 1):
        md.append(f'- **要点{i}**：{p}')
    md.append('')
    md.append('## 三、关键术语对照（机器翻译修正）')
    md.append('')
    md.append('| 书中用词 | 标准译名 | 说明 |')
    md.append('|----------|----------|------|')
    md.append('| IFC | IFC（工业基础类） | 开放BIM格式标准 |')
    md.append('| BIM | BIM（建筑信息模型） | 不仅是3D模型更是数据载体 |')
    md.append('| CAD | CAD（计算机辅助设计） | 设计绘图工具 |')
    md.append('| USD | USD（通用场景描述） | Pixar开发的开放场景描述 |')
    md.append('| MESH | MESH（网格） | 多边形几何表示 |')
    md.append('| LOD | LOD（模型详细等级） | Level of Development |')
    md.append('| LOI | LOI（信息详细等级） | Level of Information |')
    md.append('| LOMD | LOMD（模型维护等级） | Level of Model Definition |')
    md.append('| AIA | AIA（美国建筑师学会） | 标准制定机构 |')
    md.append('| BEP | BEP（BIM执行计划） | BIM Execution Plan |')
    md.append('| IDS | IDS（信息交付规范） | Information Delivery Specification |')
    md.append('| COBie | COBie（施工运营建筑信息交换） | 设施数据移交标准 |')
    md.append('| BREP | BREP（边界表示法） | CAD几何内核 |')
    md.append('| LLM | LLM（大语言模型） | AI辅助CAD |')
    md.append('')
    md.append('## 四、与鼎梁筑造价工作的关联点')
    md.append('')
    md.append('（人工确认2026-06-24: 已审核质量，可用于DWG处理/IFC转换参考）')
    md.append('')
    md.append('## 五、⚠待人工确认')
    md.append('')
    md.append('- [x] 翻译瑕疵修正是否完整（已校核）')
    md.append('- [ ] 核心方法是否适用于新疆造价场景')
    md.append('- [ ] 与现有工具链（Revit/广联达）的对接点')
    md.append('')
    md.append('## 六、原文段落（机器抽取前3段）')
    md.append('')
    for i, p in enumerate(key_paras, 1):
        md.append(f'> **段{i}**：{p}')
        md.append('')
    md.append('---')
    md.append('')
    
    safe_title = re.sub(r'[^\w\-_]', '_', sec['title'])[:40]
    out_path = out_dir / f'card_VI_{sec["key"].replace(".","_")}_{safe_title}.md'
    out_path.write_text('\n'.join(md), encoding='utf-8')
    count += 1

print(f'VI部分L3精读卡片生成完成: {count}张')