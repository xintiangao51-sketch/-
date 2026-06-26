#!/usr/bin/env node
/**
 * 统一检索脚本 · Node 版
 * 用法： node search.js "查询词"
 * 输出： 控制台 + output/yyyy-mm-dd_HH-MM-SS_<query>.md
 *
 * 设计：
 *   - 并行查询所有启用的引擎，失败不阻塞其它
 *   - 本地 markdown 用纯 Node 实现，不依赖外部库
 *   - 三件套通过 fetch (Node18+) 调 HTTP API
 *   - 结果合并、按相关度排序、去重、Top N 输出
 */

const fs = require('fs');
const path = require('path');

// ── 解析 CLI ────────────────────────────────────────
const query = process.argv.slice(2).join(' ').trim();
if (!query) {
  console.error('用法： node search.js "查询词"');
  process.exit(1);
}

const ROOT = path.resolve(__dirname);
const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, 'config', 'engines.json'), 'utf8'));
const TIMEOUT_MS = 8000;

// ── 工具函数 ────────────────────────────────────────
function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error(`${label} 超时(${ms}ms)`)), ms))
  ]);
}

function escapeHtml(s) { return (s || '').replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])); }

function snippet(text, query, maxLen = 200) {
  if (!text) return '';
  const lower = text.toLowerCase();
  const q = query.toLowerCase();
  const tokens = q.split(/\s+/).filter(Boolean);
  let idx = -1;
  for (const t of tokens) {
    idx = lower.indexOf(t);
    if (idx >= 0) break;
  }
  if (idx < 0) idx = 0;
  const start = Math.max(0, idx - 60);
  return (start > 0 ? '…' : '') + text.substring(start, start + maxLen).replace(/\s+/g, ' ').trim() + (start + maxLen < text.length ? '…' : '');
}

// ── 引擎 1: 本地 markdown 全文搜 ───────────────────────
async function searchLocalMd(query) {
  const cfg = CONFIG.engines.local_md;
  if (!cfg?.enabled) return { name: 'local_md', results: [], skipped: '未启用' };

  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!tokens.length) return { name: 'local_md', results: [] };

  const excludes = new Set(cfg.exclude_dirs || []);
  const hits = [];

  function walk(dir) {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.isDirectory()) {
        if (excludes.has(e.name)) continue;
        walk(path.join(dir, e.name));
      } else if (e.isFile() && /\.(md|markdown|txt)$/i.test(e.name)) {
        const full = path.join(dir, e.name);
        let content;
        try { content = fs.readFileSync(full, 'utf8'); } catch { continue; }
        const lower = content.toLowerCase();
        let score = 0;
        for (const t of tokens) {
          const m = lower.split(t).length - 1;
          if (m > 0) score += m * (t.length > 4 ? 2 : 1);
        }
        if (score > 0) {
          hits.push({
            engine: 'local_md',
            score,
            title: path.basename(full, path.extname(full)),
            path: full,
            url: 'file:///' + full.replace(/\\/g, '/'),
            snippet: snippet(content, query),
          });
        }
      }
    }
  }

  try {
    walk(cfg.root);
    hits.sort((a, b) => b.score - a.score);
    return { name: 'local_md', results: hits.slice(0, CONFIG.output.top_per_engine) };
  } catch (e) {
    return { name: 'local_md', error: e.message, results: [] };
  }
}

// ── 引擎 2: Khoj ──────────────────────────────────
async function searchKhoj(query) {
  const cfg = CONFIG.engines.khoj;
  if (!cfg?.enabled || !cfg.url) return { name: 'khoj', results: [], skipped: '未启用' };
  try {
    const url = `${cfg.url}/api/search?q=${encodeURIComponent(query)}&t=markdown&n=${CONFIG.output.top_per_engine}`;
    const headers = { 'Accept': 'application/json' };
    if (cfg.api_key) headers['Authorization'] = `Bearer ${cfg.api_key}`;
    const r = await withTimeout(fetch(url, { headers }), TIMEOUT_MS, 'Khoj');
    if (!r.ok) return { name: 'khoj', error: `HTTP ${r.status}`, results: [] };
    const data = await r.json();
    const list = Array.isArray(data) ? data : (data.results || data.entries || []);
    return {
      name: 'khoj',
      results: list.slice(0, CONFIG.output.top_per_engine).map(it => ({
        engine: 'khoj',
        score: it.score || it.relevance || 1,
        title: it.title || it.compiled?.split('\n')[0]?.substring(0, 80) || '(no title)',
        path: it.file || it.url || '',
        url: it.url || it.file || '',
        snippet: snippet(it.entry || it.compiled || it.snippet || '', query),
      })),
    };
  } catch (e) {
    return { name: 'khoj', error: e.message, results: [] };
  }
}

