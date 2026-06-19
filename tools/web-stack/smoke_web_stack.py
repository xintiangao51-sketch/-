import os, sys, json, subprocess, tempfile, pathlib, textwrap, urllib.parse
from importlib.metadata import version, PackageNotFoundError

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'test-output' / 'web-stack-smoke'
OUT.mkdir(parents=True, exist_ok=True)
PY = sys.executable

def pkgver(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None

def run(cmd, timeout=120, env=None):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout, env=env)
    return {"cmd":" ".join(map(str,cmd)), "returncode":p.returncode, "stdout":p.stdout[-2000:], "stderr":p.stderr[-2000:]}

results = []

def record(name, ok, detail):
    results.append({"name": name, "ok": bool(ok), "detail": detail})
    print(("PASS" if ok else "FAIL"), name, str(detail)[:300].replace('\n',' | '))

# 1 Jina Reader via r.jina.ai
try:
    import requests
    url = 'https://r.jina.ai/http://r.jina.ai/http://example.com'
    r = requests.get(url, timeout=30)
    ok = r.status_code == 200 and 'Example Domain' in r.text
    (OUT/'jina_example.md').write_text(r.text, encoding='utf-8')
    record('Jina Reader', ok, {"status": r.status_code, "chars": len(r.text), "file": str(OUT/'jina_example.md')})
except Exception as e:
    record('Jina Reader', False, repr(e))

# 2 Scrapling static fetch
try:
    from scrapling.fetchers import Fetcher
    page = Fetcher.get('https://example.com')
    title = page.css('h1::text').get()
    record('Scrapling Fetcher', title == 'Example Domain', {"version": pkgver('scrapling'), "title": title})
except Exception as e:
    record('Scrapling Fetcher', False, {"version": pkgver('scrapling'), "error": repr(e)})

# 3 Crawl4AI skill CLI help + import
try:
    import crawl4ai
    cli = ROOT/'tools'/'web-stack'/'.venv'/'Scripts'/'crawl4ai-skill.exe'
    rr = run([str(cli), '--help'], timeout=60)
    ok = rr['returncode'] == 0 and 'Commands:' in rr['stdout']
    record('Crawl4AI Skill CLI', ok, {"version": pkgver('crawl4ai-skill'), "crawl4ai": pkgver('crawl4ai'), "cli": rr})
except Exception as e:
    record('Crawl4AI Skill CLI', False, repr(e))

# 4 Tavily package / API key gate
try:
    import tavily
    has_key = bool(os.environ.get('TAVILY_API_KEY'))
    if has_key:
        rr = run([PY, str(ROOT/'skills'/'tavily'/'scripts'/'tavily_search.py'), 'OpenAI', '--max-results', '1'], timeout=60)
        ok = rr['returncode'] == 0
        detail = {"version": pkgver('tavily-python'), "api_key": True, "run": rr}
    else:
        ok = True
        detail = {"version": pkgver('tavily-python'), "api_key": False, "note": "No TAVILY_API_KEY in environment; package import verified, live search skipped."}
    record('Tavily', ok, detail)
except Exception as e:
    record('Tavily', False, repr(e))

# 5 Pandoc via pypandoc binary
try:
    import pypandoc
    md = OUT/'pandoc_input.md'; html = OUT/'pandoc_output.html'; docx = OUT/'pandoc_output.docx'
    md.write_text('# 标题\n\n这是 Pandoc 试跑。\n', encoding='utf-8')
    pypandoc.convert_file(str(md), 'html', outputfile=str(html))
    pypandoc.convert_file(str(md), 'docx', outputfile=str(docx))
    ok = html.exists() and html.stat().st_size > 20 and docx.exists() and docx.stat().st_size > 1000
    record('Pandoc', ok, {"pypandoc": pkgver('pypandoc'), "html": str(html), "docx": str(docx), "html_size": html.stat().st_size, "docx_size": docx.stat().st_size})
except Exception as e:
    record('Pandoc', False, {"pypandoc": pkgver('pypandoc'), "error": repr(e)})

# 6 Marker CLI help + lightweight PDF extraction with --disable_ocr
try:
    from reportlab.pdfgen import canvas
    pdf = OUT/'marker_input.pdf'; outdir = OUT/'marker_out'
    c = canvas.Canvas(str(pdf)); c.drawString(72,720,'Hello Marker PDF'); c.drawString(72,700,'Xinjiang cost engineer smoke test'); c.save()
    marker_cli = ROOT/'tools'/'web-stack'/'.venv'/'Scripts'/'marker_single.exe'
    rr = run([str(marker_cli), str(pdf), '--output_dir', str(outdir), '--disable_ocr', '--disable_multiprocessing', '--disable_image_extraction'], timeout=240)
    found = list(outdir.rglob('*.md')) if outdir.exists() else []
    ok = rr['returncode'] == 0 and found and any('Hello Marker PDF' in f.read_text(encoding='utf-8', errors='ignore') for f in found)
    record('Marker PDF', ok, {"version": pkgver('marker-pdf'), "pdf": str(pdf), "outdir": str(outdir), "md_files": [str(f) for f in found], "run": rr})
except Exception as e:
    record('Marker PDF', False, {"version": pkgver('marker-pdf'), "error": repr(e)})

# 7 CamoFox npm package help/version and server start quick check if possible
try:
    rr_version = run(['npx','--yes','camofox-browser@2.4.5','--version'], timeout=60)
    rr_mcp = run(['npx','--yes','camofox-mcp@1.10.0','--help'], timeout=60)
    ok = rr_version['returncode'] == 0 and '2.4.5' in rr_version['stdout'] and rr_mcp['returncode'] == 0
    record('CamoFox packages', ok, {"browser_version": rr_version, "mcp_help": rr_mcp})
except Exception as e:
    record('CamoFox packages', False, repr(e))

summary = {"ok": all(r['ok'] for r in results), "results": results}
(OUT/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print('\nSUMMARY_FILE', OUT/'summary.json')
if not summary['ok']:
    sys.exit(1)
