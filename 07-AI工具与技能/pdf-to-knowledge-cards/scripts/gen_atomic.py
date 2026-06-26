import json
from pathlib import Path
from datetime import datetime

base = Path(r'D:\知识库\99-原子知识库')
idx = json.loads((base / 'index.json').read_text(encoding='utf-8-sig'))  # 处理BOM

print('当前原子库状态:')
for k, v in idx['categories'].items():
    print(f'  {k}: {v["count"]}条')

methods_to_add = [
    {"id":"M-2026-008","type":"method","content":"基于资源的成本估算方法（Resource-Based Estimating）：将工程分解为'材料+人工+机械+管理费+利润'五元组，按资源数据库逐项计算后求和。优势：透明度高、可追溯、便于敏感性分析；劣势：依赖完整资源数据库","tags":["成本估算","资源法","DDC","V部分"],"source":"DDC_2ndEdition_Chinese.pdf p235-243 章5.1.3-5.1.5","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_V_5_1_3_基于资源的成本计算方法.md","notes":"DDC核心方法论，与新疆2020定额'量价分离'思路有相似但工具链不同"},
    {"id":"M-2026-009","type":"method","content":"QTO（Quantity Take-Off）按属性分组法：从CAD/BIM模型按'构件类型+材料+尺寸+楼层'等多维度属性分组，自动汇总工程量清单。Excel规则分组是入门实现，LLM+结构化数据可实现智能化","tags":["QTO","工程量清单","BIM","DDC","V部分"],"source":"DDC_2ndEdition_Chinese.pdf p251-269 章5.2.3-5.2.5","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_V_5_2_3_QTO工程量清单_按属性分组.md","notes":"造价AI化的核心路径，需结合国内清单计价规范(G50500-2024)调整"},
    {"id":"M-2026-010","type":"method","content":"4D-8D建模扩展体系：4D=3D+时间（进度）、5D=4D+成本（造价）、6D=5D+可持续性/能耗、7D=6D+运维、8D=7D+拆除/安全。覆盖建筑全生命周期数据集成","tags":["4D","5D","6D","BIM","DDC","V部分"],"source":"DDC_2ndEdition_Chinese.pdf p269-280 章5.3.1-5.3.3","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_V_5_3_3_6D-8D扩展属性层.md","notes":"BIM进阶概念，国内主要应用4D-5D，6D-8D实践少"},
    {"id":"M-2026-011","type":"method","content":"LLM+结构化数据的QTO自动化：从PDF图纸/CAD文件中提取构件信息→LLM语义解析→映射到结构化schema→自动汇总工程量。三步：①图纸OCR/解析 ②LLM实体抽取 ③规则汇总","tags":["LLM","QTO","AI造价","DDC","V部分"],"source":"DDC_2ndEdition_Chinese.pdf p258-262 章5.2.4","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_V_5_2_4_使用LLM和结构化数据的QTO自动化.md","notes":"AI造价落地路径，依赖图纸质量+LLM精度，目前仅适合辅助而非全自动"},
    {"id":"M-2026-012","type":"method","content":"CO2排放计算方法：从材料工程量×碳排放因子数据库（如ICE/Ecoinvent）→施工运输能耗→运营能耗→拆除回收，多阶段累加。书中给出基于BIM自动提取+碳因子库的完整计算流程","tags":["CO2","碳排放","ESG","DDC","V部分"],"source":"DDC_2ndEdition_Chinese.pdf p275-280 章5.3.4","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_V_5_3_4_CO2排放量计算.md","notes":"ESG新方向，国内2024版清单计价标准暂未强制要求"},
]

insights_to_add = [
    {"id":"I-2026-001","type":"insight","content":"DDC洞察：建筑业'数据爆炸但知识贫乏'的根本原因——90%数据被困在专有格式/孤立系统中（CAD孤岛、ERP孤岛、PMIS孤岛），无法互操作。解决路径是开放格式（IFC/CSV/Parquet）+ ETL管道","tags":["数据孤岛","开放格式","DDC","II部分"],"source":"DDC_2ndEdition_Chinese.pdf p61-88 II部分","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_II_数据孤岛.md","notes":"宏观洞察，适用于国内造价行业的同样问题（广联达/鲁班/品茗数据互不兼容）"},
    {"id":"I-2026-002","type":"insight","content":"DDC洞察：HiPPO（Highest Paid Person's Opinion）决策风险——大数据时代仍凭'高管拍脑袋'决策是数据孤岛的另一面。打破路径：①数据可视化②决策记录可追溯③A/B测试文化","tags":["决策风险","数据驱动","DDC","II部分"],"source":"DDC_2ndEdition_Chinese.pdf p70-73 章2.1.4","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_II_数据孤岛.md","notes":"管理学洞察，造价行业的'专家经验'也面临同样问题"},
    {"id":"I-2026-003","type":"insight","content":"DDC洞察：封闭格式（专有CAD格式）阻碍互操作性，IFC/CSV/Parquet等开放格式+开源软件（如Blender、FreeCAD、BIMserver）是未来。CAD-BIM的'30年生命周期'预言值得警惕","tags":["开放格式","BIM未来","DDC","VI部分"],"source":"DDC_2ndEdition_Chinese.pdf p295-349 VI部分","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_VI_BIM生态.md","notes":"趋势性洞察，国内Revit主导现状短期内难改"},
]

