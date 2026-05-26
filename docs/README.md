# Финальные материалы проекта

В этой папке оставлены только материалы, которые нужны для сдачи и демонстрации:

- `Диплом_отдельный_финал_60.docx` — финальная версия диплома.
- `Пояснительная_записка_финал.docx` — финальная пояснительная записка по курсовой.
- `Презентация_к_курсовой.pptx` — презентация для защиты.
- `SPK_Helpdesk_API.postman_collection.json` — коллекция запросов для Postman.
- `spk_helpdesk_figma_board.svg`, `figma_mockup_readme.md`, `mockup_images/` — макеты и изображения интерфейса (PNG для вставки в Word).

### Скриншоты в Word-документах

Готовые PNG лежат в `docs/mockup_images/` (`mockup_login.png`, `mockup_journal.png`, `mockup_create.png`, `mockup_ticket.png`).

Чтобы **сгенерировать** макеты и **вставить** их в финальные `.docx` (раздел 2.2, перед «2.3 …»):

```powershell
cd "путь\к\kurso-main 2\scripts"
python regenerate_diploma_final.py
python verify_docx_images.py
```

В дипломе должно быть **10** файлов в `word/media/` (проверка скриптом). Источники PNG: `docs/mockup_images/`, `docs/diagram_images/`.

**Важно:** `fix_diploma_v3_assignment.py` перезаписывает docx без картинок — после него всегда запускайте `insert_all_diploma_figures.py --force`.

Замена макетов на живые скрины: подставьте свои PNG в `docs/mockup_images/` с теми же именами и снова `insert_all_diploma_figures.py --force`.

Под каждым изображением — подпись по центру: **Рисунок 1**, **Рисунок 2**, … (сквозная нумерация по всему документу). Флаг `--force` удаляет старый блок макетов и вставляет заново.

Скрипт обновляет `Диплом_отдельный_финал_60.docx` и `Пояснительная_записка_финал.docx`. Приложения А/Б (БД и Postman) нужно добавить вручную из phpMyAdmin и Postman.
- `laravel_backend_plan.md` — технический план Laravel-проекта.

Черновики и промежуточные версии вынесены в папку `docs_archive` в корне проекта.
