from __future__ import annotations

import argparse
import ctypes
import sys
from pathlib import Path
from typing import Sequence

from file_compare.core.session import ComparisonOptions, LaunchContext


class _CliArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - argparse API
        raise ValueError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = _CliArgumentParser(
        prog="file-compare-cli",
        description="Launch the File Compare GUI directly or with Total Commander context.",
    )
    parser.add_argument("--left-file", type=_parse_path_argument, help="Explicit file path from the left panel.")
    parser.add_argument("--right-file", type=_parse_path_argument, help="Explicit file path from the right panel.")
    parser.add_argument("--left-dir", type=_parse_path_argument, help="Left panel directory.")
    parser.add_argument("--right-dir", type=_parse_path_argument, help="Right panel directory.")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include subdirectories when scanning directories or selected folders.",
    )
    parser.add_argument("--size", action="store_true", help="Compare file sizes.")
    parser.add_argument("--date", action="store_true", help="Compare modification dates.")
    parser.add_argument(
        "--left-selected",
        action="append",
        default=[],
        metavar="PATH",
        help="Selected path relative to --left-dir. Can be passed multiple times.",
    )
    parser.add_argument(
        "--right-selected",
        action="append",
        default=[],
        metavar="PATH",
        help="Selected path relative to --right-dir. Can be passed multiple times.",
    )
    parser.add_argument(
        "--left-selected-list",
        type=_parse_path_argument,
        help="Text file containing left-panel selections, one path per line.",
    )
    parser.add_argument(
        "--right-selected-list",
        type=_parse_path_argument,
        help="Text file containing right-panel selections, one path per line.",
    )
    return parser


def parse_context(argv: Sequence[str] | None = None) -> LaunchContext | None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if (
        args.left_file is None
        and args.right_file is None
        and args.left_dir is None
        and args.right_dir is None
    ):
        return None

    if bool(args.left_file) ^ bool(args.right_file):
        parser.error("--left-file and --right-file must be provided together.")

    if args.left_file is not None and args.right_file is not None:
        if any(
            (
                args.left_dir is not None,
                args.right_dir is not None,
                args.left_selected,
                args.right_selected,
                args.left_selected_list is not None,
                args.right_selected_list is not None,
            )
        ):
            parser.error(
                "Explicit file mode cannot be combined with directory or selection arguments."
            )

        return LaunchContext(
            left_dir=args.left_file.parent,
            right_dir=args.right_file.parent,
            options=ComparisonOptions(
                recursive=args.recursive,
                compare_name=False,
                compare_size=args.size,
                compare_date=args.date,
            ),
            left_file=args.left_file,
            right_file=args.right_file,
        )

    if args.left_dir is None or args.right_dir is None:
        parser.error("--left-dir and --right-dir must be provided together.")

    left_selected = tuple(_load_selection_values(args.left_selected, args.left_selected_list))
    right_selected = tuple(_load_selection_values(args.right_selected, args.right_selected_list))

    if bool(left_selected) ^ bool(right_selected):
        parser.error(
            "Selection mode requires both left and right selections. "
            "Provide selections for both sides or omit them entirely."
        )

    return LaunchContext(
        left_dir=args.left_dir,
        right_dir=args.right_dir,
        options=ComparisonOptions(
            recursive=args.recursive,
            compare_name=True,
            compare_size=args.size,
            compare_date=args.date,
        ),
        left_selected=tuple(Path(item) for item in left_selected),
        right_selected=tuple(Path(item) for item in right_selected),
    )


def main(argv: Sequence[str] | None = None) -> int:
    try:
        context = parse_context(argv)
        return launch_gui(context, argv=argv)
    except ValueError as exc:
        _show_startup_error(str(exc))
        return 2


def launch_gui(context: LaunchContext | None, argv: Sequence[str] | None = None) -> int:
    from file_compare.gui.main_window import main as gui_main

    return gui_main(argv=argv, context=context)


def _load_selection_values(values: list[str], list_path: Path | None) -> list[str]:
    loaded_values = [_normalize_shell_value(value) for value in values if value]
    if list_path is None:
        return loaded_values

    if not list_path.exists():
        return loaded_values

    loaded_values.extend(_read_selection_file(list_path))
    return [value for value in loaded_values if value]


def _read_selection_file(path: Path) -> list[str]:
    raw_bytes = path.read_bytes()
    if raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16", "utf-8-sig", "utf-8")
    else:
        encodings = ("utf-8-sig", "utf-8", "utf-16")

    for encoding in encodings:
        try:
            content = raw_bytes.decode(encoding)
            break
        except UnicodeError:
            continue
    else:
        content = raw_bytes.decode("latin-1")

    return [line.strip().strip('"') for line in content.splitlines() if line.strip()]


def _parse_path_argument(value: str) -> Path:
    normalized = _normalize_shell_value(value)
    return Path(normalized)


def _normalize_shell_value(value: str) -> str:
    normalized = value.strip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {'"', "'"}:
        normalized = normalized[1:-1]
    return normalized.strip()


def _show_startup_error(message: str) -> None:
    full_message = f"File Compare failed to start:\n\n{message}"
    try:
        ctypes.windll.user32.MessageBoxW(None, full_message, "File Compare", 0x10)
    except Exception:
        print(full_message, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
