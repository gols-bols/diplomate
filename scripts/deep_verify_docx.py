"""Глубокая проверка связей изображений в docx (ZIP + rels)."""
from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document

DIPLOMA = Path(__file__).resolve().parent.parent / "docs" / "Диплом_отдельный_финал_60.docx"


def main() -> None:
    print("FILE:", DIPLOMA, "size:", DIPLOMA.stat().st_size)
    with ZipFile(DIPLOMA) as zf:
        media = [n for n in zf.namelist() if n.startswith("word/media/")]
        print("media files:", len(media))
        ct = zf.read("[Content_Types].xml").decode("utf-8")
        print("Content_Types has png:", "image/png" in ct)
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")
        image_rels = re.findall(r'Target="media/([^"]+)"', rels)
        print("document.xml.rels -> media:", image_rels)
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        embeds = re.findall(r'r:embed="([^"]+)"', doc_xml)
        print("r:embed count in document.xml:", len(embeds))
        blips = doc_xml.count("<a:blip")
        drawings = doc_xml.count("<w:drawing")
        print("a:blip:", blips, "w:drawing:", drawings)
        # orphan embeds?
        rids = set(re.findall(r'Id="(rId\d+)"', rels))
        for e in embeds:
            if e not in rids:
                print("WARN orphan embed", e)

    doc = Document(str(DIPLOMA))
    broken = 0
    for i, p in enumerate(doc.paragraphs):
        for run in p.runs:
            if run._element.xpath(".//a:blip"):
                try:
                    # access inline shape if any
                    _ = run.element
                except Exception as exc:
                    print("broken run", i, exc)
                    broken += 1
    print("broken runs:", broken)


if __name__ == "__main__":
    main()
