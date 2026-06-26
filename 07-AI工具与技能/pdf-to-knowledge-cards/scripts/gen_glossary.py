"""
DDC翻译瑕疵词典 v2 - 修复字符串转义
"""
import re, json
from pathlib import Path
from datetime import datetime

base = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设\raw')

glossary_fixes = [
    {"src":"友邦保险公司","std":"AIA","std_zh":"美国建筑师学会","context":"建筑标准/合同模板","page":"289","note":"书中AIA=American Institute of Architects，机器误译为保险公司"},
    {"src":"国际出版商协会","std":"IPA","std_zh":"IPA（信息发布协议）","context":"标准/协议","page":"54,94,95,97,109","note":"International Publisher Association 或 Information Protocol Architecture"},
    {"src":"克劳德","std":"Claude","std_zh":"Anthropic Claude AI","context":"LLM章节","page":"20","note":"AI模型名，不应中文化"},
    {"src":"阿帕奇气流","std":"Apache Airflow","std_zh":"Apache Airflow任务调度","context":"ETL/工作流","page":"311,361-371,399","note":"ETL调度工具，机器直译错误"},
    {"src":"Apache NiFi","std":"Apache NiFi","std_zh":"Apache NiFi数据流","context":"数据集成","page":"116,311,361-371","note":"数据流处理工具"},
    {"src":"阿帕奇 ORC","std":"Apache ORC","std_zh":"Apache ORC列存格式","context":"大数据格式","page":"62,330,378","note":"Optimized Row Columnar 列存优化"},
    {"src":"阿帕奇镶木地板","std":"Apache Parquet","std_zh":"Apache Parquet列存格式","context":"大数据格式","page":"62,67,380-381,494","note":"Parquet直译为镶木地板是机器翻译严重错误"},
    {"src":"黑匣子","std":"BlackBox","std_zh":"Pandas BlackBox构造函数","context":"Python Pandas","page":"240,242,243","note":"编程概念，非航空黑匣子"},
    {"src":"brep","std":"BREP","std_zh":"边界表示法","context":"CAD几何","page":"多个","note":"Boundary Representation"},
    {"src":"copxml","std":"CPIXML","std_zh":"CPIXML","context":"建筑数据交换","page":"多个","note":"待人工核对全文含义"},
    {"src":"虚化","std":"Blurring","std_zh":"模糊化","context":"图像处理","page":"320,337","note":"机器误译"},
    {"src":"炸弹","std":"BOM","std_zh":"物料清单","context":"BIM/产品数据","page":"76,77,79,257,263","note":"Bill of Materials，非爆炸物"},
    {"src":"资本支出","std":"CAPEX","std_zh":"资本性支出","context":"投资分析","page":"多个","note":"Capital Expenditure"},
    {"src":"CDE","std":"CDE","std_zh":"通用数据环境","context":"BIM数据","page":"多个","note":"Common Data Environment"},
    {"src":"副驾驶员","std":"Copilot","std_zh":"Copilot AI助手","context":"LLM辅助编程","page":"多个","note":"GitHub/Microsoft产品，不应直译"},
    {"src":"早晨","std":"AM","std_zh":"上午","context":"时间表达","page":"14,84,151,153","note":"AM/PM错译"},
]

md = []
md.append("# DDC 翻译瑕疵词典（完整版）")
md.append("")
md.append(f"> 数据源：06-参考文档/DDC数字驱动建设/raw/part19_术语表.txt + part21_主题索引.txt + 全文机器核对  ")
md.append(f"> 用途：辅助PDF阅读、关键词检索、知识库引用时还原正确术语  ")
md.append(f"> 生成方式：机器抽取+人工核对通道（B级证据）  ")
md.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
md.append(f"> 条目数：{len(glossary_fixes)}条")
md.append("")
md.append("## 一、术语对照表（按字母排序）")
md.append("")
md.append("| 书中译名 | 标准英文 | 标准中文 | 应用场景 | 出处页码 | 说明 |")
md.append("|----------|----------|----------|----------|----------|------|")
for item in glossary_fixes:
    md.append(f"| {item['src']} | **{item['std']}** | {item['std_zh']} | {item['context']} | {item['page']} | {item['note']} |")
md.append("")
md.append("## 二、原始术语表（part19）解析")
md.append("")
md.append("> 原始PDF术语表（p542-547）因排版断行，正则解析困难。建议用此词典替代。")
md.append("")
md.append("## 三、高频易混术语清单（按类分组）")
md.append("")
md.append("### 数据格式类")
md.append("- CSV（逗号分隔值） / Parquet（列存）/ ORC（列存优化）/ JSON（键值对）/ XML（标签）")
md.append("- DWG（AutoCAD原生）/ RVT（Revit原生）/ IFC（开放BIM）/ USD（通用场景描述）")
md.append("- Excel（.xlsx表格）/ DataFrame（内存数据表）/ Pandas（处理库）")
md.append("")
md.append("### 系统类")
md.append("- ERP（企业资源规划）/ PMIS（项目管理系统）/ BIM（建筑信息模型）/ CAD（计算机辅助设计）")
md.append("- QTO（工程量清单）/ BOQ（工程量清单英文）/ CWICR（施工工作项目成本资源）")
md.append("")
md.append("### AI/ML类")
md.append("- LLM（大语言模型）/ ML（机器学习）/ NLP（自然语言处理）/ RAG（检索增强生成）")
md.append("- ChatGPT / Claude / LlaMa / Mistral / DeepSeek / QWEN / Grok — 主流LLM产品名（不应中文化）")
md.append("")
md.append("### 数据处理工具类")
md.append("- Apache Airflow（任务调度）/ Apache NiFi（数据流）/ Apache Kafka（消息队列）")
md.append("- ETL（抽取-转换-加载）/ DataOps（数据运维）/ MLOps（机器学习运维）")
md.append("")
md.append("## 四、⚠待人工确认")
md.append("")
md.append("- [ ] CPIXML/copxml的完整含义")
md.append("- [ ] 是否将本词典同步写入 02-业务中台/ 业务术语表")
md.append("- [ ] 是否将常见术语（如LLM/IFC/Parquet）加入首页标签体系")
md.append("")
md.append("---")
md.append("")
md.append("**生成Agent**：Hermes（调度部 / 总监级）  ")
md.append("**证据等级**：B级（机器抽取，建议人工核对最后一列）")
md.append("")

out_path = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设\翻译瑕疵词典.md')
out_path.write_text('\n'.join(md), encoding='utf-8')
print(f'已生成: {out_path}')
print(f'条目数: {len(glossary_fixes)}')
print(f'大小: {out_path.stat().st_size:,} bytes')

# JSON版
json_path = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设\keywords\translation_glossary.json')
json_path.write_text(json.dumps(glossary_fixes, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'JSON版: {json_path}')