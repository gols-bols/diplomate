from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

from resolve_diploma_v2 import resolve_diploma_v2


TASKS_SENTENCE = "Для достижения поставленной цели необходимо решить следующие задачи:"


def insert_paragraph_after(paragraph: Paragraph, text: str = "") -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    p = Paragraph(new_p, paragraph._parent)
    if text:
        p.add_run(text)
    return p


def delete_paragraph(p: Paragraph) -> None:
    el = p._element
    parent = el.getparent()
    if parent is not None:
        parent.remove(el)


def set_body_format(p: Paragraph, *, size: int = 14, first_indent: bool = True, center: bool = False) -> None:
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    fmt = p.paragraph_format
    fmt.line_spacing = 1.5
    fmt.first_line_indent = Cm(0 if center or not first_indent else 1.25)
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(0)
    fmt.page_break_before = False
    for run in p.runs:
        run.font.name = "Times New Roman"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        run.font.size = Pt(size)


def set_heading_format(p: Paragraph, *, size: int = 16) -> None:
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fmt = p.paragraph_format
    fmt.line_spacing = 1.5
    fmt.first_line_indent = Cm(0)
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(12)
    for run in p.runs:
        run.font.name = "Times New Roman"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        run.font.size = Pt(size)
        run.bold = True


def replace_dashes(text: str) -> str:
    return re.sub(r"\s*[-–—]\s*", " — ", text)


