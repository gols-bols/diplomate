from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from project_paths import MOCKUP_DIR, pil_font_candidates

OUT_DIR = MOCKUP_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in pil_font_candidates(bold=bold):
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()


BG = "#F4EFE6"
PANEL = "#FFF9F1"
STROKE = "#D8C7AE"
TEXT = "#2F261A"
MUTED = "#72614B"
ACCENT = "#8F4626"
BUTTON = "#9C4F2D"


def panel(draw: ImageDraw.ImageDraw, box, radius=24, fill=PANEL, outline=STROKE, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw: ImageDraw.ImageDraw, box, text: str, fill: str, text_fill: str):
    draw.rounded_rectangle(box, radius=16, fill=fill)
    draw.text((box[0] + 16, box[1] + 8), text, font=font(20, True), fill=text_fill)


def login_screen() -> Path:
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    panel(draw, (220, 120, 1380, 780), radius=30)
    panel(draw, (520, 220, 1080, 650), radius=26, fill="#FFFFFF")
    draw.text((580, 285), "Вход в систему", font=font(44, True), fill=TEXT)
    draw.text((580, 340), "Служба заявок СПК", font=font(24), fill=MUTED)
    panel(draw, (580, 410, 1020, 485), radius=18, fill="#FFFDF9")
    draw.text((605, 435), "Электронная почта", font=font(24), fill="#8D7C67")
    panel(draw, (580, 515, 1020, 590), radius=18, fill="#FFFDF9")
    draw.text((605, 540), "Пароль", font=font(24), fill="#8D7C67")
    draw.rounded_rectangle((580, 620, 790, 685), radius=18, fill=BUTTON)
    draw.text((650, 638), "Войти", font=font(28, True), fill="white")
    path = OUT_DIR / "mockup_login.png"
    img.save(path)
    return path


def journal_screen() -> Path:
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    panel(draw, (50, 40, 1550, 860), radius=28)
    panel(draw, (90, 80, 1510, 190), radius=24, fill="#FFF7EC")
    draw.text((130, 115), "Журнал заявок", font=font(46, True), fill=TEXT)
    draw.text((130, 160), "Разделение ролей, цветные статусы, фильтры и полная информация по обращениям.", font=font(22), fill=MUTED)
    pill(draw, (1310, 110, 1450, 155), "ADMIN", "#FFF1E3", ACCENT)

    stats = [
        ("Общий поток", "18", BUTTON),
        ("Новые", "5", "#D2A02F"),
        ("В работе", "7", "#2F7FC4"),
        ("Решенные", "6", "#3F8C57"),
    ]
    x = 90
    for title, value, color in stats:
        panel(draw, (x, 230, x + 320, 380), radius=20, fill="#FFFFFF")
        draw.rectangle((x, 230, x + 10, 380), fill=color)
        draw.text((x + 28, 265), title.upper(), font=font(18, True), fill=MUTED)
        draw.text((x + 28, 315), value, font=font(42, True), fill=TEXT)
        x += 350

    panel(draw, (90, 420, 1510, 780), radius=24, fill="#FFFFFF")
    draw.text((125, 470), "Не работает проектор в кабинете 45", font=font(34, True), fill=ACCENT)
    pill(draw, (1280, 455, 1440, 500), "В работе", "#DFF1FF", "#0D5885")
    draw.text((125, 525), "Учебный корпус 1 · кабинет 45", font=font(24), fill=MUTED)
    draw.text((125, 570), "Заявитель: Карташов Илья Сергеевич", font=font(22), fill=MUTED)
    draw.text((125, 610), "Исполнитель: Якименко О.А.", font=font(22), fill=MUTED)
    draw.rounded_rectangle((125, 690, 315, 745), radius=16, fill="#F1ECE4")
    draw.text((180, 707), "Открыть", font=font(24, True), fill=TEXT)
    draw.rounded_rectangle((340, 690, 590, 745), radius=16, fill="#F1ECE4")
    draw.text((390, 707), "Редактировать", font=font(24, True), fill=TEXT)
    path = OUT_DIR / "mockup_journal.png"
    img.save(path)
    return path


