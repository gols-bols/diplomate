"""Проверка целевого диплома v2."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from zipfile import ZipFile

from docx import Document

from resolve_diploma_v2 import resolve_diploma_v2

REPORT = Path(__file__).resolve().parent / "diploma_v2_verify_report.txt"


def main() -> int:
    target = resolve_diploma_v2()
    lines = [f"TARGET={target}", f"exists={target.is_file()}", f"size={target.stat().st_size}"]

    with ZipFile(target) as zf:
        media = sorted(n for n in zf.namelist() if n.startswith("word/media/"))
        lines.append(f"media_count={len(media)}")
        for m in media:
            lines.append(f"  {m} {zf.getinfo(m).file_size}")

    doc = Document(str(target))
    for i, p in enumerate(doc.paragraphs):
        t = (p.text or "").strip()
        if re.match(r"^Рисунок\s+\d+", t, re.I) or p._p.xpath(".//w:drawing"):
            lines.append(f"para {i}: {'IMG' if p._p.xpath('.//w:drawing') else ''} {t[:80]}")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return 0 if target.is_file() else 1


if __name__ == "__main__":
    sys.exit(main())
