from docx import Document
from pathlib import Path

p = Path(r"c:\Users\Admin\Downloads\Диплом_отдельный_расширенный_3_v2_ФИНАЛ.docx")
doc = Document(str(p))
for i, par in enumerate(doc.paragraphs):
    t = (par.text or "").strip()
    if t == "Введение" or (i < 15 and t):
        fmt = par.paragraph_format
        print(
            i,
            repr(t[:50]),
            "before",
            fmt.space_before,
            "after",
            fmt.space_after,
            "first_indent",
            fmt.first_line_indent,
            par.style.name if par.style else "",
        )
