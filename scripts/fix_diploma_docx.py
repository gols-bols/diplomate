from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

from docx_figures import FigureCounter
from project_paths import MOCKUP_FIGURES


def set_text(paragraph: Paragraph, text: str) -> None:
    for run in paragraph.runs:
        run.text = ""
    if paragraph.runs:
        paragraph.runs[0].text = text
    else:
        paragraph.add_run(text)


def paragraph_after(paragraph: Paragraph, text: str = "", style: str | None = None) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    if style:
        set_paragraph_style(new_para, style)
    if text:
        new_para.add_run(text)
    return new_para


def delete_paragraph(paragraph: Paragraph) -> None:
    element = paragraph._element
    element.getparent().remove(element)
    paragraph._p = paragraph._element = None


def find_para(doc: Document, needle: str) -> Paragraph:
    def norm(s: str) -> str:
        import re

        s = (s or "").lower()
        s = s.replace("-", " ")
        s = s.replace("—", " ")
        s = s.replace("–", " ")
        s = re.sub(r"[^0-9a-zа-яё\s]", " ", s, flags=re.I)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    nneedle = norm(needle)
    # First pass: exact substring
    for p in doc.paragraphs:
        if needle in p.text:
            return p
    # Second pass: normalized substring match
    for p in doc.paragraphs:
        if nneedle and nneedle in norm(p.text):
            return p
    # Third pass: try regex search (case-insensitive)
    import re

    try:
        pattern = re.compile(needle, re.IGNORECASE)
        for p in doc.paragraphs:
            if pattern.search(p.text or ""):
                return p
    except re.error:
        pass

    # If not found, raise with helpful message
    raise ValueError(f"paragraph not found: {needle}")


def remove_highlights_and_colored_marks(doc: Document) -> None:
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            rpr = run._element.find(qn("w:rPr"))
            if rpr is None:
                continue
            for tag in ("w:highlight",):
                for node in list(rpr.findall(qn(tag))):
                    rpr.remove(node)
            # Remove explicit color elements that may produce blue/colored headings
            color = rpr.find(qn("w:color"))
            if color is not None:
                rpr.remove(color)


def normalize_heading_colors(doc: Document) -> None:
    """Ensure heading paragraphs use black text color."""
    for p in doc.paragraphs:
        style = getattr(p.style, "name", "")
        if style.startswith("Heading") or p.text.strip().upper().startswith("ГЛАВА"):
            for run in p.runs:
                try:
                    run.font.color.rgb = RGBColor(0, 0, 0)
                except Exception:
                    pass


def remove_drawing_only_paragraphs(doc: Document) -> None:
    for p in list(doc.paragraphs):
        has_drawing = bool(p._element.findall(".//" + qn("w:drawing")))
        if has_drawing and not p.text.strip():
            delete_paragraph(p)


def remove_empty_headings(doc: Document) -> None:
    for p in list(doc.paragraphs):
        style = getattr(p.style, "name", "")
        if style.startswith("Heading") and not p.text.strip():
            delete_paragraph(p)


