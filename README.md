# File Compare

`File Compare` это настольная Windows-утилита для сравнения файлов и каталогов.
Проект написан на Python и PySide6 и в первую очередь рассчитан на запуск как внешнего инструмента из Total Commander.

## Что умеет программа

Программа сравнивает левую и правую сторону и показывает результат в виде списка:

- файлы, которые есть с обеих сторон;
- файлы, которые есть только слева;
- файлы, которые есть только справа;
- несовпадения по выбранным критериям.

Поддерживаются такие критерии сравнения:

- имя;
- размер;
- дата изменения.

Поддерживаются три основных режима работы:

1. сравнение двух каталогов;
2. сравнение только выбранных элементов с обеих сторон;
3. сравнение одной явной пары файлов.

Для явной пары файлов GUI также умеет показывать side-by-side diff содержимого и разрешает редактирование UTF-8 текстовых файлов.

## Основные возможности

- настольный GUI на PySide6;
- side-by-side diff для выбранной пары файлов;
- `Edit Mode` для явного сравнения файлов;
- независимые `Save Left` и `Save Right`;
- `Recompare` после правок;
- запрос при несохранённых изменениях перед `Compare`, `Recompare` и закрытием окна;
- интерфейс на английском и русском;
- сохранение выбора языка через `QSettings`;
- launcher-режим для Total Commander;
- готовый Windows-артефакт `dist\FileCompareTC.exe`.

## Быстрый старт

### Установка окружения

```bash
pip install -e ".[dev]"
```

### Запуск GUI

```bash
file-compare
```

Альтернатива:

```bash
python -m file_compare.gui.main_window
```

### Запуск CLI launcher

```bash
file-compare-cli --help
```

Примеры:

```bash
file-compare-cli --left-dir "D:\Left" --right-dir "D:\Right" --size --date
file-compare-cli --left-file "D:\Left\a.txt" --right-file "D:\Right\b.txt" --size --date
file-compare-cli --left-dir "D:\Left" --right-dir "D:\Right" --left-selected-list "D:\left.txt" --right-selected-list "D:\right.txt" --size --date
```

## Сборка EXE

```bash
pip install -e ".[dev]"
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

Ожидаемый результат:

- `dist\FileCompareTC.exe`

## Документация

- Руководство пользователя: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Интеграция с Total Commander: [docs/TOTAL_COMMANDER.md](docs/TOTAL_COMMANDER.md)
- Git workflow: [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md)

## Проверка

Запуск тестов:

```bash
python -m pytest tests -q
```

Проверка линтером:

```bash
ruff check file_compare tests
```

## Правило разработки

Не работай напрямую в `main`.
Каждая новая задача начинается от обновлённого `main` в отдельной ветке.

Полный workflow:

- [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md)
