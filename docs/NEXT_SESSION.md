# Next Session: File Compare

## Статус на 09.03.2026

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
5. **Локализация GUI** внедрена:
   - добавлен `file_compare/gui/localization.py` с переводами `en` и `ru`;
   - язык выбирается через combobox в главном окне;
   - выбор языка сохраняется через `QSettings`;
   - стартовый язык определяется по сохранённой настройке, иначе по system locale;
   - основные GUI-компоненты (`MainWindow`, `CriteriaPanel`, `DirSelector`, `ResultsView`, `ContentCompareView`) умеют `retranslate_ui()` без потери текущего compare state;
   - локализованы основные статусы, подписи, diff-панель и prompt для unsaved changes.
6. **Packaging** реализован:
   - `file_compare_tc.spec`
   - `scripts/build_exe.ps1`
   - собран `dist\FileCompareTC.exe`
7. **Docs** обновлены под сценарий Total Commander.
8. **Git** инициализирован локально:
   - основная ветка `main`
   - стартовый snapshot-коммит создан
   - workflow описан в `docs/GIT_WORKFLOW.md`
9. **Git workflow** приведён к рабочему процессу этой среды:
   - каждая новая задача начинается с новой осмысленно названной ветки
   - основная ветка `main` синхронизируется с GitHub
   - merge на GitHub остаётся основным путём
   - preferred path через `gh pr create` / `gh pr merge` уже добавлен в `docs/GIT_WORKFLOW.md`
   - локальный `ff-only` merge в `main` описан как fallback, если GitHub/`gh` недоступны
   - для `git pull` / `git push` / удаления remote-веток зафиксировано правило повторного запуска вне sandbox при типичных ошибках среды

### ✅ Что уже проверено

Техническая валидация:
```bash
python -m pytest tests -q
ruff check file_compare tests
```

Фактический результат:
- `53 passed`
- `ruff` без ошибок
- локализация GUI проходит smoke-тесты:
  - авто-выбор `ru` по `ru_RU`
  - ручное переключение `en`/`ru`
  - сохранение выбора языка между окнами
  - prompt unsaved changes использует активный язык
- `PyInstaller` после i18n-изменений успешно пересобрал `dist\FileCompareTC.exe`
- предупреждения в `build/file_compare_tc/warn-file_compare_tc.txt` стандартные для Windows-сборки (`pwd`, `grp`, `fcntl`, `posix`) и не выглядят блокирующими
- CLI parser smoke-check пройден: `--help` работает, explicit file mode корректно собирает `LaunchContext`
- built `EXE` стартует локально; процесс поднимается без мгновенного падения
- ручная проверка в Total Commander после i18n-изменений выполнена: запуск и рабочий сценарий подтверждены

### 📦 Текущее deliverable

Главный артефакт:
```text
dist\FileCompareTC.exe
```

Размер последнего известного собранного артефакта:
- `47,221,466 bytes`

Текущий контекст разработки:
- активная ветка: `feature/gui-language-switch`
- HEAD: `def2b4e`
- рабочее дерево НЕ чистое:
  - изменены GUI-файлы и `tests/test_gui_smoke.py`
  - добавлен новый файл `file_compare/gui/localization.py`
  - есть лишний untracked `patch.txt` от служебной попытки патча; перед коммитом не включать его

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

#### 1. Завершить ветку `feature/gui-language-switch`
- проверить diff перед коммитом, особенно `file_compare/gui/localization.py` и `tests/test_gui_smoke.py`
- после финальной проверки закоммитить i18n-изменения отдельным осмысленным коммитом

#### 2. Если selection placeholders не сработают
- уточнить, какие `%`-параметры поддерживает конкретная сборка Total Commander
- подогнать строку `Parameters` под эту версию

#### 3. Нефункциональные улучшения, если TC-интеграция подтвердится
- hotkey setup documentation
- иконка/branding для `EXE`
- UX-полировка GUI

#### 4. Ограничения режима редактирования
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