def set_heading_spacing(doc: Document) -> None:
    for style_name in ("Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        try:
            style = doc.styles[style_name]
            style.paragraph_format.space_after = Pt(0)
        except KeyError:
            pass
    for p in doc.paragraphs:
        style = getattr(p.style, "name", "")
        if style.startswith("Heading"):
            p.paragraph_format.space_after = Pt(0)


def iter_paragraphs(doc: Document):
    yield from doc.paragraphs
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs


def replace_dashes(text: str) -> str:
    if re.match(r"^\s*[-–—]\s+", text):
        return re.sub(r"^\s*[-–—]\s*", "", text).strip()
    if is_numbered_list_line(text) or is_hierarchical_numbering(text):
        return re.sub(r"^\s*\d+(?:\.\d+)*[\.\)]?\s*", "", text).strip()
    return text.strip()


def apply_list_style(paragraph: Paragraph) -> None:
    for style_name in ("List Bullet", "List Bullet 2", "Маркированный", "Маркированный список"):
        try:
            paragraph.style = style_name
            return
        except Exception:
            continue


def is_numbered_list_line(text: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", text))


def is_hierarchical_numbering(text: str) -> bool:
    return bool(re.match(r"^\d+(?:\.\d+)+[\.)]?\s+", text))


def normalize_numbered_list_paragraph(paragraph: Paragraph, prev_paragraph: Paragraph | None = None, next_paragraph: Paragraph | None = None) -> None:
    text = paragraph.text or ""
    style_name = getattr(paragraph.style, "name", "")
    if not text.strip() or style_name.startswith("Heading") or style_name.startswith("Заголовок"):
        return

    if is_hierarchical_numbering(text):
        return

    if re.match(r"^\s*[-–—]\s+", text):
        item_text = replace_dashes(text)
        set_text(paragraph, item_text)
        apply_list_style(paragraph)
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
            item_text = replace_dashes(text)
            set_text(paragraph, item_text)
            apply_list_style(paragraph)


def lowercase_list_markers(paragraph: Paragraph) -> None:
    if not paragraph.runs:
        return
    text = paragraph.text or ""
    m = re.match(r"^(\(?)([A-ZА-ЯЁ])([\)\.]?)(\s|$)", text)
    if not m:
        return
    new_marker = f"{m.group(1)}{m.group(2).lower()}{m.group(3)}{m.group(4)}"
    if text.startswith(m.group(0)) and new_marker != m.group(0):
        first = paragraph.runs[0]
        first.text = first.text.replace(m.group(0), new_marker, 1)


def normalize_doc_fonts_and_bold(doc: Document) -> None:
    paragraphs = list(iter_paragraphs(doc))
    for idx, paragraph in enumerate(paragraphs):
        prev_paragraph = paragraphs[idx - 1] if idx > 0 else None
        next_paragraph = paragraphs[idx + 1] if idx + 1 < len(paragraphs) else None
        style = getattr(paragraph.style, "name", "")
        is_heading = style.startswith("Heading") or paragraph.text.strip().upper().startswith("ГЛАВА")
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            try:
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
            except Exception:
                pass
            run.bold = bool(is_heading)
        # Preserve existing list formatting and markers in the original document.


def body_index(doc: Document, paragraph: Paragraph) -> int:
    body = doc._body._element
    return list(body).index(paragraph._p)


def move_block_before(doc: Document, start_text: str, end_before_text: str, before_text: str) -> None:
    start = find_para(doc, start_text)
    end = find_para(doc, end_before_text)
    before = find_para(doc, before_text)
    body = doc._body._element
    children = list(body)
    start_i = children.index(start._p)
    end_i = children.index(end._p)
    block = children[start_i:end_i]
    for element in block:
        body.remove(element)
    target_i = list(body).index(before._p)
    for offset, element in enumerate(block):
        body.insert(target_i + offset, element)


def move_block_after(doc: Document, start_text: str, end_before_text: str, after_text: str) -> None:
    start = find_para(doc, start_text)
    end = find_para(doc, end_before_text)
    after = find_para(doc, after_text)
    body = doc._body._element
    children = list(body)
    start_i = children.index(start._p)
    end_i = children.index(end._p)
    block = children[start_i:end_i]
    for element in block:
        body.remove(element)
    target_i = list(body).index(after._p) + 1
    for offset, element in enumerate(block):
        body.insert(target_i + offset, element)


def remove_paragraph_range(doc: Document, start_para: Paragraph, end_para: Paragraph) -> None:
    """Remove all paragraphs from start_para up to (but not including) end_para."""
    body = doc._body._element
    children = list(body)
    start_i = children.index(start_para._p)
    end_i = children.index(end_para._p)
    for element in children[start_i:end_i]:
        body.remove(element)


def add_caption_after(paragraph: Paragraph, text: str) -> Paragraph:
    p = paragraph_after(paragraph, text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
    return p


def add_picture_after(paragraph: Paragraph, image: Path, width_cm: float = 14.0) -> Paragraph:
    p = paragraph_after(paragraph)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image), width=Cm(width_cm))
    return p


def add_figure_after(paragraph: Paragraph, image: Path, caption: str, description: str | None = None) -> Paragraph:
    pic = add_picture_after(paragraph, image)
    cap = add_caption_after(pic, caption)
    if description:
        desc = paragraph_after(cap, description)
        desc.paragraph_format.first_line_indent = Cm(1.25)
        return desc
    return cap


def paragraph_before(paragraph: Paragraph, text: str = "", style: str | None = None) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addprevious(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    if style:
        set_paragraph_style(new_para, style)
    if text:
        new_para.add_run(text)
    return new_para


def set_paragraph_style(paragraph: Paragraph, style: str | None) -> None:
    if style is None:
        return
    try:
        paragraph.style = style
    except Exception:
        # Some documents may have style objects available only through iteration.
        for s in paragraph.part.styles:
            if getattr(s, "type", None) and s.type.name == "PARAGRAPH" and getattr(s, "name", None) == style:
                paragraph.style = s
                return
        paragraph.style = style


def add_picture_before(paragraph: Paragraph, image: Path, width_cm: float = 14.0) -> Paragraph:
    p = paragraph_before(paragraph)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image), width=Cm(width_cm))
    return p