def create_screen() -> Path:
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    panel(draw, (60, 40, 1540, 860), radius=28)
    draw.text((100, 95), "Создание новой заявки", font=font(44, True), fill=TEXT)
    draw.text((100, 145), "Пользователь указывает корпус, кабинет и описание проблемы.", font=font(22), fill=MUTED)
    panel(draw, (100, 210, 980, 800), radius=24, fill="#FFFFFF")
    fields = [
        (260, "Заголовок заявки", 1),
        (360, "Корпус", 0.5),
        (360, "Кабинет", 0.5),
        (460, "Подробное описание", 1),
    ]
    panel(draw, (1170, 250, 1470, 520), radius=24, fill="#FFF7EC")
    draw.text((1205, 295), "Подсказки", font=font(28, True), fill=ACCENT)
    for i, tip in enumerate(["Укажите корпус", "Заполните кабинет", "Опишите проблему"]):
        draw.text((1205, 350 + i * 50), f"• {tip}", font=font(22), fill=MUTED)

    panel(draw, (140, 300, 940, 375), radius=18, fill="#FFFDF9")
    draw.text((165, 325), "Заголовок заявки", font=font(24), fill="#8D7C67")
    panel(draw, (140, 410, 520, 485), radius=18, fill="#FFFDF9")
    draw.text((165, 435), "Корпус", font=font(24), fill="#8D7C67")
    panel(draw, (560, 410, 940, 485), radius=18, fill="#FFFDF9")
    draw.text((585, 435), "Кабинет", font=font(24), fill="#8D7C67")
    panel(draw, (140, 520, 940, 690), radius=18, fill="#FFFDF9")
    draw.text((165, 548), "Подробное описание", font=font(24), fill="#8D7C67")
    draw.rounded_rectangle((140, 720, 370, 785), radius=18, fill=BUTTON)
    draw.text((205, 740), "Сохранить", font=font(28, True), fill="white")
    path = OUT_DIR / "mockup_create.png"
    img.save(path)
    return path


def ticket_screen() -> Path:
    img = Image.new("RGB", (1600, 900), BG)
    draw = ImageDraw.Draw(img)
    panel(draw, (50, 40, 1550, 860), radius=28)
    draw.text((90, 95), "Карточка заявки", font=font(44, True), fill=TEXT)
    draw.text((90, 145), "Полная информация по обращению, статусу, кабинету и исполнителю.", font=font(22), fill=MUTED)
    panel(draw, (90, 220, 980, 760), radius=24, fill="#FFFFFF")
    draw.text((130, 270), "Не работает проектор в кабинете 45", font=font(34, True), fill=ACCENT)
    draw.text((130, 340), "Описание обращения", font=font(28, True), fill=TEXT)
    draw.text((130, 395), "В кабинете 45 не включается проектор. Требуется", font=font(24), fill=MUTED)
    draw.text((130, 430), "проверка подключения и работоспособности оборудования.", font=font(24), fill=MUTED)
    panel(draw, (1040, 220, 1490, 760), radius=24, fill="#FFF7EC")
    draw.text((1080, 275), "Служебные сведения", font=font(28, True), fill=ACCENT)
    lines = [
        "Заявитель: Карташов И.С.",
        "Корпус: Учебный корпус 1",
        "Кабинет: 45",
        "Исполнитель: Якименко О.А.",
        "Приоритет: Обычный",
        "Статус: В работе",
    ]
    for i, line in enumerate(lines):
        draw.text((1080, 340 + i * 55), line, font=font(22), fill=MUTED)
    draw.rounded_rectangle((90, 785, 300, 835), radius=16, fill="#F1ECE4")
    draw.text((132, 802), "Назад к списку", font=font(24, True), fill=TEXT)
    path = OUT_DIR / "mockup_ticket.png"
    img.save(path)
    return path


def main() -> None:
    for builder in [login_screen, journal_screen, create_screen, ticket_screen]:
        builder()


if __name__ == "__main__":
    main()
