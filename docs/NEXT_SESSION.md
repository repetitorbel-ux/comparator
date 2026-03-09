# Next Session: File Compare

## Статус на 09.03.2026

### Что актуально сейчас

1. `main` содержит все последние изменения:
- GUI локализация (`en`/`ru`) и сохранение языка;
- документация пользователя и интеграции TC;
- hardening CLI launcher для Total Commander;
- авто-выбор режима в универсальной кнопке TC.

2. Логика запуска из TC (актуальная):
- если переданы `--left-dir` и `--right-dir`, режим file-pair не используется;
- если есть selections с обеих сторон -> selected-items mode;
- иначе -> directory mode;
- мусорные `--left-dir/--right-dir` (например `Q`) подхватываются через parent валидных `--left-file/--right-file`.

3. Режим редактирования:
- доступен только для явной пары файлов (`--left-file/--right-file`);
- только UTF-8 text files;
- перед `Compare`, `Recompare` и закрытием окна есть prompt по unsaved changes.

## Проверено

Технические проверки:

```bash
python -m pytest tests -q
ruff check file_compare tests
```

Фактический результат:
- `60 passed`
- `ruff` без ошибок
- `PyInstaller` сборка успешна
- ручная проверка из Total Commander пройдена, включая проблемные кейсы:
  - каталоги без выделения;
  - асимметричные выделения;
  - mixed placeholders с fallback.

## Deliverable

Актуальный артефакт:

```text
dist\FileCompareTC.exe
```

Текущий размер:
- `47,326,025 bytes`

## Текущее состояние репозитория

- ветка: `main`
- HEAD: `637eb8a`
- `main` синхронизирован с `origin/main`
- рабочее дерево чистое

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
2. При UX-итерациях рассмотреть явный индикатор активного режима (`directories` / `selected-items` / `file-pair`) в статус-баре.
3. При релизной подготовке добавить версионирование иконки/branding для `FileCompareTC.exe`.