def add_figure_before(paragraph: Paragraph, image: Path, caption: str, description: str | None = None) -> Paragraph:
    pic = add_picture_before(paragraph, image)
    cap = add_caption_after(pic, caption)
    if description:
        desc = paragraph_after(cap, description)
        desc.paragraph_format.first_line_indent = Cm(1.25)
        return desc
    return cap


def paragraph_has_picture(paragraph: Paragraph) -> bool:
    if paragraph is None:
        return False
    if paragraph._element.findall('.//' + qn('w:drawing')):
        return True
    if paragraph._element.findall('.//' + qn('wp:inline')):
        return True
    if paragraph._element.findall('.//' + qn('wp:anchor')):
        return True
    return False


def next_paragraph(paragraph: Paragraph) -> Paragraph | None:
    nxt = paragraph._element.getnext()
    while nxt is not None:
        if nxt.tag == qn('w:p'):
            return Paragraph(nxt, paragraph._parent)
        nxt = nxt.getnext()
    return None


def find_nearest_picture_paragraph(paragraph: Paragraph, max_lookahead: int = 4) -> Paragraph | None:
    current = next_paragraph(paragraph)
    looked = 0
    while current is not None and looked < max_lookahead:
        if paragraph_has_picture(current):
            return current
        current = next_paragraph(current)
        looked += 1
    return None


def insert_diagram_if_missing(doc: Document, anchor_text: str, image: Path, caption: str) -> None:
    anchor = find_para(doc, anchor_text)
    if find_nearest_picture_paragraph(anchor) is None:
        add_figure_after(anchor, image, caption)


def insert_diagram_before_caption_if_missing(doc: Document, caption_text: str, image: Path) -> None:
    try:
        caption_para = find_para(doc, caption_text)
    except ValueError:
        return
    prev = previous_paragraph(caption_para)
    if prev is None or not paragraph_has_picture(prev):
        add_picture_before(caption_para, image)


def previous_paragraph(paragraph: Paragraph) -> Paragraph | None:
    prev = paragraph._element.getprevious()
    while prev is not None:
        if prev.tag == qn("w:p"):
            return Paragraph(prev, paragraph._parent)
        prev = prev.getprevious()
    return None


def max_figure_number(doc: Document) -> int:
    maximum = 0
    for p in doc.paragraphs:
        match = re.search(r"Рисунок\s+(\d+)", p.text or "")
        if match:
            maximum = max(maximum, int(match.group(1)))
    return maximum


