"""Находит и возвращает путь к Диплом_отдельный_расширенный_3_v2.docx."""
from __future__ import annotations

from pathlib import Path

DOWNLOADS = Path(r"c:\Users\Admin\Downloads")
PATH_FILE = Path(__file__).resolve().parent / "diploma_v2_path.txt"


def resolve_diploma_v2() -> Path:
    # Явный путь пользователя (NFC)
    explicit = DOWNLOADS / "Диплом_отдельный_расширенный_3_v2.docx"
    if explicit.is_file():
        return explicit.resolve()

    if PATH_FILE.is_file():
        p = Path(PATH_FILE.read_text(encoding="utf-8").strip())
        if p.is_file():
            return p.resolve()

    best: Path | None = None
    for p in DOWNLOADS.glob("*.docx"):
        name = p.name
        if "v2" in name and "3" in name:
            if best is None or p.stat().st_size > best.stat().st_size:
                best = p
    if best is None:
        raise FileNotFoundError("Не найден Диплом_отдельный_расширенный_3_v2.docx в Downloads")
    return best.resolve()


if __name__ == "__main__":
    p = resolve_diploma_v2()
    PATH_FILE.write_text(str(p), encoding="utf-8")
    PATH_FILE.with_suffix(".size.txt").write_text(str(p.stat().st_size), encoding="utf-8")