tools_to_add = [
    {"id":"T-2026-005","type":"tool","content":"Python+Pandas处理造价表格数据：pd.read_excel读取广联达/Excel导出→DataFrame分组聚合→输出CSV。优势：批量处理+可复用+可审计","tags":["Python","Pandas","造价数据","DDC"],"source":"DDC_2ndEdition_Chinese.pdf p152-156 章3.4.2","confidence":"A","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_III_数据分类+LLM.md","notes":"鼎梁筑工作台已在用的工具，可立即落地"},
    {"id":"T-2026-006","type":"tool","content":"Apache Airflow调度ETL管道：用于造价数据定时抽取（图纸/清单/价格）→转换（格式标准化）→加载（数据库/数据仓库）。DAG模式可视化","tags":["Airflow","ETL","调度","DDC"],"source":"DDC_2ndEdition_Chinese.pdf p361-371 主题索引 + VII部分","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_VII_决策自动化.md","notes":"数据工程工具，对单机造价工作可能过重，但适合多项目并行"},
    {"id":"T-2026-007","type":"tool","content":"Apache Parquet列存格式：相比CSV/Excel在数据分析时快10-100倍，适合造价大数据集（多年历史项目+多地区价格）。可与Pandas无缝集成","tags":["Parquet","列存","性能","DDC"],"source":"DDC_2ndEdition_Chinese.pdf 主题索引（机器翻译为'镶木地板'）","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/keywords/en_keywords.json","notes":"数据格式，翻译瑕疵：'阿帕奇镶木地板'实为'Apache Parquet'"},
    {"id":"T-2026-008","type":"tool","content":"PyMuPDF（fitz）PDF解析：相比pdfplumber更快，支持中文+表格+图像。本知识库已验证：574页DDC PDF 5分钟提取全文+TOC+页码定位","tags":["PDF","解析","Python","工具"],"source":"鼎梁筑实测（DDC解析项目）","confidence":"A","card_ref":"本任务执行记录","notes":"已验证可用，建议加入鼎梁筑标准工具链"},
    {"id":"T-2026-009","type":"tool","content":"IFC（Industry Foundation Classes）开放BIM格式：跨CAD软件数据交换（Revit↔Archicad↔Bentley）。但书中警告：IFC转换仍受几何内核影响，复杂模型有损","tags":["IFC","BIM","开放格式","DDC"],"source":"DDC_2ndEdition_Chinese.pdf p301-306 章6.1.3","confidence":"B","card_ref":"06-参考文档/DDC数字驱动建设/cards/card_VI_BIM生态.md","notes":"BIM工具，实际项目中有几何/属性丢失风险"},
]

created_at = datetime.now().strftime('%Y-%m-%d')
for m in methods_to_add: m.update({'created':created_at,'last_used':None,'use_count':0})
for ins in insights_to_add: ins.update({'created':created_at,'last_used':None,'use_count':0})
for t in tools_to_add: t.update({'created':created_at,'last_used':None,'use_count':0})

with open(base / 'methods.jsonl', 'a', encoding='utf-8') as f:
    for m in methods_to_add: f.write(json.dumps(m, ensure_ascii=False) + '\n')
with open(base / 'insights.jsonl', 'a', encoding='utf-8') as f:
    for ins in insights_to_add: f.write(json.dumps(ins, ensure_ascii=False) + '\n')
with open(base / 'tools.jsonl', 'a', encoding='utf-8') as f:
    for t in tools_to_add: f.write(json.dumps(t, ensure_ascii=False) + '\n')

idx['categories']['methods']['count'] += len(methods_to_add)
idx['categories']['insights']['count'] += len(insights_to_add)
idx['categories']['tools']['count'] += len(tools_to_add)
idx['last_updated'] = created_at
# 保持BOM避免破坏Windows编辑器
(base / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding='utf-8-sig')

print(f'\n写入完成:')
print(f'  +{len(methods_to_add)} methods')
print(f'  +{len(insights_to_add)} insights')
print(f'  +{len(tools_to_add)} tools')
print(f'\n更新后状态:')
for k, v in idx['categories'].items():
    print(f'  {k}: {v["count"]}条')