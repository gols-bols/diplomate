from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/Users/gnome/Downloads/kurso-main 2")
LIB_DIR = Path("/tmp/odflib")
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from odf import teletype  # type: ignore
from odf.opendocument import OpenDocumentText  # type: ignore
from odf.style import (  # type: ignore
    Footer,
    GraphicProperties,
    MasterPage,
    PageLayout,
    PageLayoutProperties,
    ParagraphProperties,
    Style,
    TabStop,
    TabStops,
    TextProperties,
)
from odf.text import (  # type: ignore
    H,
    IndexBody,
    IndexEntryPageNumber,
    IndexEntryTabStop,
    IndexEntryText,
    IndexTitle,
    IndexTitleTemplate,
    P,
    PageNumber,
    S,
    Span,
    TableOfContent,
    TableOfContentEntryTemplate,
    TableOfContentSource,
)


SOURCE = ROOT / "docs" / "Пояснительная_записка_по_плану.md"
OUTPUT = ROOT / "docs" / "Пояснительная_записка_libreoffice.odt"

STRUCTURAL_HEADINGS = {
    "перечень сокращений и обозначений",
    "введение",
    "заключение",
    "библиография",
}


def strip_md(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


def parse_markdown(markdown: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False

    for raw in markdown.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            blocks.append(("code", line))
            continue

        if not stripped or stripped == "---":
            blocks.append(("blank", ""))
            continue

        if stripped.startswith("# "):
            continue

        if stripped.startswith("## "):
            blocks.append(("h2", strip_md(stripped[3:])))
            continue

        if stripped.startswith("### "):
            blocks.append(("h3", strip_md(stripped[4:])))
            continue

        if re.match(r"^\d+\.\s", stripped):
            blocks.append(("number", strip_md(stripped)))
            continue

        if stripped.startswith("- "):
            blocks.append(("bullet", strip_md(stripped[2:])))
            continue

        blocks.append(("p", strip_md(stripped)))

    return blocks


def add_style(doc: OpenDocumentText, style: Style, *, automatic: bool = False) -> None:
    if automatic:
        doc.automaticstyles.addElement(style)
    else:
        doc.styles.addElement(style)


def configure_styles(doc: OpenDocumentText) -> None:
    page_layout = PageLayout(name="Pm1")
    page_layout.addElement(
        PageLayoutProperties(
            margintop="2cm",
            marginbottom="2cm",
            marginleft="3cm",
            marginright="1cm",
            pagewidth="21cm",
            pageheight="29.7cm",
            printorientation="portrait",
        )
    )
    doc.automaticstyles.addElement(page_layout)

    footer_style = Style(name="Footer", family="paragraph")
    footer_style.addElement(
        ParagraphProperties(textalign="right", marginleft="0cm", marginright="0cm")
    )
    footer_style.addElement(
        TextProperties(fontname="Times New Roman", fontsize="12pt")
    )
    add_style(doc, footer_style)

    master_page = MasterPage(name="Standard", pagelayoutname=page_layout)
    footer = Footer()
    footer_p = P(stylename=footer_style)
    footer_p.addElement(PageNumber(selectpage="current"))
    footer.addElement(footer_p)
    master_page.addElement(footer)
    doc.masterstyles.addElement(master_page)

    body_style = Style(name="BodyText", family="paragraph")
    body_style.addElement(
        ParagraphProperties(
            textalign="justify",
            textindent="1.25cm",
            lineheight="150%",
            margintop="0cm",
            marginbottom="0cm",
        )
    )
    body_style.addElement(
        TextProperties(fontname="Times New Roman", fontsize="14pt")
    )
    add_style(doc, body_style)

    heading1 = Style(name="Heading1Custom", family="paragraph")
    heading1.addElement(
        ParagraphProperties(
            textalign="justify",
            breakbefore="page",
            margintop="0cm",
            marginbottom="0cm",
        )
    )
    heading1.addElement(
        TextProperties(fontname="Times New Roman", fontsize="16pt", fontweight="bold")
    )
    add_style(doc, heading1)

    centered_heading = Style(name="CenteredHeading1Custom", family="paragraph")
    centered_heading.addElement(
        ParagraphProperties(
            textalign="center",
            breakbefore="page",
            margintop="0cm",
            marginbottom="0cm",
        )
    )
    centered_heading.addElement(
        TextProperties(fontname="Times New Roman", fontsize="16pt", fontweight="bold")
    )
    add_style(doc, centered_heading)

    heading2 = Style(name="Heading2Custom", family="paragraph")
    heading2.addElement(
        ParagraphProperties(
            textalign="justify",
            textindent="1.25cm",
            lineheight="150%",
            margintop="0cm",
            marginbottom="0cm",
        )
    )
    heading2.addElement(
        TextProperties(fontname="Times New Roman", fontsize="16pt", fontweight="bold")
    )
    add_style(doc, heading2)

    toc_title = Style(name="TocTitle", family="paragraph")
    toc_title.addElement(
        ParagraphProperties(
            textalign="center",
            breakbefore="page",
            margintop="0cm",
            marginbottom="0cm",
        )
    )
    toc_title.addElement(
        TextProperties(fontname="Times New Roman", fontsize="16pt", fontweight="bold")
    )
    add_style(doc, toc_title)

    toc_level_1 = Style(name="Contents_20_1", family="paragraph")
    toc_level_1.addElement(
        ParagraphProperties(
            textalign="justify",
            lineheight="150%",
            marginleft="0cm",
            marginright="0cm",
            textindent="0cm",
            autotextindent="false",
        )
    )
    toc_level_1.addElement(
        TextProperties(fontname="Times New Roman", fontsize="14pt")
    )
    add_style(doc, toc_level_1)

    toc_level_2 = Style(name="Contents_20_2", family="paragraph")
    toc_level_2.addElement(
        ParagraphProperties(
            textalign="justify",
            lineheight="150%",
            marginleft="0cm",
            marginright="0cm",
            textindent="0cm",
            autotextindent="false",
        )
    )
    toc_level_2.addElement(
        TextProperties(fontname="Times New Roman", fontsize="14pt")
    )
    add_style(doc, toc_level_2)

    toc_heading = Style(name="Contents_20_Heading", family="paragraph")
    toc_heading.addElement(
        ParagraphProperties(textalign="center", lineheight="150%", margintop="0cm")
    )
    toc_heading.addElement(
        TextProperties(fontname="Times New Roman", fontsize="16pt", fontweight="bold")
    )
    add_style(doc, toc_heading)

    bullet_style = Style(name="BulletText", family="paragraph")
    bullet_style.addElement(
        ParagraphProperties(
            textalign="justify",
            marginleft="1.25cm",
            textindent="-0.63cm",
            lineheight="150%",
        )
    )
    bullet_style.addElement(
        TextProperties(fontname="Times New Roman", fontsize="14pt")
    )
    add_style(doc, bullet_style)

    number_style = Style(name="NumberText", family="paragraph")
    number_style.addElement(
        ParagraphProperties(
            textalign="justify",
            marginleft="1.25cm",
            textindent="-0.63cm",
            lineheight="150%",
        )
    )
    number_style.addElement(
        TextProperties(fontname="Times New Roman", fontsize="14pt")
    )
    add_style(doc, number_style)

    code_style = Style(name="CodeText", family="paragraph")
    code_style.addElement(
        ParagraphProperties(
            textalign="left",
            marginleft="1.25cm",
            textindent="0cm",
            lineheight="100%",
        )
    )
    code_style.addElement(
        TextProperties(fontname="Courier New", fontsize="12pt")
    )
    add_style(doc, code_style)

    empty_break = Style(name="PageBreakOnly", family="paragraph")
    empty_break.addElement(ParagraphProperties(breakafter="page"))
    add_style(doc, empty_break)

    index_graphic = Style(name="IndexTabStop", family="graphic")
    index_graphic.addElement(GraphicProperties())
    add_style(doc, index_graphic, automatic=True)


def make_paragraph(text: str, style_name: str) -> P:
    p = P(stylename=style_name)
    teletype.addTextToElement(p, text)
    return p


def make_heading(text: str, level: int, style_name: str) -> H:
    h = H(stylename=style_name, outlinelevel=level)
    teletype.addTextToElement(h, text)
    return h


def make_toc() -> TableOfContent:
    toc = TableOfContent(name="Table of Contents1", protected="true")

    source = TableOfContentSource(outlinelevel=2, useoutlinelevel="true")
    title_template = IndexTitleTemplate(stylename="Contents_20_Heading")
    teletype.addTextToElement(title_template, "Содержание")
    source.addElement(title_template)

    for level, style_name in ((1, "Contents_20_1"), (2, "Contents_20_2")):
        entry = TableOfContentEntryTemplate(outlinelevel=level, stylename=style_name)
        entry.addElement(IndexEntryText())
        entry.addElement(
            IndexEntryTabStop(
                type="right",
                leaderchar=" ",
            )
        )
        entry.addElement(IndexEntryPageNumber())
        source.addElement(entry)

    toc.addElement(source)

    body = IndexBody()
    title = IndexTitle(name="Table of Contents Title")
    title_p = P(stylename="Contents_20_Heading")
    teletype.addTextToElement(title_p, "Содержание")
    title.addElement(title_p)
    body.addElement(title)
    toc.addElement(body)
    return toc


def build_document() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    blocks = parse_markdown(markdown)

    doc = OpenDocumentText()
    configure_styles(doc)

    # First page reserved for the title sheet.
    doc.text.addElement(P(stylename="PageBreakOnly"))

    doc.text.addElement(make_paragraph("Содержание", "TocTitle"))
    doc.text.addElement(make_toc())
    doc.text.addElement(P(stylename="PageBreakOnly"))

    first_section = True
    for kind, text in blocks:
        if kind == "blank":
            doc.text.addElement(P())
            continue

        if kind == "h2":
            lowered = text.lower()
            style_name = (
                "CenteredHeading1Custom"
                if lowered in STRUCTURAL_HEADINGS or lowered.startswith("приложение")
                else "Heading1Custom"
            )

            if first_section:
                # The first heading should start on the page after the TOC,
                # so it does not need an extra page break from content flow.
                style_name = (
                    "CenteredHeading1Custom" if style_name == "CenteredHeading1Custom" else "Heading1Custom"
                )
                first_section = False

            doc.text.addElement(make_heading(text, 1, style_name))
            continue

        if kind == "h3":
            doc.text.addElement(make_heading(text, 2, "Heading2Custom"))
            continue

        if kind == "bullet":
            doc.text.addElement(make_paragraph("- " + text, "BulletText"))
            continue

        if kind == "number":
            doc.text.addElement(make_paragraph(text, "NumberText"))
            continue

        if kind == "code":
            doc.text.addElement(make_paragraph(text, "CodeText"))
            continue

        doc.text.addElement(make_paragraph(text, "BodyText"))

    doc.save(str(OUTPUT))


if __name__ == "__main__":
    build_document()
