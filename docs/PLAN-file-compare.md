# File Compare — План проекта

> Полный план: см. artifacts `implementation_plan.md`

## Обзор

Утилита для сравнения двух директорий по именам и атрибутам файлов.
Архитектура: **Гибрид** (Core Engine + **PySide6** GUI + CLI).

## Стек

- Python 3.12+ / **PySide6** (LGPL) / pytest / ruff / mypy

## Phase 1: Core + GUI (10 задач)

- [x] 1. Структура проекта + `pyproject.toml`
- [x] 2. `models.py` — FileEntry (с поддержкой `relative_path`)
- [x] 3. `scanner.py` — сканирование (с поддержкой рекурсии)
- [x] 4. `criteria.py` — Strategy: ByName, ByNameAndSize
- [x] 5. `comparator.py` — основной компаратор
- [x] 6. `dir_selector.py` — виджет выбора папки
- [x] 7. `criteria_panel.py` — панель (критерии + чекбокс "Recursive")
- [x] 8. `results_view.py` — таблица результатов
- [x] 9. `main_window.py` — главное окно
- [x] 10. `conftest.py` — тестовые фикстуры

## Phase 2: TC Launcher + CLI

- [x] 11. `cli/main.py` — аргументы командной строки
- [x] 12. Selection-aware compare для обеих панелей
- [x] 13. GUI autostart из TC-контекста

## Phase 3: Packaging

- [x] 14. `PyInstaller` spec
- [x] 15. Скрипт локальной сборки `.exe`
- [x] 16. Инструкция интеграции с Total Commander

## Phase X: Верификация

- [ ] `python -m pytest tests/ -v` — все тесты green
- [ ] `ruff check file_compare tests/` — без ошибок
- [ ] Ручная проверка GUI: сравнение с рекурсией и без
- [ ] Ручная проверка из Total Commander
