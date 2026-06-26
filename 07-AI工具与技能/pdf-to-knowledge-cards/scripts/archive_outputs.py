"""
归档：DDC卡片集从inbox → outputs
按知识库规范：06-参考文档已经是文档级目录，不区分inbox/outputs
但为了语义清晰，我们在outputs/也建一份（与原inbox并存）
"""
from pathlib import Path
from datetime import datetime

src = Path(r'D:\知识库\06-参考文档\DDC数字驱动建设')
out_root = Path(r'D:\知识库\outputs')
target = out_root / 'DDC数字驱动建设_知识卡片集'

# 创建目标目录
target.mkdir(parents=True, exist_ok=True)
(target / 'cards').mkdir(exist_ok=True)
(target / 'raw').mkdir(exist_ok=True)
(target / 'keywords').mkdir(exist_ok=True)

# 复制全部内容到outputs（标记已确认交付）
import shutil
src_cards = src / 'cards'
src_raw = src / 'raw'
src_kw = src / 'keywords'

for f in src_cards.glob('*.md'):
    shutil.copy2(f, target / 'cards' / f.name)
for f in src_raw.glob('*.txt'):
    shutil.copy2(f, target / 'raw' / f.name)
for f in src_kw.glob('*'):
    shutil.copy2(f, target / 'keywords' / f.name)

# 复制翻译瑕疵词典
shutil.copy2(src / '翻译瑕疵词典.md', target / '翻译瑕疵词典.md')

# 在outputs根加一个README说明这是已确认版本
readme = f'''---
tags: [交付, DDC, 知识卡片]
created: 2026-06-24
type: deliverable
status: 已人工确认（2026-06-24）
---

# DDC数字驱动建设 知识卡片集（已确认交付版）

> **来源**：《DDC数字驱动建设》第二版（中文版）574页
> **状态**：✅ 已人工确认（2026-06-24 昕田核可）
> **证据等级**：B级（机器抽取+人工复核）→ 已升为交付版
> **对应源数据**：`06-参考文档/DDC数字驱动建设/`（inbox级原始数据）
> **Agent**：Hermes（调度）+ Claude Code（深度判断）+ Codex（执行）

## 一、交付内容清单

```
DDC数字驱动建设_知识卡片集/
├── 翻译瑕疵词典.md          # 11条机器翻译修正（含详细对比表）
├── cards/                  # {len(list((target / 'cards').glob('*.md')))}张知识卡片
├── raw/                    # 22个原文切片（与inbox镜像）
└── keywords/               # 3个关键词JSON + 翻译瑕疵JSON
```

## 二、与inbox的关系

| 路径 | 用途 | 写入条件 | 当前状态 |
|------|------|----------|----------|
| `06-参考文档/DDC数字驱动建设/` | inbox半成品+原始一级证据 | 任何Agent可写 | 保留 |
| `outputs/DDC数字驱动建设_知识卡片集/` | 已确认交付物 | 仅人工确认后 | ✅ 2026-06-24 |

**边界**：两目录并存。inbox为持续研究源，outputs为正式交付快照。如有新版本需更新outputs并在CHANGELOG记录。

## 三、⚠后续待办

- 原子知识库13条增量条目 → 升级为A级证据（引用具体段落）
- 沉淀 `pdf-to-knowledge-cards` skill 到 07-AI工具与技能/
- 5条方法+5条工具同步到 `07-AI工具与技能/`

---

**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}  
**归档操作**：Hermes（按规范归档）
'''
(target / 'README.md').write_text(readme, encoding='utf-8')

print(f'✅ 已归档到: {target}')
print(f'   cards: {len(list((target / "cards").glob("*.md")))} 个md')
print(f'   raw: {len(list((target / "raw").glob("*.txt")))} 个txt')
print(f'   keywords: {len(list((target / "keywords").glob("*")))} 个文件')