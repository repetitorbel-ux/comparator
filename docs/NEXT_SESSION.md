# Next Session: File Compare

## 📅 Статус на 08.03.2026

### ✅ Что уже реализовано
1. **Package layout** переведён на `file_compare`.
2. **Core Engine** поддерживает:
   - сравнение каталогов целиком;
   - сравнение только selected items с обеих панелей;
   - критерии `Name`, `Size`, `Date`.
3. **GUI (PySide6)** умеет:
   - стартовать как обычное приложение;
   - стартовать из TC-контекста и сразу запускать сравнение.
   - показывать side-by-side diff содержимого для выбранной пары файлов.
   - включать `Edit Mode` для явной пары файлов, сохранять `Save Left/Save Right` и обновлять diff через `Recompare`.
   - спрашивать, что делать с unsaved changes перед `Compare`, `Recompare` и закрытием окна.
4. **CLI launcher** реализован:
   - `--left-file`, `--right-file`
   - `--left-dir`, `--right-dir`
   - `--recursive`, `--size`, `--date`
   - `--left-selected`, `--right-selected`
   - `--left-selected-list`, `--right-selected-list`
5. **Packaging** реализован:
   - `file_compare_tc.spec`
   - `scripts/build_exe.ps1`
   - собран `dist\FileCompareTC.exe`
6. **Docs** обновлены под сценарий Total Commander.
7. **Git** инициализирован локально:
   - основная ветка `main`
   - стартовый snapshot-коммит создан
   - workflow описан в `docs/GIT_WORKFLOW.md`
8. **Текущая рабочая ветка**:
   - `feature/edit-compared-files`
   - edit mode уже зафиксирован коммитом `07b839b`
   - ветка ещё не влита в `main`

### ✅ Что уже проверено

Техническая валидация:
```bash
python -m pytest tests -q
ruff check file_compare tests
```

Фактический результат:
- `49 passed`
- `ruff` без ошибок
- `PyInstaller` успешно собрал `dist\FileCompareTC.exe`

### 📦 Текущее deliverable

Главный артефакт:
```text
dist\FileCompareTC.exe
```

Размер на момент фиксации:
- `47,155,652 bytes`

Текущий контекст разработки:
- ветка: `feature/edit-compared-files`
- рабочее дерево чистое после коммита `07b839b`

### 🔧 Полезные команды

Проверка тестов:
```bash
python -m pytest tests -q
```

Проверка линтера:
```bash
ruff check file_compare tests
```

Пересборка EXE:
```bash
pip install -e ".[dev]"
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

Обычный запуск GUI:
```bash
file-compare
```

Ручной запуск TC launcher:
```bash
file-compare-cli --left-dir "D:\Left" --right-dir "D:\Right" --size --date
```

### 🧭 Настройка кнопки в Total Commander

`Command`
```text
D:\Development\file_compare_codex\dist\FileCompareTC.exe
```

`Parameters` для сравнения каталогов:
```text
--left-dir "%<Q" --right-dir "%>Q" --size --date
```

`Parameters` для сравнения текущего файла слева и справа:
```text
--left-file "%P%N" --right-file "%T%M" --size --date
```

`Parameters` для сравнения только selected items:
```text
--left-dir "%<Q" --right-dir "%>Q" --left-selected-list "%<$L" --right-selected-list "%>$L" --size --date
```

### ⏳ Что делать следующим

#### 1. Ручная проверка в Total Commander
- настроить кнопку на `dist\FileCompareTC.exe`
- использовать параметры `--left-file "%P%N" --right-file "%T%M" --size --date`
- открыть две UTF-8 text files на левой и правой панели
- запустить сравнение и убедиться, что кнопка `Edit Mode` активна
- войти в `Edit Mode`, изменить левый файл, нажать `Save Left`, затем `Recompare`
- повторить для правого файла через `Save Right`
- изменить текст и проверить prompt про unsaved changes при `Recompare`
- изменить текст и проверить prompt про unsaved changes при закрытии окна
- дополнительно открыть пару, где один файл `UTF-16` или binary, и убедиться, что редактирование недоступно

#### 2. Если selection placeholders не сработают
- уточнить, какие `%`-параметры поддерживает конкретная сборка Total Commander
- подогнать строку `Parameters` под эту версию

#### 3. Если ручная проверка успешна
- влить `feature/edit-compared-files` в `main`
- при необходимости удалить рабочую ветку

#### 4. Нефункциональные улучшения, если TC-интеграция подтвердится
- hotkey setup documentation
- иконка/branding для `EXE`
- UX-полировка GUI

#### 5. Ограничения режима редактирования
- редактирование доступно только для `--left-file/--right-file`
- поддерживаются только UTF-8 text files
- перед `Recompare`, `Compare` и закрытием окна приложение спрашивает, что делать с несохранёнными изменениями

### 🧪 Шаблон отчёта по ручной проверке в Total Commander

```md
## Manual TC Check — 2026-03-08

### Environment
- Total Commander version:
- Executable used: `dist\FileCompareTC.exe`
- Button command:
  `D:\Development\file_compare_codex\dist\FileCompareTC.exe`
- Button parameters:
  `--left-file "%P%N" --right-file "%T%M" --size --date`

### Scenario 1: explicit file pair, UTF-8
- Left file:
- Right file:
- Result:
- `Edit Mode` button state: PASS / FAIL
- Notes:

### Scenario 2: save left file
- Change made:
- `Save Left`: PASS / FAIL
- File updated on disk: PASS / FAIL
- `Recompare` after save: PASS / FAIL
- Notes:

### Scenario 3: save right file
- Change made:
- `Save Right`: PASS / FAIL
- File updated on disk: PASS / FAIL
- `Recompare` after save: PASS / FAIL
- Notes:

### Scenario 4: unsaved changes on recompare
- Prompt shown: PASS / FAIL
- `Save` path works: PASS / FAIL / NOT TESTED
- `Discard` path works: PASS / FAIL / NOT TESTED
- `Cancel` path works: PASS / FAIL / NOT TESTED
- Notes:

### Scenario 5: unsaved changes on window close
- Prompt shown: PASS / FAIL
- `Save` path works: PASS / FAIL / NOT TESTED
- `Discard` path works: PASS / FAIL / NOT TESTED
- `Cancel` path works: PASS / FAIL / NOT TESTED
- Notes:

### Scenario 6: non-UTF-8 or binary file
- File pair:
- `Edit Mode` disabled: PASS / FAIL
- Read-only hint shown: PASS / FAIL
- Notes:

### Final result
- Overall: PASS / FAIL
- Blocking issues:
- Follow-up tasks:
```