def insert_screenshot_mockups_as_23(doc: Document) -> None:
    try:
        anchor = find_para(doc, "2.4.")
    except ValueError:
        return

    # Create a subsection 2.3.3 within the client part for interface mockups.
    heading = paragraph_before(anchor, "2.3.3. Скриншоты макетов интерфейса", style="Heading 3")
    intro = paragraph_after(heading, "Ниже приведены макеты основных экранов веб-приложения: авторизация, журнал заявок, создание и карточка обращения.")
    intro.paragraph_format.first_line_indent = Cm(1.25)

    current = intro
    next_num = max_figure_number(doc)
    for image_path, title, description in MOCKUP_FIGURES:
        next_num += 1
        caption = f"Рисунок {next_num} — {title}"
        description_text = description.format(n=next_num)
        current = add_figure_after(current, image_path, caption, description_text)


def clear_block_between(doc: Document, start_text: str, end_before_text: str, keep_start: bool = True) -> Paragraph:
    start = find_para(doc, start_text)
    end = find_para(doc, end_before_text)
    body = doc._body._element
    children = list(body)
    start_i = children.index(start._p)
    end_i = children.index(end._p)
    remove = children[start_i + (1 if keep_start else 0):end_i]
    for element in remove:
        body.remove(element)
    return start


def add_code_listing_after(paragraph: Paragraph, title: str, code: str, max_lines: int | None = None) -> Paragraph:
    # Treat code listings like figures: use figure caption style for the title
    cap_text = title.replace("Листинг", "Рисунок") if "Листинг" in title else title
    title_p = add_caption_after(paragraph, cap_text)

    lines = code.splitlines()
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines] + ["// ... остальная часть контроллера содержит обработку вложений, экспорта и истории изменений ..."]

    current = title_p
    for line in lines:
        p = paragraph_after(current, line)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        for r in p.runs:
            r.font.name = "Courier New"
            r.font.size = Pt(9)
        current = p
    return current


def remove_appendix_screenshots(doc: Document) -> None:
    for p in list(doc.paragraphs):
        if p.text.strip().startswith("ПРИЛОЖЕНИЕ 2. Интерфейс системы заявок"):
            body = doc._body._element
            children = list(body)
            start_i = children.index(p._p)
            # Keep final section properties.
            for element in children[start_i:-1]:
                body.remove(element)
            return


def is_heading_paragraph(paragraph: Paragraph) -> bool:
    style_name = getattr(paragraph.style, "name", "")
    return style_name.startswith("Heading") or style_name.startswith("Заголовок")


def normalize_heading_numbers(text: str) -> list[int] | None:
    m = re.match(r"^\s*(\d+(?:\.\d+)*)", text or "")
    if not m:
        return None
    return [int(x) for x in m.group(1).split(".") if x.isdigit()]


def remove_heading_section(doc: Document, section_prefix: str) -> bool:
    """Remove a heading and following block that belongs to the same numbered section.
    Returns True if something was removed."""
    start_para = next((p for p in doc.paragraphs if section_prefix in (p.text or "")), None)
    if start_para is None:
        return False

    start_nums = normalize_heading_numbers(start_para.text)
    body = doc._body._element
    children = list(body)
    start_i = children.index(start_para._p)
    end_i = len(children)

    # walk forward until we hit a heading that is not a child of this section
    i = start_i + 1
    while i < len(children):
        cand = Paragraph(children[i], start_para._parent)
        if is_heading_paragraph(cand):
            nums = normalize_heading_numbers(cand.text)
            if nums is None:
                end_i = i
                break
            # if the next heading is at same or higher level and not nested under start_nums
            if start_nums is None:
                end_i = i
                break
            if len(nums) <= len(start_nums) and nums != start_nums[: len(nums)]:
                end_i = i
                break
            if len(nums) > len(start_nums) and nums[: len(start_nums)] != start_nums:
                end_i = i
                break
        i += 1

    for element in children[start_i:end_i]:
        body.remove(element)
    return True


def remove_section_233(doc: Document) -> None:
    """Remove section 2.3.3 or fallback 2.2.3 (screenshots without actual images)."""
    if remove_heading_section(doc, "2.3.3"):
        return
    remove_heading_section(doc, "2.2.3")


def remove_existing_controller_note(doc: Document) -> None:
    """Remove previously inserted note paragraph to avoid duplication."""
    for p in list(doc.paragraphs):
        if "Ниже приведены основные листинги контроллеров" in (p.text or ""):
            delete_paragraph(p)


