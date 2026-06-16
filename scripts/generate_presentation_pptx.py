from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = ROOT / "scripts" / "_pptxlib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from pptx import Presentation  # type: ignore
from pptx.dml.color import RGBColor  # type: ignore
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR  # type: ignore
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR  # type: ignore
from pptx.util import Inches, Pt  # type: ignore


OUTPUT = ROOT / "docs" / "Презентация_курсовая_диаграммы.pptx"
# Use final processed version with em-dashes and no list styles
DOCX_SOURCE = ROOT / "docs" / "Диплом - правки_исправлено_final6.docx"

BG = RGBColor(247, 240, 231)
PANEL = RGBColor(255, 251, 245)
ACCENT = RGBColor(142, 74, 42)
ACCENT_SOFT = RGBColor(224, 196, 164)
TEXT = RGBColor(35, 27, 20)
MUTED = RGBColor(108, 92, 73)
LINE = RGBColor(220, 203, 182)
GREEN = RGBColor(115, 144, 123)


def set_background(slide) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG


def add_header(slide, title: str, tag: str, index: int, total: int) -> None:
    set_background(slide)

    band = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.55)
    )
    band.fill.solid()
    band.fill.fore_color.rgb = ACCENT
    band.line.fill.background()

    tag_box = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(10.55), Inches(0.82), Inches(2.2), Inches(0.42)
    )
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = ACCENT_SOFT
    tag_box.line.fill.background()
    tf = tag_box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = tag
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = ACCENT

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(10.8), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.name = "Times New Roman"
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = TEXT

    footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.8), Inches(0.25))
    tf = footer.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f"Слайд {index} / {total}"
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.color.rgb = MUTED


def add_card(slide, left: float, top: float, width: float, height: float, title: str | None = None):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = PANEL
    shape.line.color.rgb = LINE
    shape.line.width = Pt(1.2)

    if title:
        box = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.14), Inches(width - 0.44), Inches(0.35))
        tf = box.text_frame
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title
        run.font.name = "Times New Roman"
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = ACCENT

    return shape


def add_bullets(slide, left: float, top: float, width: float, height: float, bullets: list[str], font_size: int = 20) -> None:
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = MSO_VERTICAL_ANCHOR.TOP
    tf.clear()

    for idx, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = bullet
        p.level = 0
        p.alignment = PP_ALIGN.LEFT
        p.font.name = "Times New Roman"
        p.font.size = Pt(font_size)
        p.font.color.rgb = TEXT
        p.line_spacing = 1.15
        p.space_after = Pt(10)
        p.bullet = True


def add_paragraph(slide, left: float, top: float, width: float, height: float, text: str, size: int = 20, color=TEXT, bold=False, align=PP_ALIGN.LEFT) -> None:
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_arrow(slide, x1: float, y1: float, x2: float, y2: float) -> None:
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(x1),
        Inches(y1),
        Inches(x2),
        Inches(y2),
    )
    connector.line.color.rgb = ACCENT
    connector.line.width = Pt(2.2)
    connector.line.end_arrowhead = True


def add_box(slide, left: float, top: float, width: float, height: float, text: str, fill_rgb=ACCENT_SOFT, text_rgb=TEXT, font_size=18) -> None:
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    shape.line.color.rgb = ACCENT
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.name = "Times New Roman"
    run.font.size = Pt(font_size)
    run.font.bold = True
    run.font.color.rgb = text_rgb


