from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path("/Users/gnome/Downloads/kurso-main 2")
SOURCE = ROOT / "docs" / "Пояснительная_записка_по_плану.md"
OUTPUT_RTF = ROOT / "docs" / "Пояснительная_записка_официальная.rtf"
OUTPUT_DOCX = ROOT / "docs" / "Пояснительная_записка_официальная.docx"


def rtf_escape(text: str) -> str:
    text = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
    parts: list[str] = []
    for char in text:
        code = ord(char)
        if char == "\n":
            parts.append("\\line ")
        elif 32 <= code <= 126:
            parts.append(char)
        else:
            if code > 32767:
                code -= 65536
            parts.append(f"\\u{code}?")
    return "".join(parts)


def strip_md(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


def normal_paragraph(text: str) -> str:
    return (
        r"\pard\qj\fi709\sl420\slmult1\fs28\f0 "
        + rtf_escape(strip_md(text))
        + r"\par"
    )


def body_heading(text: str) -> str:
    return (
        r"\pard\qj\b\fi709\sl420\slmult1\fs32\f0 "
        + rtf_escape(strip_md(text))
        + r"\b0\par"
    )


def structural_heading(text: str) -> str:
    return (
        r"\pard\qc\b\sl420\slmult1\fs32\f0 "
        + rtf_escape(strip_md(text).upper())
        + r"\b0\par"
    )


def subheading(text: str) -> str:
    return (
        r"\pard\qj\b\fi709\sl420\slmult1\fs28\f0 "
        + rtf_escape(strip_md(text))
        + r"\b0\par"
    )


def bullet_item(text: str) -> str:
    return (
        r"\pard\qj\li1069\fi-360\sl420\slmult1\fs28\f0 "
        + rtf_escape("- " + strip_md(text))
        + r"\par"
    )


def numbered_item(text: str) -> str:
    return (
        r"\pard\qj\li1069\fi-360\sl420\slmult1\fs28\f0 "
        + rtf_escape(strip_md(text))
        + r"\par"
    )


def toc_item(text: str, level: int) -> str:
    left = 709 if level == 1 else 1069
    return (
        rf"\pard\qj\li{left}\fi0\sl420\slmult1\fs28\f0 "
        + rtf_escape(strip_md(text))
        + r"\par"
    )


def bibliography_item(text: str) -> str:
    return (
        r"\pard\qj\li1069\fi-360\sl420\slmult1\fs28\f0 "
        + rtf_escape(strip_md(text))
        + r"\par"
    )


def diagram_line(text: str) -> str:
    return (
        r"\pard\ql\li1069\fi0\sl360\slmult1\fs22\f1 "
        + rtf_escape(text.rstrip())
        + r"\par"
    )


def parse_lines(markdown: str) -> tuple[list[tuple[str, str]], list[str]]:
    blocks: list[tuple[str, str]] = []
    toc: list[str] = []
    in_code = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            if not in_code:
                blocks.append(("blank", ""))
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
            title = stripped[3:].strip()
            blocks.append(("h2", title))
            toc.append(title)
            continue

        if stripped.startswith("### "):
            title = stripped[4:].strip()
            blocks.append(("h3", title))
            toc.append("  " + title)
            continue

        if re.match(r"^\d+\.\s", stripped):
            blocks.append(("number", stripped))
            continue

        if stripped.startswith("- "):
            blocks.append(("bullet", stripped[2:]))
            continue

        blocks.append(("p", stripped))

    return blocks, toc


def build_rtf(markdown: str) -> str:
    blocks, toc = parse_lines(markdown)

    header = r"""{\rtf1\ansi\ansicpg1251\deff0
{\fonttbl{\f0 Times New Roman;}{\f1 Courier New;}}
\paperw11907\paperh16840\margl1701\margr567\margt1134\margb1134
\titlepg
{\footer\pard\qr\fs24\f0{\field{\*\fldinst PAGE }}\par}
"""

    parts = [header]

    # Reserve the first page for the title sheet the user will insert manually.
    parts.append(r"\pard\qc\sl420\slmult1\fs28\f0 \par\page")

    parts.append(structural_heading("Содержание"))
    parts.append(r"\pard\par")
    for item in toc:
        level = 2 if item.startswith("  ") else 1
        parts.append(toc_item(item.strip(), level))

    first_section = True
    for kind, text in blocks:
        if kind == "blank":
            parts.append(r"\pard\par")
            continue

        if kind == "h2":
            if not first_section:
                parts.append(r"\page")
            first_section = False
            clean = strip_md(text)
            lower = clean.lower()
            if (
                clean == "Введение"
                or clean == "Заключение"
                or "библиография" in lower
                or "перечень сокращений" in lower
                or lower.startswith("приложение")
            ):
                if "библиография" in lower:
                    parts.append(structural_heading("Библиография"))
                elif "перечень сокращений" in lower:
                    parts.append(structural_heading("Перечень сокращений и обозначений"))
                else:
                    parts.append(structural_heading(clean))
            else:
                parts.append(body_heading(clean))
            continue

        if kind == "h3":
            parts.append(subheading(text))
            continue

        if kind == "bullet":
            parts.append(bullet_item(text))
            continue

        if kind == "number":
            if re.match(r"^\d+\.\s", text) and any(ch.isalpha() or ord(ch) > 127 for ch in text):
                parts.append(bibliography_item(text))
            else:
                parts.append(numbered_item(text))
            continue

        if kind == "code":
            parts.append(diagram_line(text))
            continue

        parts.append(normal_paragraph(text))

    parts.append("}")
    return "\n".join(parts)


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    rtf = build_rtf(markdown)
    OUTPUT_RTF.write_text(rtf, encoding="utf-8")
    subprocess.run(
        [
            "textutil",
            "-convert",
            "docx",
            str(OUTPUT_RTF),
            "-output",
            str(OUTPUT_DOCX),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