def is_numbered_list_line(text: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", text))


def is_hierarchical_numbering(text: str) -> bool:
    return bool(re.match(r"^\d+(?:\.\d+)+[\.)]?\s+", text))


def normalize_numbered_list_paragraph(paragraph: Paragraph, prev_paragraph: Paragraph | None = None, next_paragraph: Paragraph | None = None) -> None:
    text = paragraph.text or ""
    if not text.strip() or paragraph.style.name.startswith("Heading"):
        return

    if is_hierarchical_numbering(text):
        return

    if re.match(r"^\s*[-–—]\s+", text):
        set_text(paragraph, replace_dashes(text))
        return

    if is_numbered_list_line(text):
        prev_text = (prev_paragraph.text or "").strip() if prev_paragraph is not None else ""
        next_text = (next_paragraph.text or "").strip() if next_paragraph is not None else ""
        if (
            prev_text.endswith(":")
            or is_numbered_list_line(prev_text)
            or prev_text.startswith("— ")
            or re.match(r"^[-–—]\s+", prev_text)
            or is_numbered_list_line(next_text)
            or next_text.startswith("— ")
        ):
            new_text = re.sub(r"^\d+\.\s+", "— ", text, count=1)
            set_text(paragraph, replace_dashes(new_text))


def lowercase_list_markers(paragraph: Paragraph) -> None:
    if not paragraph.runs:
        return
    text = paragraph.text or ""
    m = re.match(r"^(\(?)([A-ZА-ЯЁ])([\)\.])?(\s|$)", text)
    if not m:
        return
    marker = m.group(0)
    normalized = f"{m.group(1)}{m.group(2).lower()}{m.group(3) or ''}{m.group(4)}"
    if normalized != marker and text.startswith(marker):
        run = paragraph.runs[0]
        run.text = run.text.replace(marker, normalized, 1)


def normalize_fonts(doc: Document) -> dict[str, int]:
    """14pt everywhere, 16pt only for Heading 1 / 'ГЛАВА'."""
    changed = 0
    kept_16 = 0
    wrong_16 = 0
    paragraphs = list(doc.paragraphs)

    for idx, p in enumerate(paragraphs):
        text = (p.text or "").strip()
        style = p.style.name if p.style else ""
        is_chapter = style == "Heading 1" or text.upper().startswith("ГЛАВА")

        for run in p.runs:
            # determine current size
            size = run.font.size.pt if run.font.size else None
            if is_chapter:
                if size != 16:
                    run.font.size = Pt(16)
                    changed += 1
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
                run.bold = True
                kept_16 += 1
            else:
                if size == 16:
                    wrong_16 += 1
                if size != 14:
                    run.font.size = Pt(14)
                    changed += 1
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
                run.bold = False
            if run.text:
                run.text = replace_dashes(run.text)

        if not is_chapter:
            prev_p = paragraphs[idx - 1] if idx > 0 else None
            next_p = paragraphs[idx + 1] if idx + 1 < len(paragraphs) else None
            normalize_numbered_list_paragraph(p, prev_p, next_p)
            lowercase_list_markers(p)

        if is_chapter and p.runs:
            set_heading_format(p, size=16)
        else:
            set_body_format(p, size=14, first_indent=True, center=False)

    return {"changed_runs": changed, "wrong_16_runs": wrong_16, "chapter_runs": kept_16}


def clean_and_insert_tasks_list(doc: Document) -> bool:
    """Find sentence and ensure a clean 5–7 item numbered list right after it."""
    idx = None
    for i, p in enumerate(doc.paragraphs):
        if TASKS_SENTENCE in (p.text or ""):
            idx = i
            break
    if idx is None:
        return False

    anchor = doc.paragraphs[idx]

    # delete following messed numbered items (up to next heading or 30 paras)
    to_delete: list[int] = []
    for j in range(idx + 1, min(idx + 35, len(doc.paragraphs))):
        t = (doc.paragraphs[j].text or "").strip()
        style = doc.paragraphs[j].style.name if doc.paragraphs[j].style else ""
        if style.startswith("Heading") or re.match(r"^[12]\.\d", t):
            break
        if re.match(r"^\d+\.", t) or "задач" in t.lower():
            to_delete.append(j)
    for j in reversed(to_delete):
        delete_paragraph(doc.paragraphs[j])

    tasks = [
        "Провести анализ предметной области и существующих решений (аналогов helpdesk-систем).",
        "Сформировать требования к системе заявок и определить роли пользователей и сценарии работы.",
        "Спроектировать архитектуру приложения и структуру базы данных (ER-модель и связи сущностей).",
        "Реализовать web-интерфейс и серверную часть системы на базе Laravel и MySQL.",
        "Разработать и проверить REST API для формализованного тестирования через Postman.",
        "Провести тестирование пользовательских и API-сценариев и устранить выявленные ошибки.",
        "Подготовить документацию, приложения со скриншотами и материалы для защиты.",
    ]

    last = anchor
    for n, item in enumerate(tasks, start=1):
        p = insert_paragraph_after(last, f"{n}. {item}")
        set_body_format(p, size=14, first_indent=True, center=False)
        last = p

    return True


def insert_comparison_if_missing(doc: Document) -> bool:
    text_all = "\n".join((p.text or "") for p in doc.paragraphs).lower()
    if "glpi" in text_all and "jira" in text_all and "сравн" in text_all:
        return False

    # Insert into 1.2 as small block
    idx = None
    for i, p in enumerate(doc.paragraphs):
        if re.match(r"^1\.2\.\s", (p.text or "").strip()):
            idx = i
            break
    if idx is None:
        return False

    anchor = doc.paragraphs[idx]
    block = [
        "Для обоснования собственной реализации были рассмотрены распространенные системы учета заявок.",
        "GLPI — open-source helpdesk с широкими возможностями (инвентаризация, категории, SLA), однако для учебного проекта "
        "и локальной демонстрации часто избыточен и требует длительной настройки.",
        "Jira Service Management — мощный сервисный продукт, удобный для крупных организаций, но предполагает платную модель "
        "и не позволяет наглядно показать собственные навыки проектирования и реализации системы.",
        "Разработанная система заявок ориентирована на внутренние обращения СПК: упрощенная роль‑модель, привязка к корпусу "
        "и кабинету, удобный web-интерфейс и REST API для проверки в Postman. Это обеспечивает баланс между функциональностью "
        "и демонстрационной ценностью дипломного проекта.",
    ]

    last = anchor
    for line in block:
        p = insert_paragraph_after(last, line)
        set_body_format(p, size=14, first_indent=True)
        last = p
    return True


def expand_1_3(doc: Document) -> bool:
    idx = None
    for i, p in enumerate(doc.paragraphs):
        if re.match(r"^1\.3\.\s", (p.text or "").strip()):
            idx = i
            break
    if idx is None:
        return False

    # if next heading is too close, expand
    next_heading = None
    for j in range(idx + 1, min(idx + 25, len(doc.paragraphs))):
        if (doc.paragraphs[j].style.name if doc.paragraphs[j].style else "").startswith("Heading") and re.match(
            r"^1\.\d", (doc.paragraphs[j].text or "").strip()
        ):
            next_heading = j
            break

    body_count = 0
    for j in range(idx + 1, next_heading or len(doc.paragraphs)):
        if (doc.paragraphs[j].text or "").strip():
            body_count += 1
    if body_count >= 3:
        return False

    anchor = doc.paragraphs[idx]
    paras = [
        "Информационные системы можно классифицировать по назначению и способу эксплуатации. В учебной и прикладной практике "
        "выделяют оперативные системы, ориентированные на регистрацию событий и обращений, управленческие системы для учета "
        "и контроля процессов, а также аналитические системы, предназначенные для отчетности и принятия решений.",
        "Разрабатываемый проект относится к классу внутренней web‑ориентированной оперативной информационной системы управления "
        "обращениями. Система используется через браузер, хранит данные в централизованной БД MySQL, поддерживает роли "
        "пользователь/менеджер/администратор и жизненный цикл заявки от создания до закрытия. Такой класс ИС соответствует "
        "задаче автоматизации внутренней службы заявок и удобен для демонстрации на защите.",
    ]

    last = anchor
    for text in paras:
        p = insert_paragraph_after(last, text)
        set_body_format(p, size=14, first_indent=True)
        last = p
    return True


def tune_file(path: Path) -> dict[str, object]:
    doc = Document(str(path))

    ok_tasks = clean_and_insert_tasks_list(doc)
    ok_cmp = insert_comparison_if_missing(doc)
    ok_13 = expand_1_3(doc)
    font_stats = normalize_fonts(doc)

    doc.save(str(path))
    # second save for Word compatibility
    doc2 = Document(str(path))
    doc2.save(str(path))

    return {"tasks_list": ok_tasks, "comparison": ok_cmp, "expand_1_3": ok_13, **font_stats}


def main() -> None:
    base = resolve_diploma_v2()
    final = base.with_name(base.stem + "_ФИНАЛ.docx")

    for p in (final, base):
        if not p.is_file():
            raise SystemExit(f"Нет файла: {p}")

    # backups
    shutil.copy2(final, final.with_name(final.stem + ".bak_tune.docx"))
    shutil.copy2(base, base.with_name(base.stem + ".bak_tune.docx"))

    stats_final = tune_file(final)
    # sync final -> base (base должен стать идентичен)
    sync_ok = True
    synced_path = base
    try:
        shutil.copy2(final, base)
    except PermissionError:
        sync_ok = False
        synced_path = base.with_name(base.stem + "_СИНХРОН.docx")
        shutil.copy2(final, synced_path)
    stats_base = {"synced_from_final": sync_ok, "synced_path": str(synced_path), "size": synced_path.stat().st_size}

    # verification: count 16pt in non-heading
    doc = Document(str(final))
    bad16 = 0
    for p in doc.paragraphs:
        style = p.style.name if p.style else ""
        txt = (p.text or "").strip()
        is_chapter = style == "Heading 1" or txt.upper().startswith("ГЛАВА")
        if is_chapter:
            continue
        for r in p.runs:
            if r.font.size and r.font.size.pt == 16:
                bad16 += 1
    print("OK")
    print("final_size", final.stat().st_size, "bad16_runs", bad16)
    print("final_stats", stats_final)
    # Avoid printing unicode paths (console encoding).
    print("base_synced_from_final", stats_base["synced_from_final"], "base_size", stats_base["size"])


if __name__ == "__main__":
    main()

