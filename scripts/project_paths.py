from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MOCKUP_DIR = DOCS_DIR / "mockup_images"
DIAGRAM_DIR = DOCS_DIR / "diagram_images"

# Реальный диплом пользователя (Downloads), не docs/ в репозитории
DOWNLOADS_DIR = Path(r"c:\Users\Admin\Downloads")


def diploma_v2_path() -> Path:
    import unicodedata

    explicit = DOWNLOADS_DIR / "Диплом_отдельный_расширенный_3_v2.docx"
    if explicit.is_file():
        return Path(unicodedata.normalize("NFC", str(explicit.resolve())))
    path_file = PROJECT_ROOT / "scripts" / "diploma_v2_path.txt"
    if path_file.is_file():
        p = Path(path_file.read_text(encoding="utf-8").strip())
        if p.is_file():
            return p.resolve()
    raise FileNotFoundError(
        "Не найден Диплом_отдельный_расширенный_3_v2.docx в Downloads"
    )


DIPLOMA_MAIN = diploma_v2_path  # lazy: call diploma_v2_path() when needed
DIPLOMA_REPO = DOCS_DIR / "Диплом_отдельный_финал_60.docx"

# path, заголовок для пояснительного абзаца (номер рисунка подставляется при вставке)
MOCKUP_FIGURES = [
    (
        MOCKUP_DIR / "mockup_login.png",
        "макет экрана авторизации",
        "На рисунке {n} представлен предварительный макет экрана авторизации пользователя. "
        "Данный экран был спроектирован для обеспечения простого и понятного входа в систему.",
    ),
    (
        MOCKUP_DIR / "mockup_journal.png",
        "макет журнала заявок",
        "На рисунке {n} представлен макет основного рабочего экрана со списком заявок. "
        "В макете отражены сводные показатели, карточки обращений и визуальное выделение статусов.",
    ),
    (
        MOCKUP_DIR / "mockup_create.png",
        "макет формы создания заявки",
        "На рисунке {n} показан макет формы создания новой заявки. "
        "Экран включает основные поля ввода и вспомогательные подсказки для пользователя.",
    ),
    (
        MOCKUP_DIR / "mockup_ticket.png",
        "макет карточки заявки",
        "На рисунке {n} представлен макет карточки отдельной заявки, содержащей описание обращения "
        "и служебные сведения, необходимые для его обработки.",
    ),
]

# обратная совместимость: (path, caption, description) — caption генерируется в docx_figures
MOCKUP_IMAGES = MOCKUP_FIGURES


def pil_font_candidates(*, bold: bool = False) -> list[Path]:
    if os.name == "nt":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        fonts = windir / "Fonts"
        return [
            fonts / ("arialbd.ttf" if bold else "arial.ttf"),
            fonts / ("segoeuib.ttf" if bold else "segoeui.ttf"),
            fonts / "tahoma.ttf",
        ]
    return [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Tahoma.ttf"),
    ]
