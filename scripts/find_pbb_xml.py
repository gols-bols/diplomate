import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document

path = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"
xml = ZipFile(path).read("word/document.xml").decode("utf-8")
doc = Document(path)

# map para text to index
texts = [(i, (p.text or "").strip()[:80]) for i, p in enumerate(doc.paragraphs)]

# split by paragraphs in xml
parts = xml.split("<w:p ")
for idx, part in enumerate(parts[1:], start=0):
    if "pageBreakBefore" not in part:
        continue
    plain = re.sub(r"<[^>]+>", "", part)
    plain = re.sub(r"\s+", " ", plain).strip()[:90]
    # find closest doc paragraph by text overlap
    match_i = -1
    for i, t in texts:
        if t and t in plain:
            match_i = i
            break
    print("xml-part", idx, "para", match_i, plain)