def remove_existing_controller_code(doc: Document) -> None:
    """Remove previously inserted controller code blocks and their captions."""
    patterns = [
        "app/http/controllers/authcontroller.php",
        "app/http/controllers/ticketcontroller.php",
    ]
    paragraphs = list(doc.paragraphs)
    indices_to_remove: set[int] = set()

    for i, p in enumerate(paragraphs):
        lower = (p.text or "").lower()
        if any(pat in lower for pat in patterns):
            # remove until next heading or until a fresh caption that is not a controller caption
            j = i + 1
            while j < len(paragraphs):
                q = paragraphs[j]
                if is_heading_paragraph(q):
                    break
                qt = (q.text or "").strip()
                if qt.startswith("Рисунок") or qt.startswith("Листинг"):
                    # if it's another caption that doesn't mention controller files, stop
                    lqt = qt.lower()
                    if not any(pat in lqt for pat in patterns):
                        break
                j += 1
            indices_to_remove.update(range(i, j))

    for idx in sorted(indices_to_remove, reverse=True):
        if idx < len(doc.paragraphs):
            delete_paragraph(doc.paragraphs[idx])





def remove_duplicate_code_listings(doc: Document) -> None:
    """Remove duplicate code listings in section 2.4 server development."""
    listings = []  # List of (title_idx, block_end_idx, first_code_line)
    i = 0
    while i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        if p.text.strip().startswith("Листинг"):
            title_idx = i
            j = i + 1
            first_code_line = ""
            while j < len(doc.paragraphs):
                q = doc.paragraphs[j]
                if q.text.strip().startswith("Листинг"):
                    break
                if is_heading_paragraph(q) and j > i + 1:
                    break
                if not first_code_line and q.text.strip() and not q.text.strip().startswith("Листинг"):
                    first_code_line = q.text.strip()[:60]
                j += 1
            listings.append((title_idx, j, first_code_line))
            i = j
        else:
            i += 1

    seen_signatures = {}
    indices_to_remove = set()
    for title_idx, block_end, first_line in listings:
        sig = first_line
        if sig in seen_signatures:
            indices_to_remove.update(range(title_idx, block_end))
        else:
            seen_signatures[sig] = (title_idx, block_end)

    for idx in sorted(indices_to_remove, reverse=True):
        if idx < len(doc.paragraphs):
            delete_paragraph(doc.paragraphs[idx])




