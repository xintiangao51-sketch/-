#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断链精准修复 v6 — 处理剩余 54 个
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VAULT = Path('D:/知识库')

# === 精准映射 ===
PATH_FIXES = {
    # PDF/JSON 文件存在（保持 wikilink 引用即可），但 v5 已用全路径，obsidian 能解析
    # 但有些引用的是别名（无路径），需要加全路径

    # PDF/JSON 短名加全路径（如果 wikilink 是裸文件名且文件存在）
    # 这里只处理完全找不到的路径

    # KC 文件夹引用去斜杠
    '08-参考规范/KC-001_造价管理办法_2026修订/': '08-参考规范/KC-001_造价管理办法_2026修订',
    '08-参考规范/KC-002_GB50500_2024计价标准/': '08-参考规范/KC-002_GB50500_2024计价标准',
    '08-参考规范/KC-003_新疆定额体系现状_202606/': '08-参考规范/KC-003_新疆定额体系现状_202606',
    '10-索引与导航/KC-004_知识库改造方案_v1/': '10-索引与导航/KC-004_知识库改造方案_v1',

    # 总览带斜杠
    '06-参考文档/项目表单模板/项目表单模板-总览/': '06-参考文档/项目表单模板/项目表单模板-总览',
    '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设/': '06-参考文档/DDC数字驱动建设/cards/_index_DDC数字驱动建设',

    # KC 描述
    'KC-310: 机械台班': '10-索引与导航/知识库总索引#KC-310',

    # 数字驱动建设
    '06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07.txt': '06-参考文档/DDC数字驱动建设/数字住建规划_正文_2024-02-07',
    '06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文.md': '06-参考文档/DDC数字驱动建设/BIM全生命周期通知_2026-05-08_全文',
    '06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文.md': '06-参考文档/DDC数字驱动建设/住建部活动/01_智能建造工作现场会_2024-11-07_青岛_全文',
    '06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文.md': '06-参考文档/DDC数字驱动建设/住建部活动/02_住建部赴乌鲁木齐调研_全文',

    # 项目案例库的 KC（实际位置）
    '12-项目案例库/.../KC-劳务分包价格库-2026市政与企业对下指导价/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-劳务分包价格库-2026市政与企业对下指导价',
    '12-项目案例库/.../KC-劳务扩大报价分析方法论/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-劳务扩大报价分析方法论',
    '12-项目案例库/.../KC-劳务清包合同风险条款模板/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-劳务清包合同风险条款模板',
    '12-项目案例库/.../KC-建筑设备带人租赁税务定性/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-建筑设备带人租赁税务定性',
    '12-项目案例库/.../KC-旋挖钻班组最终结算案例-田让存/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-旋挖钻班组最终结算案例-田让存',
    '12-项目案例库/.../KC-鄯善启创劳务扩大报价案例复盘/': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/03_知识卡片/KC-鄯善启创劳务扩大报价案例复盘',

    # 04_分析报告-总览（实际位置）
    '09-项目资料/04_分析报告/04_分析报告-总览': '12-项目案例库/劳务分包与扩大劳务报价/2026-劳务价格与鄯善启创案例/04_分析报告/04_分析报告-总览',

    # 智能建造 PDF
    '01-造价核心/定额与计价/2026-新疆配套调整/04-智能建造-建筑机器人-消耗量定额-试行.pdf': '08-参考规范/KC-003_新疆定额体系现状_202606',
    '01-造价核心/定额与计价/2026-新疆配套调整/robot_quota_items.json': '08-参考规范/KC-003_新疆定额体系现状_202606',

    # 标签体系
    '10-索引与导航/标签体系': '10-索引与导航/🏷️ 标签体系',
    '知识库首页': '🏠 知识库首页',
    '11-材料设备价格库/乌鲁木齐2026-04_速查': '11-材料设备价格库/乌鲁木齐2026-04_速查',

    # quota_xx 文件去 .md
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_00_说明及封面': '01-造价核心/定额与计价/2026-新疆配套调整/quota_00_说明及封面.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_01_册机械设备安装工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_01_册机械设备安装工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_02_册热力设备安装工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_02_册热力设备安装工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_03_册静置设备与工艺金属结构': '01-造价核心/定额与计价/2026-新疆配套调整/quota_03_册静置设备与工艺金属结构.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_04_册电气设备安装工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_04_册电气设备安装工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_05_册建筑智能化工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_05_册建筑智能化工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_06_册自动化控制仪表安装工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_06_册自动化控制仪表安装工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_07_册通风空调工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_07_册通风空调工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_08_册工业管道工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_08_册工业管道工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_09_册消防工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_09_册消防工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_10_册给排水、采暖、燃气工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_10_册给排水、采暖、燃气工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_11_一册通信设备及线路工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_11_一册通信设备及线路工程.md',
    '01-造价核心/定额与计价/2026-新疆配套调整/quota_12_二册刷油、防腐蚀、绝热工程': '01-造价核心/定额与计价/2026-新疆配套调整/quota_12_二册刷油、防腐蚀、绝热工程.md',

    # Excalidraw 文件
    '07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw': '07-AI工具与技能/drawing-analyzer/Drawing 2026-06-08 23.46.29.excalidraw.md',

    # AI工具
    '07-AI工具与技能/md文档/造价工作台搭建方案': '07-AI工具与技能/md文档/造价工作台搭建方案.md',

    # skills 子目录的总览 → 创建对应的"-总览"指向主页
    '07-AI工具与技能/Hermes配置/skills/ima-skill/ima-skill-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill',
    '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/xinjiang-cost-engineer-总览': '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base/knowledge-base-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/knowledge-base',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/notes-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/notes',
    '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/references/references-总览': '07-AI工具与技能/Hermes配置/skills/ima-skill/notes/references',
    '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references/references-总览': '07-AI工具与技能/Hermes配置/skills/xinjiang-cost-engineer/references',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/ima-skill-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill',
    '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/xinjiang-cost-engineer-总览': '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/knowledge-base-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/notes-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/references/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/knowledge-base/references',
    '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/references/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/ima-skill/notes/references',
    '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/references/references-总览': '07-AI工具与技能/Hermes配置/备份/skills/xinjiang-cost-engineer/references',
}

def main():
    files_touched = set()
    total_fixes = 0

    for src in VAULT.rglob('*.md'):
        if any(part.startswith('.') for part in src.parts):
            continue
        text = src.read_text(encoding='utf-8', errors='ignore')
        original = text

        for old, new in PATH_FIXES.items():
            for sep in [f'[[{old}]]', f'[[{old}|']:
                if sep in text:
                    text = text.replace(sep, f'[[{new}|' if sep.endswith('|') else f'[[{new}]]')
                    total_fixes += text.count('[[') - original.count('[[')

        if text != original:
            src.write_text(text, encoding='utf-8')
            files_touched.add(src)

    print(f"已修改文件: {len(files_touched)}")
    print(f"路径修复: {total_fixes}")

if __name__ == '__main__':
    main()