def slide_title(prs: Presentation, total: int) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide)

    band = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.72)
    )
    band.fill.solid()
    band.fill.fore_color.rgb = ACCENT
    band.line.fill.background()

    add_paragraph(
        slide,
        0.8,
        1.2,
        11.4,
        1.5,
        "Разработка информационной системы управления заявками",
        size=30,
        bold=True,
    )
    add_paragraph(
        slide,
        0.82,
        2.35,
        10.8,
        1.2,
        "Курсовой проект по разработке web-приложения на Laravel с использованием MySQL и Git.",
        size=21,
        color=MUTED,
    )

    add_card(slide, 0.82, 4.2, 5.0, 1.45, "Основные технологии")
    add_bullets(slide, 1.05, 4.65, 4.55, 0.9, ["Laravel 11", "PHP 8.2", "MySQL", "Git"], font_size=19)

    add_card(slide, 6.2, 4.2, 6.1, 1.45, "Назначение проекта")
    add_paragraph(
        slide,
        6.45,
        4.7,
        5.5,
        0.7,
        "Централизованный учет, просмотр и сопровождение внутренних заявок пользователей.",
        size=19,
    )

    add_paragraph(slide, 0.82, 6.95, 12.0, 0.25, f"Слайд 1 / {total}", size=12, color=MUTED, align=PP_ALIGN.RIGHT)


def load_toc_from_docx(path: Path) -> list[tuple[str, list[str]]]:
    if not path.exists():
        return []

    sections: list[tuple[str, list[str]]] = []
    document = Document(path)
    for paragraph in document.paragraphs:
        style_name = paragraph.style.name if paragraph.style is not None else ""
        if not (style_name.startswith("Heading") or style_name.startswith("Заголовок")):
            continue

        text = paragraph.text.strip()
        if not text or text in ("Содержание", "Библиография", "ПРИЛОЖЕНИЕ 1", "ПРИЛОЖЕНИЕ 2"):
            continue

        parts = style_name.split()
        if len(parts) != 2 or not parts[1].isdigit():
            continue

        level = int(parts[1])
        if level == 1:
            sections.append((text, []))
        elif level == 2 and sections:
            sections[-1][1].append(text)

    return sections


