from pathlib import Path
import re
from zipfile import ZipFile
from docx import Document

path = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"
doc = Document(path)
with ZipFile(path) as zf:
    print("media count:", len([n for n in zf.namelist() if n.startswith("word/media/")]))

keywords = ("приложение", "2.1", "1.2", "диаграм", "рисунок", "схем", "er-", "архитект")
for i, p in enumerate(doc.paragraphs):
    t = (p.text or "").strip()
    low = t.lower()
    has_img = bool(p._p.xpath(".//w:drawing"))
    if any(k in low for k in keywords) or has_img or re.match(r"^Рисунок\s+\d", t, re.I):
        flag = "IMG" if has_img else "   "
        print(f"{i:4d} {flag} {t[:100]}")
