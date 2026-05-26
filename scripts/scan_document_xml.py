import re
from pathlib import Path
from zipfile import ZipFile

path = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"
xml = ZipFile(path).read("word/document.xml").decode("utf-8")
print("total page breaks in document.xml:", xml.count('w:type="page"'))

needle = "13."
idx = xml.find("Наличие API")
if idx >= 0:
    chunk = xml[idx : idx + 2500]
    print("page breaks near item 13:", chunk.count('w:type="page"'))
    # show paragraph boundaries
    parts = chunk.split("</w:p>")
    for j, part in enumerate(parts[:8]):
        text = re.sub(r"<[^>]+>", "", part)
        text = re.sub(r"\s+", " ", text).strip()
        pb = 'w:type="page"' in part
        pbb = "pageBreakBefore" in part
        print(j, "PAGE" if pb else "-", "PBB" if pbb else "-", text[:90])
