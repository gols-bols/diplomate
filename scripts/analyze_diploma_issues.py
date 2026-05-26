from __future__ import annotations

import re
from pathlib import Path

from docx import Document

DIPLOMA = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"


def paragraph_flags(p) -> list[str]:
    flags = []
    if p._p.xpath('.//w:br[@w:type="page"]'):
        flags.append("PAGE_BR")
    if p.paragraph_format.page_break_before:
        flags.append("PBB")
    return flags


def main() -> None:
    doc = Document(DIPLOMA)
    start = end = None
    for i, p in enumerate(doc.paragraphs):
        t = (p.text or "").strip()
        if re.match(r"^1\.4[\.\s]", t) and start is None:
            start = i
        if start is not None and re.match(r"^1\.5[\.\s]", t):
            end = i
            break
    if start is None:
        print("1.3 not found")
        return
    end = end or start + 80
    print(f"=== 1.4 block (требования/задача) paragraphs {start}..{end} ===")
    for i in range(start, min(end, len(doc.paragraphs))):
        p = doc.paragraphs[i]
        t = (p.text or "").strip()
        style = p.style.name if p.style else ""
        flags = paragraph_flags(p)
        if flags or re.match(r"^\d+\.", t) or not t:
            print(f"{i:4d} {style:12} {'|'.join(flags) or '-':8} {t[:110]}")


if __name__ == "__main__":
    main()
