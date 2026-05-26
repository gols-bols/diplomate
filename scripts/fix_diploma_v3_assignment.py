#!/usr/bin/env python3
"""Fix diploma (3).docx per official assignment + reviewer marks."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from docx_cleanup import sanitize_paragraph_element

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs_archive" / "Диплом_отдельный_расширенный.docx"
OUT = ROOT / "docs" / "Диплом_отдельный_финал_60.docx"
BAK = SRC.with_suffix(".docx.bak")

CH1_H1 = "1. Анализ предметной области"
CH2_H1 = "2. Проектная часть"
CH3_H1 = "3. Экономическое обоснование"

CH1_ORDER = [
    "1.1. Сведения об организации",
    "1.2. Информационная и функциональная структура",
    "1.3. Классификация информационных систем (выбор класса ИС)",
    "1.4. Постановка задачи",
    "1.5. Обоснование выбора программных средств для реализации проекта",
]

CH1_SOURCE = {
    "1.1. Сведения об организации": ["1.8 Сведения об организации"],
    "1.2. Информационная и функциональная структура": [
        "1.1 Анализ предметной области",
        "1.13 Детализация процессов",
        "1.14 Модель пользователей",
        "1.2 Анализ существующих подходов",
    ],
    "1.3. Классификация информационных систем (выбор класса ИС)": [
        "1.9 Обзор аналогов",
        "1.11 Сравнительная оценка",
    ],
    "1.4. Постановка задачи": [
        "1.3 Формирование требований",
        "1.10 Постановка задачи",
    ],
    "1.5. Обоснование выбора программных средств для реализации проекта": [
        "1.4 Выбор технологического стека",
    ],
}

CH1_DELETE_PREFIXES = (
    "1.5 Обоснование архитектурных",
    "1.6 Анализ рисков",
    "1.7 Анализ требований к безопасности",
    "1.12 Выводы",
    "1.15 Требования к данным",
    "1.16 Дополнительные выводы",
    "1.17 Анализ ограничений",
    "1.18 Критерии оценки",
)

CLASSIFICATION_INTRO = (
    "Для проекта выбран класс внутренней web-ориентированной информационной системы учета заявок. "
    "Такие системы работают через браузер, используют централизованную базу данных MySQL, "
    "поддерживают роли пользователей и жизненный цикл обращения от регистрации до закрытия."
)

TOC_TEXT = """1. Анализ предметной области
1.1. Сведения об организации
1.2. Информационная и функциональная структура
1.3. Классификация информационных систем (выбор класса ИС)
1.4. Постановка задачи
1.5. Обоснование выбора программных средств для реализации проекта

2. Проектная часть
2.1. Проектирование архитектуры проекта (диаграммы, схема данных)
2.2. Разработка интерфейсов
2.3. Разработка клиентской части информационной системы
2.4. Разработка серверной части информационной системы
2.5. Тестирование информационной системы

3. Экономическое обоснование
3.1. Определение затрат на проектирование
3.2. Расчет экономической эффективности

