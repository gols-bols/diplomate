#!/usr/bin/env python3
"""Fix diploma DOCX: assignment structure (chapter 1), typography, remove editor marks."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

SRC = Path("/Users/gnome/Downloads/Диплом_отдельный_расширенный (2).docx")
OUT = Path("/Users/gnome/Downloads/kurso-main 2/docs/Диплом_отдельный_финал_60.docx")
BAK = SRC.with_suffix(".docx.bak")

CENTER_TITLES = {
    "перечень сокращений и обозначений",
    "содержание",
    "введение",
    "заключение",
    "библиография",
    "список используемой литературы",
}

CH1_DELETE_PREFIXES = (
    "1.5 Обоснование архитектурных решений",
    "1.6 Анализ рисков",
    "1.7 Анализ требований к безопасности",
    "1.11 ",
    "1.12 ",
    "1.13 ",
    "1.14 ",
    "1.15 ",
    "1.16 ",
    "1.17 ",
    "1.18 ",
)

CH1_RENAME = {
    "1.1 Анализ предметной области": "1.2 Информационная и функциональная структура",
    "1.2 Анализ существующих подходов к обработке заявок": "1.4 Обзор аналогов информационных систем",
    "1.3 Формирование требований к системе": "1.6 Постановка задачи",
    "1.4 Выбор технологического стека": "1.5 Обоснование выбора программных средств для создания информационной системы",
    "1.8 Сведения об организации и особенности инфраструктуры": "1.1 Сведения об организации",
    "1.9 Обзор аналогов информационных систем": None,
    "1.10 Постановка задачи на разработку": None,
}

CLASSIFICATION_TEXT = (
    "Разрабатываемое решение относится к классу прикладных web-ориентированных информационных "
    "систем внутреннего использования. Такие системы предназначены для автоматизации учетных и "
    "операционных процессов организации, работают через браузер, используют централизованную базу "
    "данных и разграничение прав пользователей. Для проекта выбран тип локальной информационной "
    "системы управления заявками на стеке Laravel и MySQL."
)

YELLOW_REPHRASE = (
    "Наиболее распространенной формой взаимодействия сотрудников и технической поддержки во многих учреждениях по-прежнему остается неформализованная передача проблем: устные обращения, телефонные звонки, сообщения в мессенджерах и электронная почта. Такой подход не обеспечивает единого учета обращений, затрудняет контроль сроков и не позволяет формировать статистику.",
    "Во многих учреждениях обращения в техническую поддержку передаются неформализованно: устно, по телефону, через мессенджеры или электронную почту. При таком подходе трудно отслеживать статус заявки, фиксировать исполнителя и анализировать повторяющиеся инциденты.",
)


def scrub_run_xml(run) -> None:
    r_pr = run._element.find(qn("w:rPr"))
    if r_pr is None:
        return
    for tag in ("w:highlight", "w:shd"):
        for el in list(r_pr.findall(qn(tag))):
            r_pr.remove(el)
    for el in list(r_pr.findall(qn("w:color"))):
        r_pr.remove(el)


def set_run_black(run, *, size: int = 14, bold: bool = False) -> None:
    scrub_run_xml(run)
    run.font.name = "Times New Roman"
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.size = Pt(size)
    run.bold = bold


def set_paragraph_text(paragraph, text: str) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def remove_paragraph(paragraph) -> None:
    element = paragraph._element
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def find_heading1(doc: Document, predicate) -> int:
    for i, paragraph in enumerate(doc.paragraphs):
        if paragraph.style and paragraph.style.name == "Heading 1" and predicate(paragraph.text.strip()):
            return i
    return -1


def chapter1_sections(doc: Document) -> list[tuple[int, str]]:
    ch1 = find_heading1(doc, lambda t: t.startswith("1 Аналит"))
    ch2 = find_heading1(doc, lambda t: "Проектная" in t or "Практическая" in t)
    if ch1 == -1 or ch2 == -1:
        return []
    items: list[tuple[int, str]] = []
    for i in range(ch1 + 1, ch2):
        paragraph = doc.paragraphs[i]
        if paragraph.style and paragraph.style.name == "Heading 2":
            text = paragraph.text.strip()
            if re.match(r"^1\.\d+", text):
                items.append((i, text))
    return items


def delete_section(doc: Document, start: int, end: int) -> None:
    for i in range(end, start - 1, -1):
        remove_paragraph(doc.paragraphs[i])


def move_section(doc: Document, start: int, end: int, after: int) -> None:
    elements = [doc.paragraphs[i]._p for i in range(start, end + 1)]
    anchor = doc.paragraphs[after]._p
    for el in elements:
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)
    current = anchor
    for el in elements:
        current.addnext(el)
        current = el


def cleanup_pre_intro(doc: Document) -> None:
    for i in reversed(range(min(30, len(doc.paragraphs)))):
        text = doc.paragraphs[i].text.strip()
        if text.startswith(("Тема:", "Объект исследования:", "Предмет исследования:")):
            remove_paragraph(doc.paragraphs[i])


def rephrase_yellow(doc: Document) -> None:
    old, new = YELLOW_REPHRASE
    for paragraph in doc.paragraphs:
        if old in paragraph.text:
            set_paragraph_text(paragraph, paragraph.text.replace(old, new))


def fix_outdated_limitations(doc: Document) -> None:
    for paragraph in doc.paragraphs:
        if "В системе пока отсутствуют вложения, комментарии, история изменений" in paragraph.text:
            set_paragraph_text(
                paragraph,
                "На текущем этапе в системе не реализованы вложения файлов и email-уведомления; "
                "комментарии, история изменений статусов и базовая аналитика реализованы в рабочей версии проекта.",
            )


def restructure_chapter1(doc: Document) -> None:
    ch1 = find_heading1(doc, lambda t: t.startswith("1 Аналит"))
    ch2 = find_heading1(doc, lambda t: "Проектная" in t or "Практическая" in t)
    if ch1 == -1 or ch2 == -1:
        return

    sections = chapter1_sections(doc)
    if not sections:
        return

    ranges: list[tuple[int, int, str]] = []
    for idx, (start, title) in enumerate(sections):
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        ranges.append((start, end, title))

    by_title = {title: (start, end) for start, end, title in ranges}

    org = by_title.get("1.8 Сведения об организации и особенности инфраструктуры")
    if org:
        move_section(doc, org[0], org[1], ch1)

    # Delete redundant sections from end to start
    sections = chapter1_sections(doc)
    ch2 = find_heading1(doc, lambda t: "Проектная" in t or "Практическая" in t)
    for idx in range(len(sections) - 1, -1, -1):
        start, title = sections[idx]
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        if title in CH1_RENAME and CH1_RENAME[title] is None:
            delete_section(doc, start, end)
            continue
        if any(title.startswith(prefix) for prefix in CH1_DELETE_PREFIXES):
            delete_section(doc, start, end)

    # Merge 1.9 into 1.4 and 1.10 into 1.6 before delete if still present
    sections = chapter1_sections(doc)
    ch2 = find_heading1(doc, lambda t: "Проектная" in t or "Практическая" in t)
    for idx in range(len(sections) - 1, -1, -1):
        start, title = sections[idx]
        if title.startswith("1.9 ") or title.startswith("1.10 "):
            end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
            delete_section(doc, start, end)

    # Rename surviving headings
    for paragraph in doc.paragraphs:
        if paragraph.style and paragraph.style.name == "Heading 2":
            text = paragraph.text.strip()
            if text in CH1_RENAME and CH1_RENAME[text]:
                set_paragraph_text(paragraph, CH1_RENAME[text])

    # Insert 1.3 classification before 1.4
    for i, paragraph in enumerate(doc.paragraphs):
        if paragraph.style and paragraph.style.name == "Heading 2" and paragraph.text.strip().startswith("1.4 "):
            h = paragraph.insert_paragraph_before("1.3 Классификация информационных систем")
            h.style = doc.styles["Heading 2"]
            b = paragraph.insert_paragraph_before(CLASSIFICATION_TEXT)
            b.style = doc.styles["Normal"]
            break

    reorder_chapter1_blocks(doc)


def reorder_chapter1_blocks(doc: Document) -> None:
    desired = [
        "1.1 Сведения об организации",
        "1.2 Информационная и функциональная структура",
        "1.3 Классификация информационных систем",
        "1.4 Обзор аналогов информационных систем",
        "1.5 Обоснование выбора программных средств для создания информационной системы",
        "1.6 Постановка задачи",
    ]
    ch1 = find_heading1(doc, lambda t: t.startswith("1 Аналит"))
    ch2 = find_heading1(doc, lambda t: "Проектная" in t or "Практическая" in t)
    if ch1 == -1 or ch2 == -1:
        return

    sections = chapter1_sections(doc)
    grouped: dict[str, list] = {}
    for idx, (start, _title) in enumerate(sections):
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        key = doc.paragraphs[start].text.strip()
        grouped[key] = [doc.paragraphs[i]._p for i in range(start, end + 1)]

    anchor = doc.paragraphs[ch1]._p
    for i in range(ch2 - 1, ch1, -1):
        remove_paragraph(doc.paragraphs[i])

    current = anchor
    for want in desired:
        for key, elements in grouped.items():
            if key != want:
                continue
            for el in elements:
                current.addnext(el)
                current = el
            break


def paragraph_title(doc, idx):
    return doc.paragraphs[idx].text.strip()


def fix_chapter2(doc: Document) -> None:
    ch2 = find_heading1(doc, lambda t: t.startswith("2 Проект") or "Практическая" in t)
    if ch2 == -1:
        for i, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip().startswith("2.1 "):
                h = paragraph.insert_paragraph_before("2 Проектная часть")
                h.style = doc.styles["Heading 1"]
                break
    else:
        set_paragraph_text(doc.paragraphs[ch2], "2 Проектная часть")

    ch2 = find_heading1(doc, lambda t: t.startswith("2 Проект") or "Практическая" in t)
    ch3 = find_heading1(doc, lambda t: t.startswith("3 "))
    if ch2 == -1 or ch3 == -1:
        return

    h2s = []
    for i in range(ch2 + 1, ch3):
        paragraph = doc.paragraphs[i]
        if paragraph.style and paragraph.style.name == "Heading 2" and paragraph.text.strip().startswith("2."):
            h2s.append((i, paragraph.text.strip()))

    cut_from = None
    for start, title in h2s:
        if title.startswith("2.6 Разработка макета") or title.startswith("2.7") or title.startswith("2.8"):
            cut_from = start
            break
        if title.startswith("2.5.1") or title.startswith("2.5.2"):
            cut_from = start
            break

    if cut_from is not None:
        delete_section(doc, cut_from, ch3 - 1)

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text.startswith("2.5 Тестирование"):
            set_paragraph_text(paragraph, text.replace("2.5", "2.6", 1))


def apply_typography(doc: Document) -> None:
    ch1 = find_heading1(doc, lambda t: t.startswith("1 Аналит"))
    ch2 = find_heading1(doc, lambda t: t.startswith("2 Проект") or "Практическая" in t)
    intro = find_heading1(doc, lambda t: t.lower() == "введение")
    ch1_idx = find_heading1(doc, lambda t: t.startswith("1 Аналит"))

    for i, paragraph in enumerate(doc.paragraphs):
        style_name = paragraph.style.name if paragraph.style else "Normal"
        text = paragraph.text.strip()
        lower = text.lower()

        if style_name == "Heading 1":
            if lower in CENTER_TITLES:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.paragraph_format.page_break_before = lower in ("заключение", "библиография", "список используемой литературы")
                paragraph.paragraph_format.space_after = Pt(12)
                for run in paragraph.runs:
                    set_run_black(run, size=16, bold=True)
            elif text.startswith(("1 Аналит", "2 Проектная", "2 Практическая", "3 ")):
                paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                paragraph.paragraph_format.page_break_before = True
                paragraph.paragraph_format.space_after = Pt(12)
                for run in paragraph.runs:
                    set_run_black(run, size=16, bold=True)

        elif style_name in ("Heading 2", "Heading 3"):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.space_before = Pt(6)
            paragraph.paragraph_format.space_after = Pt(6)
            for run in paragraph.runs:
                set_run_black(run, size=14, bold=True)

        elif style_name == "Normal":
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.line_spacing = 1.5
            for run in paragraph.runs:
                set_run_black(run, size=14, bold=False)

    if intro != -1 and ch1_idx != -1:
        for i in range(intro + 1, ch1_idx):
            paragraph = doc.paragraphs[i]
            if paragraph.text.strip():
                for run in paragraph.runs:
                    set_run_black(run, size=14, bold=False)


def main() -> None:
    if not BAK.exists():
        shutil.copy2(SRC, BAK)
    doc = Document(str(BAK))

    cleanup_pre_intro(doc)
    rephrase_yellow(doc)
    fix_outdated_limitations(doc)
    restructure_chapter1(doc)
    fix_chapter2(doc)
    apply_typography(doc)

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            scrub_run_xml(run)
            try:
                run.font.color.rgb = RGBColor(0, 0, 0)
            except Exception:
                pass

    doc.save(str(SRC))
    shutil.copy2(SRC, OUT)
    print("Saved:", SRC)
    print("Copied to:", OUT)
    print("Backup:", BAK)


if __name__ == "__main__":
    main()
