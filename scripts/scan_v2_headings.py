from pathlib import Path
import re
from docx import Document
from resolve_diploma_v2 import resolve_diploma_v2

target = resolve_diploma_v2()
doc = Document(str(target))
out = Path(__file__).resolve().parent / "diploma_v2_headings.txt"
lines = []
for i, p in enumerate(doc.paragraphs):
    t = (p.text or "").strip()
    if not t:
        continue
    st = p.style.name if p.style else ""
    if re.match(r"^[12]\.\d", t) or "риложен" in t.lower() or "Рисунок" in t or st.startswith("Heading"):
        lines.append(f"{i:4d} {st:12} {t[:100]}")
out.write_text("\n".join(lines), encoding="utf-8")