def load_toc_structure(path: Path) -> list[tuple[str, list[str]]]:
    if path.suffix == ".docx" and path.exists():
        toc = load_toc_from_docx(path)
        if toc:
            return toc
        path = ROOT / "scripts" / "diploma_v2_headings.txt"

    if not path.exists():
        return []

    sections: list[tuple[str, list[str]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) != 3 or parts[0] != "Heading":
            continue

        level = parts[1]
        title = parts[2].strip()
        if title in ("Содержание", "Библиография", "ПРИЛОЖЕНИЕ 1", "ПРИЛОЖЕНИЕ 2"):
            continue

        if level == "1":
            sections.append((title, []))
        elif level == "2" and sections:
            sections[-1][1].append(title)

    return sections


def normalize_agenda_title(title: str) -> str:
    return re.sub(r"^\d+\.\s*", "", title).strip()


def select_agenda_items(toc: list[tuple[str, list[str]]]) -> list[str]:
    if not toc:
        return [
            "Введение",
            "Анализ предметной области",
            "Основная часть",
            "Экономическое обоснование",
            "Заключение",
        ]

    agenda = []
    for title, _subsections in toc:
        low = title.lower()
        if "скрин" in low or "макет" in low:
            continue
        if title in ("Введение", "Заключение", "Экономическое обоснование"):
            agenda.append(title)
        elif title.startswith(("1.", "2.", "3.")):
            agenda.append(normalize_agenda_title(title))

    if len(agenda) > 6:
        return agenda[:6]
    return agenda


def slide_contents(prs: Presentation, total: int, index: int, agenda: list[str]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Содержание", "Оглавление", index, total)
    add_bullets(slide, 1.0, 1.8, 11.2, 4.8, agenda, font_size=18)


def slide_topic(prs: Presentation, title: str, tag: str, bullets: list[str], index: int, total: int, font_size: int = 20) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, title, tag, index, total)
    add_bullets(slide, 1.0, 2.0, 11.2, 4.8, bullets, font_size=font_size)


def slide_images(prs: Presentation, title: str, tag: str, images: list[tuple[Path, str]], index: int, total: int) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, title, tag, index, total)
    x_positions = [0.7, 7.0]
    y_positions = [1.9, 4.2]
    for idx, (img_path, caption) in enumerate(images):
        x = x_positions[idx % 2]
        y = y_positions[idx // 2]
        slide.shapes.add_picture(str(img_path), Inches(x), Inches(y), width=Inches(4.3))
        add_paragraph(slide, x, y + 2.25, 4.3, 0.28, caption, size=16, color=ACCENT, align=PP_ALIGN.CENTER)


def slide_final(prs: Presentation, total: int) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Заключение", "Выводы", total, total)
    add_bullets(
        slide,
        1.0,
        2.0,
        11.2,
        4.8,
        [
            "Разработано web-приложение управления заявками на Laravel.",
            "Интерфейс адаптирован для демонстрации и защиты проекта.",
            "Серверная часть реализует роли, валидацию и локальное развертывание.",
            "Показатель эффективности: автоматизация учета заявок и снижение ручных затрат.",
        ],
        font_size=19,
    )


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    toc = load_toc_structure(DOCX_SOURCE)
    agenda = select_agenda_items(toc)

    total = 10  # Updated: added diagram slides
    slide_title(prs, total)
    slide_contents(prs, total, 2, agenda)
    slide_topic(
        prs,
        "Введение",
        "Цель и задачи",
        [
            "Актуальность: автоматизация учета внутренних заявок в организации.",
            "Цель: создать web-систему управления заявками на Laravel с MySQL.",
            "Задачи: анализ, проектирование, клиентская и серверная часть, тестирование.",
        ],
        3,
        total,
    )
    slide_topic(
        prs,
        "Анализ предметной области",
        "Исследование",
        [
            "Изучена структура организации, роли и бизнес-процессы заявок.",
            "Определены требования к статусам, правам доступа и данным заявки.",
            "Выбран web-подход на Laravel для удобства эксплуатации и развития.",
        ],
        4,
        total,
    )
    slide_images(
        prs,
        "Разработка клиентской части",
        "Интерфейс",
        [
            (ROOT / "docs" / "mockup_images" / "mockup_login.png", "Вход в систему"),
            (ROOT / "docs" / "mockup_images" / "mockup_journal.png", "Журнал заявок"),
            (ROOT / "docs" / "mockup_images" / "mockup_create.png", "Добавление заявки"),
            (ROOT / "docs" / "mockup_images" / "mockup_ticket.png", "Карточка заявки"),
        ],
        5,
        total,
    )
    # Additional slide with architecture and diagrams to enrich presentation
    slide_images(
        prs,
        "Диаграммы архитектуры и структуры",
        "Диаграммы",
        [
            (ROOT / "docs" / "diagram_images" / "diagram_use_case.png", "Диаграмма вариантов использования"),
            (ROOT / "docs" / "diagram_images" / "diagram_er.png", "ER-модель базы данных"),
            (ROOT / "docs" / "diagram_images" / "diagram_architecture.png", "Трехуровневая архитектура"),
            (ROOT / "docs" / "diagram_images" / "diagram_postman.png", "Postman: API-примеры"),
        ],
        6,
        total,
    )
    # Second diagrams slide for DB structure images
    slide_images(
        prs,
        "Структура данных",
        "БД",
        [
            (ROOT / "docs" / "diagram_images" / "diagram_db_users.png", "Структура таблицы пользователей"),
            (ROOT / "docs" / "diagram_images" / "diagram_db_tickets.png", "Структура таблицы заявок"),
        ],
        7,
        total,
    )
    slide_topic(
        prs,
        "Серверная часть и тестирование",
        "Backend",
        [
            "Реализованы маршруты, контроллеры, роли и валидация в Laravel.",
            "Подготовлены тестовые сценарии для ключевых операций: вход, создание, обработка и закрытие.",
            "Система готова к локальному запуску через composer, migrate и seed.",
        ],
        6,
        total,
    )
    slide_topic(
        prs,
        "Экономическое обоснование",
        "Эффективность",
        [
            "Оценены затраты на разработку и подготовку проекта к защите.",
            "Система сокращает ручной труд и повышает прозрачность обработки заявок.",
            "Решение оправдано для учебной организации и локального использования.",
        ],
        7,
        total,
    )
    slide_final(prs, total)

    prs.save(OUTPUT)


if __name__ == "__main__":
    main()
