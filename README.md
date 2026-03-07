# File Compare

Utility for comparing directory contents by filename and attributes (size, date, etc.). Based on Python and PySide6.
This version is focused on Total Commander integration via an external GUI tool.

## Features
- **Compare by Name**: Find files that exist in both directories or only in one.
- **Compare by Size**: Identify files with matching names but different sizes.
- **Recursive Scan**: Architecture supports recursive scanning (currently disabled by default).
- **GUI**: User-friendly interface with PySide6.
- **Total Commander Launch Mode**: Start the GUI from Total Commander with panel directories, selected items, or an explicit file pair.
- **Selection-Aware Compare**: Compare entire directories or only the selected files from both panels.
- **Side-by-Side Content Diff**: Inspect selected file pairs in a lower split view with aligned lines and highlighted differences.
- **Extensible**: Strategy pattern allows adding new comparison criteria easily.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

### GUI
```bash
file-compare
# or
python -m file_compare.gui.main_window
```

### TC / CLI Launcher
```bash
file-compare-cli --help
file-compare-cli --left-dir "D:\Left" --right-dir "D:\Right" --size --date
file-compare-cli --left-file "D:\Left\a.txt" --right-file "D:\Right\b.txt" --size --date
```

When launched with `--left-file` and `--right-file`, the application compares exactly that file pair.
When launched with `--left-selected` and `--right-selected` values, the application compares only those items.
For Total Commander setup examples, see [docs/TOTAL_COMMANDER.md](docs/TOTAL_COMMANDER.md).

## Build EXE

Install dependencies and build:

```bash
pip install -e ".[dev]"
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

The expected executable name is `FileCompareTC`.

## Development

Run tests:
```bash
python -m pytest tests/
```

Check code style:
```bash
ruff check file_compare tests
```
