"""
Пересборка рисунков в РЕАЛЬНОМ дипломе пользователя (Downloads/Диплом_*_3_v2.docx).
Ассеты (PNG) — из kurso-main 2/docs/mockup_images и diagram_images.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from docx import Document

from docx_cleanup import fix_chapter_heading_breaks, rebuild_requirements_list
from project_paths import PROJECT_ROOT, diploma_v2_path

SCRIPTS = Path(__file__).resolve().parent
MIN_IMAGES = 10


def run_script(name: str, *args: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=str(SCRIPTS))


def main() -> None:
    print("Корень проекта:", PROJECT_ROOT)
    target = diploma_v2_path()

    run_script("generate_figma_mockup_images.py")
    run_script("generate_diploma_diagrams.py")

    doc = Document(str(target))
    rebuild_requirements_list(doc)
    fix_chapter_heading_breaks(doc)
    doc.save(str(target.resolve()))
    print("OK: п. 1.4 и разрывы страниц")

    run_script("insert_all_diploma_figures.py", "--force")

    from zipfile import ZipFile

    with ZipFile(target) as zf:
        n = len([x for x in zf.namelist() if x.startswith("word/media/")])
    if n < MIN_IMAGES:
        raise SystemExit(f"ПРОВАЛ: media={n}, нужно >={MIN_IMAGES}")

    report = SCRIPTS / "insert_report.txt"
    print("Готово:", target)
    print("Отчёт:", report)


if __name__ == "__main__":
    main()
