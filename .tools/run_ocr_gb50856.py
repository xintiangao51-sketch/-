# -*- coding: utf-8 -*-
"""GB50856 PDF OCR runner. Resumable per-page."""
import os, sys, time, json
from pathlib import Path
from rapidocr_onnxruntime import RapidOCR
import fitz

ROOT = Path(r"D:\知识库")
TOOLS = ROOT / ".tools"
TOOLS.mkdir(exist_ok=True)

JOBS = [
    {
        "pdf": ROOT / "GB50856-2013 通用安装工程工程量计算规范.pdf",
        "out": TOOLS / "gb50856_2013_ocr.txt",
        "state": TOOLS / "gb50856_2013_ocr.state.json",
        "dpi": 180,
    },
    {
        "pdf": ROOT / "GBT50856-2024通用安装工程工程量计算标准-住建部.pdf",
        "out": TOOLS / "gbt50856_2024_ocr.txt",
        "state": TOOLS / "gbt50856_2024_ocr.state.json",
        "dpi": 160,
    },
]

def run_one(job):
    pdf = job["pdf"]
    out = job["out"]
    state_p = job["state"]
    dpi = job["dpi"]
    print(f"[OCR] {pdf.name} dpi={dpi}")
    ocr = RapidOCR()
    doc = fitz.open(pdf)
    n = len(doc)
    state = {"done": 0}
    if state_p.exists():
        try:
            state = json.loads(state_p.read_text(encoding="utf-8"))
        except Exception:
            state = {"done": 0}
    done = state.get("done", 0)
    mode = "a" if done > 0 else "w"
    f = open(out, mode, encoding="utf-8")
    try:
        t0 = time.time()
        for i in range(done, n):
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            img = pix.tobytes("png")
            result, _ = ocr(img)
            text = "\n".join(line[1] for line in (result or []))
            f.write(f"\n\n===== page {i+1}/{n} =====\n{text}\n")
            f.flush()
            state["done"] = i + 1
            state_p.write_text(json.dumps(state), encoding="utf-8")
            if (i+1) % 5 == 0:
                el = time.time() - t0
                print(f"  {pdf.name} {i+1}/{n}  elapsed {el:.1f}s  ({el/(i+1-done):.2f}s/pg)")
    finally:
        f.close()
        doc.close()
    print(f"[DONE] {pdf.name}")

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "2013"
    if which == "2013":
        run_one(JOBS[0])
    elif which == "2024":
        run_one(JOBS[1])
    elif which == "both":
        run_one(JOBS[0])
        run_one(JOBS[1])
    else:
        print("usage: run_ocr_gb50856.py [2013|2024|both]")
