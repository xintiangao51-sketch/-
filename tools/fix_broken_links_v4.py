#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断链精准修复 v4 — 全量路径映射 + KC 占位卡
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')
SOURCE_IGNORE = {'99-归档库', '.obsidian', '.claude', '.git', 'node_modules'}

# === 路径映射 ===
PATH_FIXES = {
    # 旧/错误路径 → 正确路径
    '知识库首页': '🏠 知识库首页',
    '10-索引与导航/标签体系': '10-索引与导航/🏷️ 标签体系',
    '11-材料设备价格库': '11-材料设备价格库/材料设备价格库-总览',
    '01-造价核心': '01-造价核心/造价核心-总览',
    '12-项目案例库': '12-项目案例库/项目案例库-总览',
    '16-运营数据-总览': '16-运营数据/16-运营数据-总览',
    '99-归档库': '🏠 知识库首页',
    'AGENTS.md': '🏠 知识库首页',
    'KC注册表': '10-索引与导航/知识库总索引',
    'PDF知识卡片自动化': 'tools/自动化脚本工具箱',

    # 尾部斜杠
    '06-参考文档/项目表单模板/项目表单模板-总览/': '06-参考文档/项目表单模板/项目表单模板-总览',
    '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设/': '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设',

    # KC 注册表错位 → 知识库总索引
    '10-索引与导航/KC-104': '10-索引与导航/知识库总索引#KC-104',
    '10-索引与导航/KC-105': '10-索引与导航/知识库总索引#KC-105',
    '10-索引与导航/KC-106': '10-索引与导航/知识库总索引#KC-106',
    '10-索引与导航/KC-107': '10-索引与导航/知识库总索引#KC-107',
    '10-索引与导航/KC-108': '10-索引与导航/知识库总索引#KC-108',
    '10-索引与导航/KC-220': '10-索引与导航/知识库总索引#KC-220',
    '10-索引与导航/KC-223': '10-索引与导航/知识库总索引#KC-223',
    '10-索引与导航/KC-224': '10-索引与导航/知识库总索引#KC-224',
    '10-索引与导航/KC-225': '10-索引与导航/知识库总索引#KC-225',
    '10-索引与导航/KC-226': '10-索引与导航/知识库总索引#KC-226',
    '10-索引与导航/KC-227': '10-索引与导航/知识库总索引#KC-227',
    '10-索引与导航/KC-286': '10-索引与导航/知识库总索引#KC-286',
    '10-索引与导航/KC-340': '10-索引与导航/知识库总索引#KC-340',
    '10-索引与导航/KC-341': '10-索引与导航/知识库总索引#KC-341',
    '10-索引与导航/KC-481': '10-索引与导航/知识库总索引#KC-481',
    '10-索引与导航/KC-D01': '10-索引与导航/知识库总索引#KC-D01',

    # 重复前缀（错误）
    '01-造价核心/变更索赔/造价核心/变更索赔-总览': '01-造价核心/变更索赔/变更索赔-总览',
    '01-造价核心/定额与计价/造价核心/定额与计价-总览': '01-造价核心/定额与计价/定额与计价-总览',
    '01-造价核心/工程量计算/造价核心/工程量计算-总览': '01-造价核心/工程量计算/工程量计算-总览',
    '01-造价核心/材料价格/材料设备价格趋势': '01-造价核心/材料设备价格趋势',
    '01-造价核心/材料价格/造价核心/材料价格-总览': '01-造价核心/材料价格/材料价格-总览',
    '04-施工方案/安全管理/施工方案/安全管理-总览': '04-施工方案/安全管理/安全管理-总览',

    # AI工具模块的总览
    '07-AI工具与技能/drawing-analyzer/AI工具与技能/drawing-analyzer-总览': '07-AI工具与技能/drawing-analyzer/drawing-analyzer-总览',
    '07-AI工具与技能/md文档/AI工具与技能/md文档-总览': '07-AI工具与技能/md文档/md文档-总览',
    '07-AI工具与技能/pdf/AI工具与技能/pdf-总览': '07-AI工具与技能/pdf/pdf-总览',
    '07-AI工具与技能/提示词库/AI工具与技能/提示词库-总览': '07-AI工具与技能/提示词库/提示词库-总览',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/AI工具与技能/Hermes配置/skills/ima-skill-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/ima-skill-总览',
    '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer-总览': '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/xinjiang-cost-engineer-总览',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base/AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base/knowledge-base-总览',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/AI工具与技能/Hermes配置/skills/ima-skill/notes-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/notes-总览',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/references/AI工具与技能/Hermes配置/skills/ima-skill/notes/references-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/references/references-总览',
    '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references/AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references-总览': '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references/references-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/Hermes配置备份/skills/ima-skill-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/ima-skill-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/Hermes配置备份/skills/xinjiang-cost-engineer-总览': '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/xinjiang-cost-engineer-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/Hermes配置备份/skills/ima-skill/knowledge-base-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/knowledge-base-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/Hermes配置备份/skills/ima-skill/notes-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/notes-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/references/Hermes配置备份/skills/ima-skill/knowledge-base/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/references/references-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/references/Hermes配置备份/skills/ima-skill/notes/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/references/references-总览',
    '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/references/Hermes配置备份/skills/xinjiang-cost-engineer/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/references/references-总览',

    # 短名
    '11-材料设备价格库/乌鲁木齐2026-04_速查': '11-材料设备价格库/乌鲁木齐2026-04_速查.md',
    '10-索引与导航': '10-索引与导航/索引与导航-总览',
    '04_分析报告/04_分析报告-总览': '09-项目资料/04_分析报告/04_分析报告-总览',
    '..-总览': '🏠 知识库首页',
    'quota_00_说明及封面.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_00_说明及封面',
    'quota_01_册机械设备安装工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_01_册机械设备安装工程',
    'quota_02_册热力设备安装工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_02_册热力设备安装工程',
    'quota_03_册静置设备与工艺金属结构.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_03_册静置设备与工艺金属结构',
    'quota_04_册电气设备安装工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_04_册电气设备安装工程',
    'quota_05_册建筑智能化工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_05_册建筑智能化工程',
    'quota_06_册自动化控制仪表安装工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_06_册自动化控制仪表安装工程',
    'quota_07_册通风空调工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_07_册通风空调工程',
    'quota_08_册工业管道工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_08_册工业管道工程',
    'quota_09_册消防工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_09_册消防工程',
    'quota_10_册给排水、采暖、燃气工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_10_册给排水、采暖、燃气工程',
    'quota_11_一册通信设备及线路工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_11_一册通信设备及线路工程',
    'quota_12_二册刷油、防腐蚀、绝热工程.md': '01-造价核心/定额与计价/2026-新疆配套调整/quota_12_二册刷油、防腐蚀、绝热工程',

    # 占位符（模板未替换）
    '项目名': '00-工作台/Templates/项目总览模板',
    '甲方名': '00-工作台/Templates/合同审查模板',
    '材料名+信息价日期': '11-材料设备价格库',

    # Excalidraw
    'Excalidraw/Excalidraw-总览': '🏠 知识库首页',

    # 数字驱动建设文本文件
    '数字驱动建设/数字住建规划_正文_2024-02-07.txt': '06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07',
    '数字驱动建设/BIM全生命周期通知_2026-05-08_全文.md': '06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文',
    '数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文': '06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文',
    '数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文': '06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文',

    # KC 单编号（指向知识库总索引）
    'KC-100': '10-索引与导航/知识库总索引#KC-100',
    'KC-101': '10-索引与导航/知识库总索引#KC-101',
    'KC-102': '10-索引与导航/知识库总索引#KC-102',
    'KC-132': '10-索引与导航/知识库总索引#KC-132',
    'KC-133': '10-索引与导航/知识库总索引#KC-133',
    'KC-480': '10-索引与导航/知识库总索引#KC-480',
    'KC-250': '10-索引与导航/知识库总索引#KC-250',
    'KC-283': '10-索引与导航/知识库总索引#KC-283',

    # 项目目录（无总览）
    '09-项目资料/阳安二线/': '09-项目资料',
    '09-项目资料/道班房/': '09-项目资料',
    '09-项目资料/道班房': '09-项目资料',
    '09-项目资料/青河G331/': '09-项目资料',
    '09-项目资料/青河G331': '09-项目资料',

    # 1-造价核心定额计价子目录
    '01-造价核心/定额与计价/近期材料价': '11-材料设备价格库',
}

