# Next Session: File Compare

## 📅 Статус на 06.03.2026

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

### ✅ Что уже проверено

Техническая валидация:
```bash
python -m pytest tests -q
ruff check file_compare tests
```

Фактический результат:
- `26 passed`
- `ruff` без ошибок
- `PyInstaller` успешно собрал `dist\FileCompareTC.exe`

### 📦 Текущее deliverable

Главный артефакт:
```text
dist\FileCompareTC.exe
```

Размер на момент фиксации:
- `47,155,652 bytes`

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
- проверить кнопку с параметрами `--left-file/--right-file`
- проверить запуск по hotkey
- проверить сценарий без selection
- проверить сценарий с selection в обеих панелях

#### 2. Если selection placeholders не сработают
- уточнить, какие `%`-параметры поддерживает конкретная сборка Total Commander
- подогнать строку `Parameters` под эту версию

#### 3. Нефункциональные улучшения, если TC-интеграция подтвердится
- hotkey setup documentation
- иконка/branding для `EXE`
- UX-полировка GUI
