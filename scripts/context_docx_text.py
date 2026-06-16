from __future__ import annotations

import sys
from pathlib import Path

from docx import Document

doc = Document(str(Path(sys.argv[1])))
start = int(sys.argv[2])
end = int(sys.argv[3])
for i, p in enumerate(doc.paragraphs, start=1):
    if start <= i <= end:
        style = getattr(p.style, "name", "")
        text = p.text.replace("\n", "\\n")
        print(f"{i:04d} [{style}] {text}")
