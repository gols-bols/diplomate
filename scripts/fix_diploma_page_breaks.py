from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document

from docx_cleanup import fix_chapter_heading_breaks, rebuild_requirements_list
from project_paths import DOCS_DIR, PROJECT_ROOT

DIPLOMA = DOCS_DIR / "Диплом_отдельный_финал_60.docx"


def main() -> None:
    if not DIPLOMA.is_file():
        raise SystemExit(f"Нет файла: {DIPLOMA}")

    backup = DIPLOMA.with_suffix(".docx.bak_layout")
    if not backup.exists():
        shutil.copy2(DIPLOMA, backup)

    doc = Document(str(DIPLOMA))
    rebuild_requirements_list(doc)
    fix_chapter_heading_breaks(doc)
    doc.save(str(DIPLOMA.resolve()))
    print(f"OK: {DIPLOMA}")
    print(f"Корень: {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
