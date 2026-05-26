import re
from pathlib import Path
from zipfile import ZipFile

path = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"
styles = ZipFile(path).read("word/styles.xml").decode("utf-8")
for name in ("Heading1", "Heading2", "Heading3", "Normal"):
    idx = styles.find(f'w:val="{name}"')
    if idx < 0:
        continue
    chunk = styles[max(0, idx - 200) : idx + 600]
    print(f"=== {name} ===")
    print("pageBreakBefore" in chunk, chunk[:500])