def main() -> None:
    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    root = Path(sys.argv[3])
    shutil.copy2(source, output)

    doc = Document(str(output))

    # Basic cleanup and formatting required by the methodology.
    remove_drawing_only_paragraphs(doc)
    remove_empty_headings(doc)
    set_heading_spacing(doc)

    # Section order from the individual assignment: 1.4 is tools choice, 1.5 is task statement.
    try:
        move_block_before(
            doc,
            "1.5. Обоснование выбора программных средств",
            "2. Проектная часть",
            "1.4. Постановка задачи",
        )
        try:
            set_text(find_para(doc, "1.5. Обоснование выбора программных средств"), "1.4. Обоснование выбора программных средств для создания системы заявок")
        except Exception:
            print("Warning: unable to set specific text for 1.5 heading (not found exactly)")
        try:
            set_text(find_para(doc, "1.4. Постановка задачи"), "1.5. Постановка задачи")
        except Exception:
            print("Warning: unable to set specific text for 1.4 heading (not found exactly)")
    except Exception:
        print("Warning: could not move block for 1.5 -> 1.4 reordering; continuing")

    # Reorder server and testing subsections.
    try:
        move_block_before(doc, "2.4.1 Организация API", "2.5. Тестирование", "2.4.3 Реализация ролевой модели")
    except Exception:
        print("Warning: could not move block for 2.4.1 -> 2.4.3; continuing")
    try:
        move_block_before(doc, "2.5.1 Методика тестирования", "3. Экономическое обоснование", "2.5.3 Набор тест-кейсов")
    except Exception:
        print("Warning: could not move block for 2.5.1 -> 2.5.3; continuing")

    # Remove section 2.3.3 (screenshots) - there are no actual screenshot images to display.
    try:
        remove_section_233(doc)
    except Exception:
        print("Warning: could not remove section 2.3.3; continuing")

    # Ensure referenced diagrams exist; do not duplicate existing images.
    try:
        insert_diagram_if_missing(doc, "На рисунке 1.1", root / "docs" / "diagram_images" / "diagram_use_case.png", "Рисунок 1.1 — Диаграмма вариантов использования системы заявок")
    except Exception:
        print("Warning: could not insert diagram 1.1; continuing")
    try:
        insert_diagram_before_caption_if_missing(doc, "Рисунок 1.2 — Информационная структура системы заявок", root / "docs" / "diagram_images" / "diagram_db_users.png")
        insert_diagram_before_caption_if_missing(doc, "Рисунок 1.3 — Функциональные связи пользователей и заявок", root / "docs" / "diagram_images" / "diagram_db_tickets.png")
    except Exception:
        print("Warning: could not insert diagrams 1.2/1.3; continuing")
    try:
        insert_diagram_if_missing(doc, "На рисунке 2.2", root / "docs" / "diagram_images" / "diagram_er.png", "Рисунок 2.2 — ER-модель базы данных проекта")
    except Exception:
        print("Warning: could not insert diagram 2.2; continuing")
    try:
        insert_diagram_if_missing(doc, "На рисунке 2.3", root / "docs" / "diagram_images" / "diagram_architecture.png", "Рисунок 2.3 — Трехуровневая архитектура web-приложения")
    except Exception:
        print("Warning: could not insert diagram 2.3; continuing")
    try:
        insert_screenshot_mockups_as_23(doc)
    except Exception:
        print("Warning: could not insert mockups 2.3.3; continuing")

    # Add controller code near its description instead of leaving it only in appendices.
    # Add controller code near its description instead of leaving it only in appendices.
    # Remove any previously inserted controller note/code to avoid duplicates.
    try:
        remove_existing_controller_note(doc)
        remove_existing_controller_code(doc)
    except Exception:
        pass
    
    auth_code = (root / "app" / "Http" / "Controllers" / "AuthController.php").read_text(encoding="utf-8")
    ticket_code = (root / "app" / "Http" / "Controllers" / "TicketController.php").read_text(encoding="utf-8")
    anchor = find_para(doc, "Это решение устранило типичную проблему")
    note = paragraph_after(anchor, "Ниже приведены основные листинги контроллеров, так как именно они реализуют описанную серверную логику авторизации, просмотра, создания и обработки заявок.")
    current = add_code_listing_after(note, "Листинг 1 — app/Http/Controllers/AuthController.php", auth_code)
    current = add_code_listing_after(current, "Листинг 2 — фрагмент app/Http/Controllers/TicketController.php", ticket_code, max_lines=170)

    # Remove duplicated screenshot appendix now that screenshots are in the main body.
    remove_appendix_screenshots(doc)

    # Remove duplicate code listings in section 2.4 server development.
    try:
        remove_duplicate_code_listings(doc)
    except Exception as e:
        print(f"Warning: could not remove duplicate code listings: {e}; continuing")

    remove_highlights_and_colored_marks(doc)
    normalize_doc_fonts_and_bold(doc)
    # Ensure headings are rendered in black and lists are normalized
    normalize_heading_colors(doc)
    # Normalize list-like paragraphs throughout the document
    paragraphs = list(iter_paragraphs(doc))
    for idx, p in enumerate(paragraphs):
        prev_p = paragraphs[idx - 1] if idx > 0 else None
        next_p = paragraphs[idx + 1] if idx + 1 < len(paragraphs) else None
        try:
            normalize_numbered_list_paragraph(p, prev_p, next_p)
            lowercase_list_markers(p)
        except Exception:
            continue
    set_heading_spacing(doc)

    doc.save(str(output))
    print(output)


if __name__ == "__main__":
    main()
