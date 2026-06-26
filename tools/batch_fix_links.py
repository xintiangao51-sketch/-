#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final batch fix for remaining broken links"""
import io, sys, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
VAULT = Path("D:/知识库")
IGN = {'.obsidian','.claude','.git','.tools','.skillhub-install','.claudian'}
cnt = 0
BS = chr(92)
for f in VAULT.rglob("*.md"):
    rel = str(f.relative_to(VAULT)).replace(BS, "/")
    if rel.split("/")[0] in IGN:
        continue
    c = f.read_text(encoding='utf-8')
    orig = c

    # 1. 精华摘要 nested paths
    pairs = [
        ("01-造价核心/变更索赔","变更索赔"),
        ("01-造价核心/定额与计价","定额与计价"),
        ("01-造价核心/工程量计算","工程量计算"),
        ("01-造价核心/材料价格","材料价格"),
        ("04-施工方案/安全管理","安全管理"),
        ("07-AI工具与技能/drawing-analyzer","drawing-analyzer"),
        ("07-AI工具与技能/md文档","md文档"),
        ("07-AI工具与技能/pdf","pdf"),
        ("07-AI工具与技能/提示词库","提示词库"),
    ]
    for d, sub in pairs:
        parent = d.split("/")[0]
        c = c.replace(f"[[{d}/{parent}/{sub}-总览]]", f"[[{d}/{sub}-总览|{sub}总览]]")

    # 2. Hermes 技能精华摘要 refs -> strip
    hp_dirs = [
        "07-AI工具与技能/Hermes配置/skills/ima-skill",
        "07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer",
        "07-AI工具与技能/Hermes配置/备份/skills/ima-skill",
        "07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer",
        "07-AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base",
        "07-AI工具与技能/Hermes配置/skills/ima-skill/notes",
        "07-AI工具与技能/Hermes配置/skills/ima-skill/notes/references",
        "07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references",
        "07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base",
        "07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes",
        "07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/references",
        "07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/references",
        "07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/references",
    ]
    for hp in hp_dirs:
        c = re.sub(rf'\[\[{re.escape(hp)}/.*?-总览\]\]', '<!-- _精华摘要 ref -->', c)

    # 3. 新疆工程审图专家 refs
    c = re.sub(
        r'\[\[07-AI工具与技能/Skills技能/新疆工程审图专家v1\.0\.0/.*?\]\]',
        '<!-- 审图专家 sub-ref -->', c
    )

    # 4. KC card name fixes in 案例总览
    base_kc = "12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片"
    kc_map_src = [
        "KC-劳务分包价格库-2026市政与企业对下指导价",
        "KC-劳务扩大报价分析方法论",
        "KC-劳务清包合同风险条款模板",
        "KC-建筑设备带人租赁税务定性",
        "KC-旋挖钻班组最终结算案例-田让存",
        "KC-鄯善启创劳务扩大报价案例复盘",
    ]
    for old_name in kc_map_src:
        c = c.replace(f"[[03_知识卡片/{old_name}", f"[[{base_kc}/{old_name}")

    # 5. 04_分析报告 relative refs
    base_a = "12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/04_分析报告"
    c = c.replace("[[04_分析报告/04_分析报告-总览]]", f"[[{base_a}/04_分析报告-总览|分析报告总览]]")
    c = c.replace("[[04_分析报告/劳务扩大报价准确性分析报告_2026-06-14]]",
                  f"[[{base_a}/劳务扩大报价准确性分析报告_2026-06-14|准确性分析报告]]")
    c = c.replace("[[../..-总览]]",
                  "[[12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/2026-劳务价格与鄯善启创案例-总览|案例总览]]")

    # 6. Dead file refs -> HTML comments
    dead_refs = {
        "[[07-AI工具与技能/md文档/新疆地区建设工程定额体系完整索引_2026-05-28.md]]": "<!-- 文件已删除: 定额体系完整索引 -->",
        "[[07-AI工具与技能/md文档/造价工作台搭建方案.md]]": "<!-- 文件已删除: 造价工作台搭建方案 -->",
        "[[07-AI工具与技能/md文档/AI工具与技能/md文档-总览]]": "<!-- _精华摘要 ref -->",
        "[[07-AI工具与技能/pdf/AI工具与技能/pdf-总览]]": "<!-- _精华摘要 ref -->",
        "[[07-AI工具与技能/提示词库/AI工具与技能/提示词库-总览]]": "<!-- _精华摘要 ref -->",
        "[[05-投标报价/报价策略/综合评估法报价策略]]": "<!-- 待创建: 综合评估法报价策略 -->",
        "[[05-投标报价/招标文件/招标文件关键信息提取模板]]": "<!-- 待创建: 招标文件关键信息提取模板 -->",
        "[[01-造价核心/定额与计价/独库69-72段200章逐项单价分析]]": "<!-- 待核实: 独库单价分析 -->",
        "[[01-造价核心/定额与计价/通衢隧道_单价分析表]]": "<!-- 待核实: 通衢隧道单价分析 -->",
        "[[01-造价核心/定额与计价/莎车县农村道路工程综合单价分析表]]": "<!-- 待核实: 莎车县道路单价分析 -->",
        "[[01-造价核心/定额与计价/乌市蓝天大厦玻璃幕墙专业劳务分包报价表（市场单价分析表）]]": "<!-- 待核实: 蓝天大厦玻璃幕墙报价 -->",
        "[[01-造价核心/定额与计价/乌市蓝天大厦铝单板幕墙专业劳务分包报价表（市场单价分析表）]]": "<!-- 待核实: 蓝天大厦铝单板幕墙报价 -->",
    }
    for old, new in dead_refs.items():
        c = c.replace(old, new)

    # 7. Excalidraw refs
    c = c.replace("[[Excalidraw/Drawing 2026-06-08 23.46.29.excalidraw.md]]",
                  "![[Excalidraw/Drawing 2026-06-08 23.46.29.excalidraw]]")
    c = c.replace("[[Excalidraw/Excalidraw-总览]]", "[[Excalidraw/Excalidraw-总览|Excalidraw]]")

    # 8. 哈密国源 sub-refs
    c = c.replace("[[09-项目资料/哈密国源综合服务中心/02-投标报价/澄清文件要点分析]]",
                  "[[09-项目资料/哈密国源综合服务中心/03-合同与履约/澄清文件核心要点|澄清文件核心要点]]")
    c = c.replace("[[09-项目资料/哈密国源综合服务中心/02-投标报价/施工组织设计框架分析]]",
                  "[[09-项目资料/哈密国源综合服务中心/01-招标文件/施工组织设计框架分析|施组框架分析]]")
    c = c.replace("[[05-投标报价/招标文件/投标报价全流程方法论]]",
                  "[[05-投标报价/投标报价-总览|投标报价总览]]")

    # 9. Trailing slash project refs
    c = c.replace("[[09-项目资料/阳安二线/]]", "[[09-项目资料/阳安二线/阳安二线-项目总览|阳安二线]]")
    c = c.replace("[[09-项目资料/道班房/]]", "[[09-项目资料/道班房|道班房]]")
    c = c.replace("[[09-项目资料/青河G331/]]", "[[09-项目资料/青河G331|青河G331]]")
    c = c.replace("[[09-项目资料/道班房/06-物资采购/]]", "[[09-项目资料/道班房|道班房]]")
    c = c.replace("[[09-项目资料/青河G331/06-物资采购/]]", "[[09-项目资料/青河G331|青河G331]]")

    # 10. 99-归档库 links (all exist on disk)
    archive_fixes = {
        "[[99-归档库/_00-整理中枢/新疆造价参数核验表_2026-06-14]]": "[[99-归档库/_00-整理中枢/新疆造价参数核验表_2026-06-14|参数核验表]]",
        "[[99-归档库/_00-整理中枢/D盘资料整理总览_2026-06-14]]": "[[99-归档库/_00-整理中枢/D盘资料整理总览_2026-06-14|D盘整理总览]]",
        "[[99-归档库/_00-整理中枢/老高造价上下文记忆]]": "[[99-归档库/_00-整理中枢/老高造价上下文记忆|上下文记忆]]",
        "[[99-归档库/_00-整理中枢/知识库整理规则]]": "[[99-归档库/_00-整理中枢/知识库整理规则|整理规则]]",
        "[[99-归档库/_00-整理中枢/重复候选清单_2026-06-14]]": "[[99-归档库/_00-整理中枢/重复候选清单_2026-06-14|重复候选]]",
        "[[99-归档库/_00-整理中枢/项目资料自动索引_2026-06-14]]": "[[99-归档库/_00-整理中枢/项目资料自动索引_2026-06-14|项目索引]]",
        "[[99-归档库]]": "[[99-归档库|归档库]]",
        "[[99-归档库/_造价知识库_已消化/06-基础知识库/02-核心推荐书目/03-考试执业类/README]]": "<!-- 已归档: 考试执业类/README -->",
    }
    for old, new in archive_fixes.items():
        c = c.replace(old, new)

    # 11. Bare name fixes
    c = c.replace("[[10-索引与导航/标签体系]]", "[[10-索引与导航/🏷️ 标签体系|标签体系]]")
    c = c.replace("[[10-索引与导航/标签体系|", "[[10-索引与导航/🏷️ 标签体系|")
    c = c.replace("[[知识库首页]]", "[[🏠 知识库首页]]")
    c = c.replace("[[知识库首页|", "[[🏠 知识库首页|")
    c = c.replace("[[../12-项目案例库]]", "[[12-项目案例库/项目案例库-总览|项目案例库]]")

    # 12. .obsidian/templates refs (exist but hidden)
    tpls = ["项目记录模板","造价笔记模板","项目元数据模板","文件夹索引模板"]
    for t in tpls:
        c = c.replace(f"[[.obsidian/templates/{t}]]", f"`.obsidian/templates/{t}` <!-- Templater模板 -->")

    if c != orig:
        f.write_text(c, encoding='utf-8')
        cnt += 1

print(f"Fixed {cnt} files (final comprehensive pass)")