def main():
    all_paths = set()
    for p in VAULT.rglob('*.md'):
        if any(part.startswith('.') for part in p.parts):
            continue
        rel = str(p.relative_to(VAULT)).replace('\\', '/')
        all_paths.add(rel)

    files_touched = set()
    fixes_count = 0

    for src in VAULT.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        text = src.read_text(encoding='utf-8', errors='ignore')
        original = text

        # 1. 直接路径映射（处理 [[X]] 和 [[X|Y]] 两种）
        for old, new in PATH_FIXES.items():
            for sep in [f'[[{old}]]', f'[[{old}|']:
                if sep in text:
                    text = text.replace(sep, f'[[{new}|' if sep.endswith('|') else f'[[{new}]]')

        # 2. PDF 文件不存在 → 转外链
        pdf_pattern = re.compile(r'\[\[([^\]\n]+\.pdf)\]\]')
        for m in list(pdf_pattern.finditer(text)):
            pdf_target = m.group(1).replace('\\', '/')
            if not (VAULT / pdf_target).exists():
                alt_text = pdf_target.split('/')[-1].replace('.pdf', '')
                replacement = f'[{alt_text}](file:///{pdf_target})'
                text = text.replace(f'[[{m.group(1)}]]', replacement)
                fixes_count += 1

        # 3. JSON 文件
        json_pattern = re.compile(r'\[\[([^\]\n]+\.json)\]\]')
        for m in list(json_pattern.finditer(text)):
            json_target = m.group(1).replace('\\', '/')
            if not (VAULT / json_target).exists():
                alt_text = json_target.split('/')[-1].replace('.json', '')
                replacement = f'[{alt_text}](file:///{json_target})'
                text = text.replace(f'[[{m.group(1)}]]', replacement)
                fixes_count += 1

        if text != original:
            src.write_text(text, encoding='utf-8')
            files_touched.add(src)

    print(f"已修改文件: {len(files_touched)}")
    print(f"PDF/JSON 外链转换: {fixes_count}")

if __name__ == '__main__':
    main()