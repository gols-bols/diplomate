from docx import Document
from docx.oxml.ns import qn
from pathlib import Path

doc = Document(Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx")
for i, p in enumerate(doc.paragraphs):
    breaks = p._p.xpath(".//w:br")
    pbb = p.paragraph_format.page_break_before
    sect = p._p.findall(".//" + qn("w:sectPr"))
    if breaks or pbb or sect:
        kinds = [b.get(qn("w:type")) or "line" for b in breaks]
        print(i, "pbb", pbb, "br", kinds, "sect", len(sect), (p.text or "")[:60])
