"""Проверка встроенных изображений и подписей «Рисунок» в docx."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from zipfile import ZipFile

from docx import Document

ROOT = Path(__file__).resolve().parent.parent
DIPLOMA = ROOT / "docs" / "Диплом_отдельный_финал_60.docx"
MIN_DIPLOMA_IMAGES = 10


def paragraph_has_drawing(p) -> bool:
    return bool(p._p.xpath(".//w:drawing"))


def verify(path: Path) -> bool:
    print("=" * 60)
    print("FILE:", path)
    print("exists:", path.is_file(), "size:", path.stat().st_size if path.is_file() else 0)
    if not path.is_file():
        return False

    with ZipFile(path) as zf:
        media = sorted(n for n in zf.namelist() if n.startswith("word/media/"))
        print("word/media files:", len(media))
        for m in media:
            print(f"  {m} ({zf.getinfo(m).file_size} bytes)")

    doc = Document(str(path))
    figures = []
    drawings = []
    for i, p in enumerate(doc.paragraphs):
        t = (p.text or "").strip()
        if re.match(r"^Рисунок\s+\d+", t, re.I):
            figures.append((i, t))
        if paragraph_has_drawing(p):
            drawings.append(i)

    print("paragraphs with drawing:", len(drawings), "->", drawings)
    print("captions:", len(figures))
    for i, t in figures:
        print(f"  para {i}: {t}")

    ok = len(media) == len(drawings) == len(figures) and len(media) > 0
    if path == DIPLOMA and len(media) < MIN_DIPLOMA_IMAGES:
        ok = False
        print(f"FAIL: diploma needs >={MIN_DIPLOMA_IMAGES} images, got {len(media)}")
    elif ok:
        print("OK")
    else:
        print("FAIL: media/drawings/captions mismatch")
    return ok


def main() -> None:
    ok = verify(DIPLOMA)
    other = ROOT / "docs" / "Пояснительная_записка_финал.docx"
    verify(other)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
