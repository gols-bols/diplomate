"""
Принудительная вставка ВСЕХ рисунков в диплом:
- диаграммы (1.2, 2.1, 2.1.1, приложения А/Б)
- макеты интерфейса (2.2, перед 2.3)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from docx.text.paragraph import Paragraph

from docx_figures import (
    FigureCounter,
    add_figures_before_anchor,
    is_figure_block_paragraph,
    remove_all_figures_from_document,
    remove_figure_block_before,
    insert_figures_after_anchor,
    resolve_image_path,
    set_paragraph_text,
    set_run_font,
)
from project_paths import (
    DIAGRAM_DIR,
    DIPLOMA_REPO,
    MOCKUP_DIR,
    MOCKUP_FIGURES,
    PROJECT_ROOT,
    diploma_v2_path,
)

# (path, title, description with {n})
DIAGRAM_ER = (
    DIAGRAM_DIR / "diagram_er.png",
    "ER-модель",
    "На рисунке {n} представлена ER-модель базы данных проекта с сущностями users и tickets и связью один-ко-многим.",
)
DIAGRAM_ARCH = (
    DIAGRAM_DIR / "diagram_architecture.png",
    "Архитектура",
    "На рисунке {n} показана трёхуровневая архитектура: клиент (браузер), сервер Laravel и СУБД MySQL.",
)
DIAGRAM_UC = (
    DIAGRAM_DIR / "diagram_use_case.png",
    "Варианты использования",
    "На рисунке {n} приведена схема основных вариантов использования для ролей пользователь и менеджер/администратор.",
)
DIAGRAM_DB_USERS = (
    DIAGRAM_DIR / "diagram_db_users.png",
    "Таблица users",
    "На рисунке {n} представлена структура таблицы users с ключевыми полями учётной записи.",
)
DIAGRAM_DB_TICKETS = (
    DIAGRAM_DIR / "diagram_db_tickets.png",
    "Таблица tickets",
    "На рисунке {n} представлена структура таблицы tickets и внешних ключей на users.",
)
DIAGRAM_POSTMAN = (
    DIAGRAM_DIR / "diagram_postman.png",
    "Postman",
    "На рисунке {n} показан пример проверки API в Postman: запрос авторизации и JSON-ответ с токеном.",
)


def find_paragraph(
    doc: Document,
    pattern: re.Pattern[str],
    *,
    heading_only: bool = False,
    allow_appendix: bool = False,
) -> object | None:
    for paragraph in doc.paragraphs:
        text = (paragraph.text or "").strip()
        if not text or not pattern.search(text):
            continue
        style = paragraph.style.name if paragraph.style else ""
        if allow_appendix and re.match(r"^ПРИЛОЖЕНИЕ\s+([АБ]|\d+)", text, re.I):
            return paragraph
        if heading_only:
            if style in ("Heading 1", "Heading 2", "Heading 3", "Заголовок 1", "Заголовок 2", "Заголовок 3"):
                return paragraph
            if re.match(r"^1\.2\.\s", text) and style == "Normal":
                return paragraph
            continue
        if text in {"Содержание", "Введение"} or "1.1." in text and "1.2." in text and len(text) > 80:
            continue
        return paragraph
    return None


def add_section_intro_before(anchor, text: str, *, bold_title: str | None = None) -> None:
    if bold_title:
        hp = anchor.insert_paragraph_before()
        hp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = hp.add_run(bold_title)
        set_run_font(run, 15, True)
    intro = anchor.insert_paragraph_before()
    set_paragraph_text(intro, text, first_indent=True)


def verify_assets() -> list[str]:
    errors = []
    for path, *_ in [DIAGRAM_ER, DIAGRAM_ARCH, DIAGRAM_UC, DIAGRAM_DB_USERS, DIAGRAM_DB_TICKETS, DIAGRAM_POSTMAN, *MOCKUP_FIGURES]:
        if resolve_image_path(path) is None:
            errors.append(str(path))
    return errors


def insert_all(doc: Document, *, force: bool) -> dict[str, int]:
    stats: dict[str, int] = {}
    if force:
        n = remove_all_figures_from_document(doc)
        print(f"Удалено старых блоков рисунков по документу: {n}")
    counter = FigureCounter(0)

    plan: list[tuple[str, re.Pattern[str], str, list, str | None]] = [
        (
            "1.2",
            re.compile(r"^1\.2[\.\s]"),
            "before",
            [DIAGRAM_UC],
            "Схема вариантов использования (п. 1.2).",
        ),
        (
            "2.1.2",
            re.compile(r"^2\.1\.2[\.\s]"),
            "before",
            [DIAGRAM_ER],
            None,
        ),
        (
            "2.2",
            re.compile(r"^2\.2[\.\s]"),
            "before",
            [DIAGRAM_ARCH],
            None,
        ),
        (
            "2.3",
            re.compile(r"^2\.3[\.\s]"),
            "before",
            list(MOCKUP_FIGURES),
            "2.2.3. Скриншоты макетов интерфейса",
        ),
        (
            "appendix_a",
            re.compile(r"^ПРИЛОЖЕНИЕ\s+(А|1)\b", re.I),
            "after",
            [DIAGRAM_DB_USERS, DIAGRAM_DB_TICKETS],
            None,
        ),
        (
            "appendix_b",
            re.compile(r"^ПРИЛОЖЕНИЕ\s+(Б|2)\b", re.I),
            "after",
            [DIAGRAM_POSTMAN],
            None,
        ),
    ]

    for key, pattern, mode, figures, intro_title in plan:
        anchor = find_paragraph(
            doc,
            pattern,
            heading_only=(mode == "before" and not key.startswith("appendix")),
            allow_appendix=key.startswith("appendix"),
        )
        if anchor is None:
            print(f"ПРЕДУПРЕЖДЕНИЕ: якорь не найден — {key} {pattern.pattern}")
            stats[key] = 0
            continue

        if force:
            if mode == "before":
                removed = remove_figure_block_before(anchor)
            else:
                removed = 0
                nxt = anchor._p.getnext()
                while nxt is not None:
                    para = Paragraph(nxt, anchor._parent)
                    if not is_figure_block_paragraph(para):
                        break
                    nxt = nxt.getnext()
                    delete_paragraph(para)
                    removed += 1
            if removed:
                print(f"{key}: удалено старых абзацев — {removed}")

        if mode == "before":
            if intro_title:
                add_section_intro_before(
                    anchor,
                    "Ниже приведены макеты экранов веб-приложения (авторизация, журнал, создание и карточка заявки).",
                    bold_title=intro_title,
                )
            count = add_figures_before_anchor(doc, anchor, figures, counter=counter)
        else:
            count = insert_figures_after_anchor(doc, anchor, figures, counter=counter)

        stats[key] = count
        print(f"{key}: вставлено {count}")

    return stats


def verify_docx(path: Path) -> tuple[int, int, list[tuple[int, str]]]:
    from zipfile import ZipFile

    with ZipFile(path) as zf:
        media = [n for n in zf.namelist() if n.startswith("word/media/")]
    doc = Document(str(path))
    captions = []
    drawings = 0
    for i, p in enumerate(doc.paragraphs):
        t = (p.text or "").strip()
        if re.match(r"^Рисунок\s+\d+", t, re.I):
            captions.append((i, t))
        if p._p.xpath(".//w:drawing"):
            drawings += 1
    return len(media), drawings, captions


def main() -> None:
    import shutil

    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", default=True)
    parser.add_argument("--no-force", action="store_false", dest="force")
    parser.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Путь к docx (по умолчанию: Downloads/Диплом_отдельный_расширенный_3_v2.docx)",
    )
    parser.add_argument("--also-repo", action="store_true", help="Дополнительно обновить docs/Диплом_отдельный_финал_60.docx")
    args = parser.parse_args()

    target = (args.target or diploma_v2_path()).resolve()
    report = Path(__file__).resolve().parent / "insert_report.txt"

    print("Project root:", PROJECT_ROOT)
    print("Target docx size:", target.stat().st_size if target.is_file() else 0)

    missing = verify_assets()
    if missing:
        report.write_text("FAIL missing assets:\n" + "\n".join(missing), encoding="utf-8")
        sys.exit(1)

    if not target.is_file():
        report.write_text(f"FAIL not found: {target}", encoding="utf-8")
        sys.exit(1)

    backup = target.with_name(target.stem + ".bak_figures.docx")
    output = target.with_name(target.stem + "_С_РИСУНКАМИ.docx")
    shutil.copy2(target, backup)

    doc = Document(str(target))
    stats = insert_all(doc, force=args.force)

    saved_to = output
    try:
        doc.save(str(target))
        saved_to = target
        repaired = Document(str(target))
        repaired.save(str(target))
    except PermissionError:
        doc.save(str(output))
        repaired = Document(str(output))
        repaired.save(str(output))

    media_n, draw_n, caps = verify_docx(saved_to)
    lines = [
        f"SOURCE={target}",
        f"SAVED_TO={saved_to}",
        f"BACKUP={backup}",
        f"size={saved_to.stat().st_size}",
        f"media={media_n}",
        f"drawings={draw_n}",
        f"captions={len(caps)}",
        f"stats={stats}",
    ]
    for i, t in caps:
        lines.append(f"  para {i}: {t}")
    report.write_text("\n".join(lines), encoding="utf-8")

    if media_n < 10 or draw_n < 10 or len(caps) < 10:
        sys.exit(1)

    if args.also_repo and DIPLOMA_REPO.is_file():
        shutil.copy2(target, DIPLOMA_REPO)

    print("OK report:", report.name)


if __name__ == "__main__":
    main()
