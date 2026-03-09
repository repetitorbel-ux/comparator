# Total Commander Integration

`File Compare` is designed to run as an external tool from Total Commander.
It is not a native `WDX/WFX/WLX/WCX` plugin.

## Expected Deliverable

- One Windows executable: `FileCompareTC.exe`
- Total Commander command or hotkey that launches the executable
- The executable opens a GUI window with comparison results

## Supported Launch Modes

### 1. Compare the current file pair

Pass the full path to one file from each panel:

```text
--left-file "D:\Left\a.txt" --right-file "D:\Right\b.txt" --size --date
```

This mode is intended for the common Total Commander button workflow:

- highlight or focus one file in the left panel
- highlight or focus one file in the right panel
- press the button or hotkey

The launcher compares exactly those two files.

In GUI, this is also the only mode that enables in-app file editing:

- `Edit Mode` unlocks both text panes for editing
- `Save Left` and `Save Right` write changes back to disk independently
- `Recompare` refreshes the diff after saving or discarding local edits
- editing is available only for UTF-8 text files; non-UTF-8/binary files remain read-only

Recommended Total Commander button parameters:

```text
--left-file "%P%N" --right-file "%T%M" --size --date
```

This uses the current file in the source panel and the current file in the target panel.

### 2. Compare current directories

Pass left and right panel paths:

```text
--left-dir "%<Q" --right-dir "%>Q" --size --date
```

### 3. Compare only selected items

Pass left and right panel paths plus selection list files:

```text
--left-dir "%<Q" --right-dir "%>Q" --left-selected-list "%<$L" --right-selected-list "%>$L" --size --date
```

The launcher accepts:

- repeated `--left-selected` / `--right-selected` values
- list files via `--left-selected-list` / `--right-selected-list`

If both sides provide selections, only the selected items are compared.
If neither side provides selections, the whole directories are compared.

## Recommended Total Commander Setup

### Single universal button (recommended)

You can configure one command that works for all common scenarios:

```text
--left-dir "%<Q" --right-dir "%>Q" --left-file "%P%N" --right-file "%T%M" --left-selected-list "%<$L" --right-selected-list "%>$L" --size --date
```

Mode selection priority for this command:

1. if both selection lists are present, compare selected items;
2. otherwise compare directories.

Note:
- if `--left-dir` and `--right-dir` are passed, `--left-file` / `--right-file` are ignored.
- to force explicit file-pair mode, use a dedicated command without `--left-dir` / `--right-dir`.

### Menu or button command

- Command: path to `FileCompareTC.exe`
- Parameters:
  `--left-file "%P%N" --right-file "%T%M" --size --date`
- Start path: leave empty or point to the executable directory

### Hotkey workflow

- Add the command above to a user command or button
- Assign a hotkey in Total Commander to that command

## Notes

- Explicit file mode compares exactly one left file and one right file.
- In-app editing is limited to explicit file mode and UTF-8 text files.
- Selection mode is symmetric for MVP: selections must exist on both panels or on neither panel.
- The result always opens in a separate GUI window.
- The tool compares files only; it does not synchronize, copy, or modify panel contents.
