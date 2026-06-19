# Web 抓取/搜索/文档转换工具栈安装与验收记录

生成时间：2026-06-14
工作根目录：`D:\知识库`
Python 环境：`D:\知识库\tools\web-stack\.venv`（Python 3.11.15）

## 1. 已安装 SkillHub 技能

| 工具 | SkillHub slug | 安装目录 | 状态 |
|---|---|---|---|
| Jina Reader | `jina-ai` | `D:\知识库\skills\jina-ai` | 已安装 |
| Crawl4AI | `crawl4ai-skill` | `D:\知识库\skills\crawl4ai-skill` | 已安装 |
| Scrapling | `scrapling` | `D:\知识库\skills\scrapling` | 已安装 |
| CamoFox | `camofox-mcp` | `D:\知识库\skills\camofox-mcp` | 已安装 |
| Tavily | `tavily` | `D:\知识库\skills\tavily` | 已安装 |
| Pandoc | `pandoc` | `D:\知识库\skills\pandoc` | 已安装 |
| Marker | `latex-formula-extraction-marker` | `D:\知识库\skills\latex-formula-extraction-marker` | 已安装 |

## 2. 已安装本地运行环境

激活/调用方式：

```bash
# Git Bash，工作目录 D:\知识库
source tools/web-stack/.venv/Scripts/activate
# 或直接调用
./tools/web-stack/.venv/Scripts/python.exe --version
```

关键包版本：

| 包/命令 | 版本 | 说明 |
|---|---:|---|
| Python | 3.11.15 | venv 内解释器 |
| requests | 2.34.2 | Jina HTTP 调用基础 |
| scrapling | 0.2.99 | 静态抓取已通过；高版本因依赖回溯最终锁到 0.2.99 |
| crawl4ai-skill | 0.2.0 | CLI 可用 |
| crawl4ai | 0.8.9 | 单页抓取已通过 |
| tavily-python | 0.7.26 | 包可导入；缺 API key 未做在线搜索 |
| pypandoc | 1.17 | Python 封装 |
| pypandoc_binary | 1.17 | 内置 Pandoc 二进制 |
| Pandoc | 3.9 | 由 pypandoc_binary 提供 |
| marker-pdf | 1.10.2 | CLI 可用，首次运行已下载 OCR error 模型 |
| torch | 2.12.0+cpu | marker 依赖 |
| surya-ocr | 0.17.1 | marker 依赖 |
| camofox-browser | 2.4.5 | npm/npx 包可用；浏览器启动存在本机 profile 兼容问题 |
| camofox-mcp | 1.10.0 | npm/npx 包可用 |

## 3. 实测通过项

| 工具 | 验收命令/脚本 | 结果文件 | 结果 |
|---|---|---|---|
| Crawl4AI | `tools/web-stack/.venv/Scripts/crawl4ai-skill.exe crawl https://example.com --format fit_markdown --output test-output/web-stack-smoke/crawl4ai_example.md` | `test-output/web-stack-smoke/crawl4ai_example.md` | 通过，成功输出 Example Domain Markdown |
| Scrapling | `Fetcher.get('https://example.com')` | 脚本内断言 | 通过，抓到标题 `Example Domain` |
| Pandoc | `pypandoc.convert_file(..., 'html/docx')` | `pandoc_output.html`、`pandoc_output.docx` | 通过，Markdown 转 HTML/DOCX 成功 |
| Marker | `marker_single marker_input.pdf --output_dir marker_out2 --disable_ocr --disable_multiprocessing --disable_image_extraction` | `marker_out2/marker_input/marker_input.md` | 通过，PDF 提取文本成功 |
| CamoFox 包 | `npx --yes camofox-browser@2.4.5 --version`；`npx --yes camofox-mcp@1.10.0 --help` | 控制台输出 | 包检测通过 |
| Tavily 包 | `import tavily` | 无 | 包检测通过 |

## 4. 受限/未完全通过项

| 工具 | 问题 | 实测输出/原因 | 处理建议 |
|---|---|---|---|
| Jina Reader | 匿名访问被拒绝 | `401 AuthenticationRequiredError: blocked from performing anonymous queries due to bad IP reputation` | 需要申请/配置 `JINA_API_KEY` 后重测；技能已安装，本地 HTTP 调用逻辑可用 |
| Tavily | 缺 API Key | 环境中未发现 `TAVILY_API_KEY` | 申请 Tavily key 后写入 `.env` 或当前 shell：`export TAVILY_API_KEY=tvly-...`，再运行 `skills/tavily/scripts/tavily_search.py` |
| CamoFox 浏览器实跑 | 本机已有 `~/.camofox/profiles/cli-default` profile 与 camoufox-js 安装状态不兼容 | `Cannot verify profile compatibility for user "cli-default": installed Camoufox version could not be determined` | 包与服务健康检查可用；需清理/重建 CamoFox profile 或固定 `CAMOFOX_PROFILES_DIR` 后重启服务再做页面打开 |
| Scrapling stealth/Camoufox 依赖 | Camoufox 浏览器依赖下载被 GitHub API 限流 | `403 rate limit exceeded for https://api.github.com/repos/daijro/camoufox/releases` | 静态 Fetcher 已通过；StealthyFetcher 需等 GitHub 限流恢复或配置 GitHub token/代理后执行 `scrapling install` |

## 5. 快速使用命令

### Jina Reader

```bash
# 需要 JINA_API_KEY 时加 Header；匿名当前 IP 被 Jina 拒绝
curl -L "https://r.jina.ai/http://example.com"
```

### Crawl4AI

```bash
tools/web-stack/.venv/Scripts/crawl4ai-skill.exe crawl https://example.com --format fit_markdown --output out.md
tools/web-stack/.venv/Scripts/crawl4ai-skill.exe search "新疆 造价 信息价" --num-results 5
```

### Scrapling

```bash
tools/web-stack/.venv/Scripts/python.exe - <<'PY'
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')
print(page.css('h1::text').get())
PY
```

### Tavily

```bash
export TAVILY_API_KEY="tvly-你的key"
tools/web-stack/.venv/Scripts/python.exe skills/tavily/scripts/tavily_search.py "新疆建设工程信息价" --max-results 5
```

### Pandoc

```bash
tools/web-stack/.venv/Scripts/python.exe - <<'PY'
import pypandoc
pypandoc.convert_file('input.md', 'docx', outputfile='output.docx')
PY
```

### Marker

```bash
tools/web-stack/.venv/Scripts/marker_single.exe input.pdf --output_dir marker_out --disable_image_extraction
```

### CamoFox

```bash
npx --yes camofox-browser@2.4.5 --version
npx --yes camofox-browser@2.4.5 server start
curl http://localhost:9377/health
CAMOFOX_TRANSPORT=http npx --yes camofox-mcp@1.10.0
```

## 6. 验收产物

- `D:\知识库\test-output\web-stack-smoke\crawl4ai_example.md`
- `D:\知识库\test-output\web-stack-smoke\pandoc_output.html`
- `D:\知识库\test-output\web-stack-smoke\pandoc_output.docx`
- `D:\知识库\test-output\web-stack-smoke\marker_out2\marker_input\marker_input.md`
- `D:\知识库\test-output\web-stack-smoke\summary.json`（第一次综合脚本记录，含失败项详情）
