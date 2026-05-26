from pathlib import Path
from zipfile import ZipFile

path = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"
xml = ZipFile(path).read("word/document.xml").decode("utf-8")
print("lastRenderedPageBreak:", xml.count("lastRenderedPageBreak"))
print('w:type="page":', xml.count('w:type="page"'))
print("pageBreakBefore:", xml.count("pageBreakBefore"))
