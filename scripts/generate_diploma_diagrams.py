"""Генерация диаграмм для диплома (ER, архитектура, БД, Postman)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from project_paths import DIAGRAM_DIR, pil_font_candidates

try:
    from generate_figma_mockup_images import font, BG, PANEL, STROKE, TEXT, MUTED, ACCENT, panel
except ImportError:
    from PIL import ImageFont

    def font(size: int, bold: bool = False):
        for candidate in pil_font_candidates(bold=bold):
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                continue
        return ImageFont.load_default()

    BG, PANEL, STROKE, TEXT, MUTED, ACCENT = "#F4EFE6", "#FFF9F1", "#D8C7AE", "#2F261A", "#72614B", "#8F4626"

    def panel(draw, box, **kw):
        draw.rounded_rectangle(box, radius=kw.get("radius", 20), fill=kw.get("fill", PANEL), outline=STROKE, width=2)


DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)


def save(name: str, img: Image.Image) -> Path:
    path = DIAGRAM_DIR / name
    img.save(path)
    print("saved", path)
    return path


def draw_arrow(draw, start, end, color=ACCENT):
    draw.line([start, end], fill=color, width=3)
    ex, ey = end
    draw.polygon([(ex, ey), (ex - 12, ey - 6), (ex - 12, ey + 6)], fill=color)


def er_diagram() -> Path:
    img = Image.new("RGB", (1400, 720), BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "ER-модель базы данных (users, tickets)", font=font(32, True), fill=TEXT)
    panel(draw, (120, 160, 580, 520), radius=24)
    draw.text((150, 190), "users", font=font(28, True), fill=ACCENT)
    for i, col in enumerate(["id PK", "name", "email", "role", "campus", "api_token"]):
        draw.text((150, 240 + i * 42), col, font=font(22), fill=TEXT)
    panel(draw, (760, 160, 1220, 560), radius=24)
    draw.text((790, 190), "tickets", font=font(28, True), fill=ACCENT)
    for i, col in enumerate(
        ["id PK", "title", "description", "status", "priority", "campus", "created_by FK", "assignee_id FK"]
    ):
        draw.text((790, 240 + i * 38), col, font=font(20), fill=TEXT)
    draw_arrow(draw, (580, 340), (760, 340))
    draw.text((620, 300), "1:N", font=font(22, True), fill=MUTED)
    return save("diagram_er.png", img)


def architecture_diagram() -> Path:
    img = Image.new("RGB", (1400, 720), BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "Архитектура web-приложения (MVC + REST API)", font=font(32, True), fill=TEXT)
    boxes = [
        (100, 280, 360, 420, "Браузер\n(Blade UI)"),
        (520, 280, 880, 420, "Laravel\nControllers + API"),
        (1040, 280, 1300, 420, "MySQL\nusers, tickets"),
    ]
    for x1, y1, x2, y2, label in boxes:
        panel(draw, (x1, y1, x2, y2), radius=22)
        draw.multiline_text((x1 + 30, y1 + 45), label, font=font(24, True), fill=TEXT, spacing=8)
    draw_arrow(draw, (360, 350), (520, 350))
    draw_arrow(draw, (880, 350), (1040, 350))
    draw.text((400, 450), "HTTP / JSON", font=font(20), fill=MUTED)
    return save("diagram_architecture.png", img)


def use_case_diagram() -> Path:
    img = Image.new("RGB", (1400, 720), BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "Варианты использования (основные роли)", font=font(32, True), fill=TEXT)
    panel(draw, (80, 200, 320, 600), radius=20)
    draw.text((120, 360), "Пользователь", font=font(24, True), fill=TEXT)
    panel(draw, (1080, 200, 1320, 600), radius=20)
    draw.text((1120, 320), "Менеджер /\nАдминистратор", font=font(22, True), fill=TEXT)
    panel(draw, (450, 180, 950, 280), radius=18)
    draw.text((500, 220), "Авторизация", font=font(22), fill=TEXT)
    panel(draw, (450, 310, 950, 410), radius=18)
    draw.text((500, 350), "Создание и просмотр заявок", font=font(22), fill=TEXT)
    panel(draw, (450, 440, 950, 540), radius=18)
    draw.text((500, 480), "Обработка заявок, назначение исполнителя", font=font(22), fill=TEXT)
    return save("diagram_use_case.png", img)


def db_table_diagram(title: str, columns: list[str], filename: str) -> Path:
    img = Image.new("RGB", (1200, 640), BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), title, font=font(30, True), fill=TEXT)
    panel(draw, (120, 120, 1080, 560), radius=24, fill="#FFFFFF")
    for i, col in enumerate(columns):
        draw.text((160, 170 + i * 48), col, font=font(24), fill=TEXT)
    return save(filename, img)


def postman_diagram() -> Path:
    img = Image.new("RGB", (1400, 720), BG)
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "Проверка API в Postman (пример запроса)", font=font(32, True), fill=TEXT)
    panel(draw, (80, 120, 1320, 660), radius=26, fill="#FFFFFF")
    draw.text((120, 160), "POST  /api/v1/login", font=font(26, True), fill=ACCENT)
    draw.text((120, 220), "Status: 200 OK", font=font(24), fill="#1B6B2F")
    panel(draw, (120, 280, 600, 520), radius=16, fill="#F8F8F8")
    draw.text((140, 310), 'Body: {"email":"...","password":"..."}', font=font(20), fill=TEXT)
    panel(draw, (640, 280, 1280, 520), radius=16, fill="#F8F8F8")
    draw.text((660, 310), 'Response: {"token":"..."}', font=font(20), fill=TEXT)
    return save("diagram_postman.png", img)


def main() -> None:
    er_diagram()
    architecture_diagram()
    use_case_diagram()
    db_table_diagram(
        "Приложение А — таблица users",
        ["id — INTEGER PK", "name — VARCHAR", "email — VARCHAR UNIQUE", "password — VARCHAR", "role — VARCHAR", "campus — VARCHAR"],
        "diagram_db_users.png",
    )
    db_table_diagram(
        "Приложение А — таблица tickets",
        [
            "id — INTEGER PK",
            "title, description — TEXT",
            "status, priority — VARCHAR",
            "campus, room — VARCHAR",
            "created_by, assignee_id — FK → users",
        ],
        "diagram_db_tickets.png",
    )
    postman_diagram()
    print("Диаграммы в", DIAGRAM_DIR)


if __name__ == "__main__":
    main()