// ── 引擎 3: AnythingLLM ──────────────────────────────
async function searchAnythingLLM(query) {
  const cfg = CONFIG.engines.anythingllm;
  if (!cfg?.enabled || !cfg.url || !cfg.api_key) return { name: 'anythingllm', results: [], skipped: '未配置 API key' };
  try {
    // AnythingLLM 没有公开的 search API，用 workspace chat 当作检索代理
    if (!cfg.workspace) return { name: 'anythingllm', results: [], skipped: '未配置 workspace' };
    const url = `${cfg.url}/api/v1/workspace/${encodeURIComponent(cfg.workspace)}/chat`;
    const r = await withTimeout(fetch(url, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${cfg.api_key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: `请检索与"${query}"相关的文档片段，只列出引用片段，不要总结。`, mode: 'query' }),
    }), TIMEOUT_MS * 2, 'AnythingLLM');
    if (!r.ok) return { name: 'anythingllm', error: `HTTP ${r.status}`, results: [] };
    const data = await r.json();
    const sources = data.sources || [];
    return {
      name: 'anythingllm',
      results: sources.slice(0, CONFIG.output.top_per_engine).map(s => ({
        engine: 'anythingllm',
        score: s.score || 0.5,
        title: s.title || s.docname || '(no title)',
        path: s.url || '',
        url: s.url || '',
        snippet: snippet(s.text || s.chunk || '', query),
      })),
    };
  } catch (e) {
    return { name: 'anythingllm', error: e.message, results: [] };
  }
}

// ── 引擎 4: RAGFlow ──────────────────────────────────
async function searchRAGFlow(query) {
  const cfg = CONFIG.engines.ragflow;
  if (!cfg?.enabled || !cfg.url || !cfg.api_key) return { name: 'ragflow', results: [], skipped: '未配置' };
  try {
    const url = `${cfg.url}/api/v1/retrieval`;
    const r = await withTimeout(fetch(url, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${cfg.api_key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: query,
        kb_id: cfg.kb_id || undefined,
        top_k: CONFIG.output.top_per_engine,
      }),
    }), TIMEOUT_MS, 'RAGFlow');
    if (!r.ok) return { name: 'ragflow', error: `HTTP ${r.status}`, results: [] };
    const data = await r.json();
    const chunks = data.data?.chunks || data.chunks || [];
    return {
      name: 'ragflow',
      results: chunks.slice(0, CONFIG.output.top_per_engine).map(c => ({
        engine: 'ragflow',
        score: c.similarity || c.score || 0.5,
        title: c.docnm_kwd || c.document_name || '(no title)',
        path: c.docnm_kwd || '',
        url: '',
        snippet: snippet(c.content_with_weight || c.content || '', query),
      })),
    };
  } catch (e) {
    return { name: 'ragflow', error: e.message, results: [] };
  }
}

// ── 主流程 ───────────────────────────────────────────
(async () => {
  console.log(`\n🔍 查询: "${query}"\n`);
  const t0 = Date.now();

  const reports = await Promise.all([
    searchLocalMd(query),
    searchKhoj(query),
    searchAnythingLLM(query),
    searchRAGFlow(query),
  ]);

  const elapsed = ((Date.now() - t0) / 1000).toFixed(2);

  // 控制台输出
  let mdOut = `# 检索报告\n\n- **查询**: \`${query}\`\n- **时间**: ${new Date().toISOString()}\n- **耗时**: ${elapsed}s\n\n---\n\n`;

  for (const rep of reports) {
    const label = `[${rep.name}]`.padEnd(15);
    if (rep.skipped) {
      console.log(`${label} ⏭  跳过：${rep.skipped}`);
      mdOut += `## ⏭ ${rep.name} — 跳过：${rep.skipped}\n\n`;
      continue;
    }
    if (rep.error) {
      console.log(`${label} ❌ 失败：${rep.error}`);
      mdOut += `## ❌ ${rep.name} — 失败：${rep.error}\n\n`;
      continue;
    }
    console.log(`${label} ✅ ${rep.results.length} 条`);
    mdOut += `## ✅ ${rep.name} — ${rep.results.length} 条\n\n`;

    if (rep.results.length === 0) {
      mdOut += '_无结果_\n\n';
      continue;
    }
    rep.results.forEach((r, i) => {
      console.log(`  ${i + 1}. [${r.score.toFixed?.(2) ?? r.score}] ${r.title}`);
      console.log(`     📄 ${r.path || r.url}`);
      console.log(`     ${r.snippet.substring(0, 120)}...`);
      mdOut += `### ${i + 1}. ${r.title}\n`;
      mdOut += `- 相关度: ${r.score}\n`;
      mdOut += `- 路径: \`${r.path || r.url}\`\n`;
      mdOut += `- 片段:\n\n  > ${r.snippet}\n\n`;
    });
  }

  // 落盘
  if (CONFIG.output.save_md) {
    const ts = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
    const safeQ = query.replace(/[^\w\u4e00-\u9fa5]+/g, '_').substring(0, 40);
    const outPath = path.join(CONFIG.output.dir, `${ts}_${safeQ}.md`);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, mdOut, 'utf8');
    console.log(`\n💾 报告: ${outPath}`);
  }

  console.log(`\n⏱  共 ${elapsed}s\n`);
})();
