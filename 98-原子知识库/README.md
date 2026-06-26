---
tags: [知识库, 原子化, AI-first]
created: 2026-06-22
type: reference
---

# 98-原子知识库

> 为AI Agent设计的结构化造价知识资产。非人读文档，供Agent通过标准协议调用。

## 设计原则

| 原则 | 说明 |
|------|------|
| 原子化 | 每条知识一个独立事实，不混杂 |
| 可过滤 | 按type/tags/confidence多维筛选 |
| 可迭代 | use_count/last_used自动追踪，定期价值重判 |

## 六类原子信息

| 类型 | 文件 | 说明 |
|------|------|------|
| principles | principles.jsonl | 造价铁律与取费准则 |
| methods | methods.jsonl | 套定额/编清单/组价的具体方法 |
| cases | cases.jsonl | 项目实例与经验案例 |
| anti_patterns | anti_patterns.jsonl | 常见错误与禁止事项 |
| tools | tools.jsonl | 定额查询/信息价/工具路径 |
| insights | insights.jsonl | 市场洞察与经验总结 |

## 记录格式

```json
{
  "id": "P-2026-001",
  "type": "principle",
  "content": "具体知识内容",
  "tags": ["标签1", "标签2"],
  "source": "来源文件或项目",
  "confidence": "A/B/C/D",
  "created": "2026-06-22",
  "last_used": null,
  "use_count": 0
}
```

## 置信度等级

| 等级 | 含义 |
|------|------|
| A | 有定额原文/合同条款/信息价/图纸证据 |
| B | 有强经验/行业惯例/历史数据支撑 |
| C | 逻辑推断缺硬证据 |
| D | 资料不足或风险过高 |

## Agent调用方式

1. 读取index.json获取全局标签映射
2. 按tags/type筛选目标JSONL文件
3. 查询结果后更新use_count和last_used

## 维护规则

- 新知识：任务完成后由Hermes判断是否值得沉淀
- 价值重判：定期（周/月）由Agent结合个人画像重新评估
- 淘汰：use_count=0且confidence=C/D超过30天→标记待归档

---

🔗 **知识库首页**：[[🏠 知识库首页]]