ЗАКЛЮЧЕНИЕ
БИБЛИОГРАФИЯ
ПРИЛОЖЕНИЕ А
ПРИЛОЖЕНИЕ Б"""

YELLOW_OLD = (
    "Наиболее распространенной формой взаимодействия сотрудников и технической поддержки во многих "
    "учреждениях по-прежнему остается неформализованная передача проблем: устные обращения, "
    "телефонные звонки, сообщения в мессенджерах и электронная почта. Такой подход не обеспечивает "
    "единого учета обращений, затрудняет контроль сроков и не позволяет формировать статистику."
)
YELLOW_NEW = (
    "Во многих учреждениях обращения в техническую поддержку передаются неформализованно: устно, "
    "по телефону, через мессенджеры или электронную почту. При таком подходе сложно контролировать "
    "статус заявки, назначать исполнителя и анализировать повторяющиеся инциденты."
)


def scrub_run(run) -> None:
    r_pr = run._element.find(qn("w:rPr"))
    if r_pr is None:
        return
    for tag in ("w:highlight", "w:shd"):
        for el in list(r_pr.findall(qn(tag))):
            r_pr.remove(el)
    for el in list(r_pr.findall(qn("w:color"))):
        r_pr.remove(el)


def set_black(run, *, size=14, bold=False) -> None:
    scrub_run(run)
    run.font.name = "Times New Roman"
    run.font.color.rgb = RGBColor(0, 0, 0)
    run.font.size = Pt(size)
    run.bold = bold


def set_text(p, text: str) -> None:
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def remove_p(p) -> None:
    el = p._element
    parent = el.getparent()
    if parent is not None:
        parent.remove(el)


def find_h1(doc: Document, pred) -> int:
    for i, p in enumerate(doc.paragraphs):
        if p.style and p.style.name == "Heading 1" and pred(p.text.strip()):
            return i
    return -1


def find_ch3(doc: Document) -> int:
    return find_h1(
        doc,
        lambda t: bool(re.match(r"^3[\.\s]", t))
        or "Экономич" in t
        or "экономическ" in t.lower(),
    )


def find_conclusion(doc: Document) -> int:
    return find_h1(doc, lambda t: "заключение" in t.lower())


def ch2_list(doc: Document, start: int, end: int, prefix: str) -> list[tuple[int, str]]:
    items = []
    for i in range(start, end):
        p = doc.paragraphs[i]
        if p.style and p.style.name == "Heading 2":
            t = p.text.strip()
            if t.startswith(prefix):
                items.append((i, t))
    return items


def ch2_major_num(title: str) -> int | None:
    m = re.match(r"^2\.(\d+)", title.strip())
    return int(m.group(1)) if m else None


def delete_range(doc: Document, start: int, end: int) -> None:
    for i in range(end, start - 1, -1):
        remove_p(doc.paragraphs[i])


def move_section(doc: Document, start: int, end: int, after: int) -> None:
    els = [doc.paragraphs[i]._p for i in range(start, end + 1)]
    anchor = doc.paragraphs[after]._p
    for el in els:
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)
    cur = anchor
    for el in els:
        cur.addnext(el)
        cur = el


def match_source(title: str, patterns: list[str]) -> bool:
    return any(p in title for p in patterns)


def add_heading2(doc: Document, title: str):
    paragraph = doc.add_paragraph(title)
    for style_name in ("Heading 2", "Заголовок 2"):
        try:
            paragraph.style = doc.styles[style_name]
            return paragraph
        except KeyError:
            continue
    paragraph.style = doc.styles["Normal"]
    for run in paragraph.runs:
        set_black(run, size=14, bold=True)
    return paragraph


def rebuild_chapter1(doc: Document) -> None:
    ch1 = find_h1(doc, lambda t: "Аналит" in t or "Анализ предметной" in t or t.startswith("1 "))
    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    if ch1 == -1 or ch2 == -1:
        return

    set_text(doc.paragraphs[ch1], CH1_H1)

    sections = ch2_list(doc, ch1 + 1, ch2, "1.")
    ranges: list[tuple[int, int, str]] = []
    for idx, (start, title) in enumerate(sections):
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        ranges.append((start, end, title))

    # Move architecture to chapter 2 (before 2.1)
    for start, end, title in ranges:
        if title.startswith("1.5 Обоснование архитектурных"):
            for i in range(ch2 + 1, len(doc.paragraphs)):
                if doc.paragraphs[i].text.strip().startswith("2.1"):
                    move_section(doc, start, end, i - 1)
                    break
            break

    # Delete unwanted sections
    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    sections = ch2_list(doc, ch1 + 1, ch2, "1.")
    for idx in range(len(sections) - 1, -1, -1):
        start, title = sections[idx]
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        if any(title.startswith(p) for p in CH1_DELETE_PREFIXES):
            delete_range(doc, start, end)
            continue
        if title.startswith("1.9 ") or title.startswith("1.10 ") or title.startswith("1.11 "):
            delete_range(doc, start, end)

    # Collect blocks by source key
    ch1 = find_h1(doc, lambda t: "Анализ предметной" in t)
    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    sections = ch2_list(doc, ch1 + 1, ch2, "1.")
    grouped: dict[str, list] = {}
    for idx, (start, title) in enumerate(sections):
        end = sections[idx + 1][0] - 1 if idx + 1 < len(sections) else ch2 - 1
        # skip old subsection heading, keep body only
        grouped[title] = [doc.paragraphs[i]._p for i in range(start + 1, end + 1)]

    delete_range(doc, ch1 + 1, ch2 - 1)

    cur = doc.paragraphs[ch1]._p
    for new_title in CH1_ORDER:
        hp = add_heading2(doc, new_title)
        hel = hp._p
        hel.getparent().remove(hel)
        cur.addnext(hel)
        cur = hel

        if "1.3." in new_title:
            bp = doc.add_paragraph(CLASSIFICATION_INTRO)
            bel = bp._p
            bel.getparent().remove(bel)
            cur.addnext(bel)
            cur = bel

        for old_title, elements in grouped.items():
            if match_source(old_title, CH1_SOURCE[new_title]):
                for el in elements:
                    sanitize_paragraph_element(el)
                    cur.addnext(el)
                    cur = el


def fix_chapter2(doc: Document) -> None:
    ch2 = find_h1(doc, lambda t: t.startswith("2."))
    if ch2 == -1:
        for i, p in enumerate(doc.paragraphs):
            if p.text.strip().startswith("2.1 "):
                h = p.insert_paragraph_before(CH2_H1)
                h.style = doc.styles["Heading 1"]
                ch2 = i
                break
    else:
        set_text(doc.paragraphs[ch2], CH2_H1)

    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    ch3 = find_ch3(doc)
    if ch2 == -1 or ch3 == -1:
        return

    h2s = ch2_list(doc, ch2 + 1, ch3, "2.")
    for idx in range(len(h2s) - 1, -1, -1):
        start, title = h2s[idx]
        major = ch2_major_num(title)
        if major is not None and major >= 6:
            end = h2s[idx + 1][0] - 1 if idx + 1 < len(h2s) else ch3 - 1
            delete_range(doc, start, end)
        elif title.startswith("1.5 Обоснование архитектурных"):
            end = h2s[idx + 1][0] - 1 if idx + 1 < len(h2s) else ch3 - 1
            delete_range(doc, start, end)

    # Remove orphan subsections (e.g. moved 1.5 architecture block) and appendices in ch.2
    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    ch3 = find_ch3(doc)
    extras = []
    for i in range(ch2 + 1, ch3):
        p = doc.paragraphs[i]
        if p.style and p.style.name == "Heading 2":
            t = p.text.strip()
            if not t.startswith("2."):
                extras.append(i)
    for idx in reversed(extras):
        end = ch3 - 1
        for j in range(idx + 1, ch3):
            if doc.paragraphs[j].style and doc.paragraphs[j].style.name == "Heading 2":
                end = j - 1
                break
        delete_range(doc, idx, end)

    ch3 = find_ch3(doc)
    ch2 = find_h1(doc, lambda t: "Проект" in t or t.startswith("2."))
    for i in range(ch3 - 1, ch2, -1):
        t = doc.paragraphs[i].text.strip()
        if t.startswith("ПРИЛОЖЕНИЕ") or t.startswith("Приложение"):
            remove_p(doc.paragraphs[i])


def fix_titles_end(doc: Document) -> None:
    for p in doc.paragraphs:
        t = p.text.strip()
        if t == "Заключение":
            set_text(p, "ЗАКЛЮЧЕНИЕ")
        elif t == "Библиография":
            set_text(p, "БИБЛИОГРАФИЯ")
        elif t.startswith("Приложение А"):
            set_text(p, "ПРИЛОЖЕНИЕ А. Скриншоты структуры базы данных")
        elif t.startswith("Приложение Б"):
            set_text(p, "ПРИЛОЖЕНИЕ Б. Скриншоты проверки API в Postman")


def fix_chapter3(doc: Document) -> None:
    ch3 = find_ch3(doc)
    ch_end = find_conclusion(doc)
    if ch3 == -1:
        return
    set_text(doc.paragraphs[ch3], CH3_H1)

    h2s = ch2_list(doc, ch3 + 1, ch_end if ch_end != -1 else len(doc.paragraphs), "3.")
    for idx in range(len(h2s) - 1, -1, -1):
        start, title = h2s[idx]
        end = (
            h2s[idx + 1][0] - 1
            if idx + 1 < len(h2s)
            else (ch_end - 1 if ch_end != -1 else len(doc.paragraphs) - 1)
        )
        if title.startswith("3.1 Комплекс работ"):
            delete_range(doc, start, end)
        elif re.match(r"^3\.2\.\d", title):
            delete_range(doc, start, end)

    for p in doc.paragraphs:
        t = p.text.strip()
        if t.startswith("3.2 Определение затрат") or t.startswith("3.2 Определение"):
            set_text(p, "3.1. Определение затрат на проектирование")
        elif t.startswith("3.3 Оценка экономической") or t.startswith("3.3 Оценка"):
            set_text(p, "3.2. Расчет экономической эффективности")


def remove_duplicate_appendices(doc: Document) -> None:
    """Drop appendix blocks inside chapter 2; keep only at document end."""
    ch3 = find_ch3(doc)
    ch_end = find_conclusion(doc)
    if ch3 == -1:
        return
    end = ch_end if ch_end != -1 else len(doc.paragraphs)
    for i in range(ch3, end):
        t = doc.paragraphs[i].text.strip()
        if t.startswith("ПРИЛОЖЕНИЕ") or t.startswith("Приложение"):
            remove_p(doc.paragraphs[i])


def apply_typography(doc: Document) -> None:
    for i, p in enumerate(doc.paragraphs):
        style = p.style.name if p.style else "Normal"
        t = p.text.strip()
        low = t.lower()

        if style == "Heading 1":
            if low in ("перечень сокращений и обозначений", "содержание", "введение"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(12)
                for r in p.runs:
                    set_black(r, size=16, bold=True)
            elif low in ("заключение", "библиография") or t.startswith("ПРИЛОЖЕНИЕ") or t.startswith("Приложение"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.page_break_before = True
                p.paragraph_format.space_after = Pt(12)
                for r in p.runs:
                    set_black(r, size=16, bold=True)
            elif t.startswith(("1.", "2.", "3.")) and any(
                x in t for x in ("Анализ предметной", "Проектная", "Экономическое")
            ):
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.page_break_before = True
                p.paragraph_format.space_after = Pt(12)
                for r in p.runs:
                    set_black(r, size=16, bold=True)

        elif style in ("Heading 2", "Heading 3"):
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            for r in p.runs:
                set_black(r, size=14, bold=True)

        elif style == "Normal":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            for r in p.runs:
                set_black(r, size=14, bold=False)


def remove_intro_task_list(doc: Document) -> None:
    """Remove numbered task list in Введение (duplicate of 1.4, marked red)."""
    in_intro = False
    to_delete: list[int] = []
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if p.style and p.style.name == "Heading 1" and t == "Введение":
            in_intro = True
            continue
        if in_intro and p.style and p.style.name == "Heading 1":
            break
        if in_intro and re.match(r"^\d+\.\s", t):
            to_delete.append(i)
    for i in reversed(to_delete):
        remove_p(doc.paragraphs[i])


def cleanup_intro(doc: Document) -> None:
    cleanup_meta(doc)
    remove_intro_task_list(doc)
    for p in doc.paragraphs:
        if YELLOW_OLD in p.text:
            set_text(p, p.text.replace(YELLOW_OLD, YELLOW_NEW))
        if "пока отсутствуют вложения, комментарии" in p.text:
            set_text(
                p,
                "В текущей версии реализованы комментарии и история статусов; "
                "не реализованы вложения и email-уведомления.",
            )

    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t == "Оглавление будет сформировано при открытии документа в Word или LibreOffice.":
            set_text(p, "Введение\n\n" + TOC_TEXT)
            break
        if "1. Анализ предметной области" in t and "1.1. Сведения" in t and p.style.name == "Normal":
            set_text(p, "Введение\n\n" + TOC_TEXT)
            break

    for p in doc.paragraphs:
        if "неформализованная передача проблем" in p.text or "неформализованной передаче" in p.text:
            set_text(p, YELLOW_NEW)


def cleanup_meta(doc: Document) -> None:
    for i in reversed(range(min(30, len(doc.paragraphs)))):
        t = doc.paragraphs[i].text.strip()
        if t.startswith(("Тема:", "Объект исследования:", "Предмет исследования:")):
            remove_p(doc.paragraphs[i])


def main() -> None:
    if not BAK.exists():
        shutil.copy2(SRC, BAK)
    doc = Document(str(BAK))

    cleanup_intro(doc)
    rebuild_chapter1(doc)
    fix_chapter2(doc)
    fix_chapter3(doc)
    remove_duplicate_appendices(doc)
    fix_titles_end(doc)
    apply_typography(doc)

    for p in doc.paragraphs:
        for r in p.runs:
            scrub_run(r)
            try:
                r.font.color.rgb = RGBColor(0, 0, 0)
            except Exception:
                pass

    doc.save(str(SRC))
    shutil.copy2(SRC, OUT)
    print("OK:", SRC)
    print("Copy:", OUT)

    # fix_diploma всегда перезаписывает docx без рисунков — вставляем их сразу после копии
    import subprocess
    import sys

    scripts_dir = Path(__file__).resolve().parent
    for script in ("generate_figma_mockup_images.py", "generate_diploma_diagrams.py", "insert_all_diploma_figures.py"):
        subprocess.run([sys.executable, str(scripts_dir / script), "--force"], check=True, cwd=str(scripts_dir))
    print("Figures re-inserted into:", OUT)


if __name__ == "__main__":
    main()
