# Next Session: File Compare

## Git Workflow Guardrail

Always follow `docs/GIT_WORKFLOW.md`.

Checklist before starting or closing a task:

1. Confirm branch/state:
   - `git status --short --branch`
   - `git branch --show-current`
2. If you are on `main`, sync first and create a dedicated task branch (`feature/...`, `fix/...`, or `docs/...`).
3. Before close: run minimum checks:
   - `python -m pytest tests -q`
   - `ruff check file_compare tests`
4. Push task branch to GitHub and merge via PR (do not merge into local `main`).
5. After GitHub merge, sync local `main` from `origin/main`.

## Статус на 11.03.2026

### Что актуально сейчас

1. `main` содержит последние изменения по UX и запуску из TC:
- явный индикатор активного режима в статус-баре;
- статус завершения сравнения в формате `Режим: ... | Найдено: ...`;
- корректный fallback для мусорных `--left-dir/--right-dir` при mixed-аргументах TC.

2. Логика запуска из TC (актуальная):
- если переданы `--left-dir` и `--right-dir`, режим file-pair не используется;
- если есть selections с обеих сторон -> selected-items mode;
- иначе -> directory mode;
- если `--left-dir/--right-dir` невалидны, fallback идет через `--left-file/--right-file`:
  - если `--left-file/--right-file` указывают на каталоги -> используются сами каталоги;
  - если указывают на файлы -> используются parent-каталоги.

3. Режим редактирования (актуальный):
- доступен для выбранной строки результата, если есть хотя бы один существующий текстовый файл;
- работает не только для explicit file-pair, но и для строк из directory/selected-items результатов;
- для `LEFT_ONLY/RIGHT_ONLY` редактируется только существующая сторона;
- бинарные файлы остаются read-only;
- при сохранении используется исходная кодировка файла;
- перед `Compare`, `Recompare` и закрытием окна есть prompt по unsaved changes.

## Проверено

Технические проверки:

```bash
python -m pytest tests -q
ruff check file_compare tests
```

Фактический результат:
- `63 passed`
- `ruff` без ошибок
- `PyInstaller` сборка успешна
- ручная проверка из Total Commander пройдена для сценариев directories/selected-items/file-pair.

## Deliverable

Актуальный артефакт:

```text
dist\FileCompareTC.exe
```

## Текущее состояние репозитория

- ветка: `main`
- HEAD: `5e0f21c`
- `main` синхронизирован с `origin/main`

## Настройка Total Commander (рекомендуемая)

`Command`:

```text
D:\Development\file_compare_codex\dist\FileCompareTC.exe
```

`Parameters` (универсальная кнопка):

```text
--left-dir "%<Q" --right-dir "%>Q" --left-file "%P%N" --right-file "%T%M" --left-selected-list "%<$L" --right-selected-list "%>$L" --size --date
```

Дополнительно:
- для принудительного file-pair mode используй отдельную кнопку без `--left-dir` / `--right-dir`.

## Полезные команды

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

## Что делать следующим

1. Если будут новые кейсы TC placeholder-ов, сохранять точную строку `Parameters` и сообщение ошибки для регрессионного теста.
2. При UX-итерациях можно добавить визуальный маркер side availability в `Edit Mode` для `LEFT_ONLY/RIGHT_ONLY`.
3. При релизной подготовке добавить версионирование иконки/branding для `FileCompareTC.exe`.
