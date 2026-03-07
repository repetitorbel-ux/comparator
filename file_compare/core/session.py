from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from file_compare.core.comparator import Comparator
from file_compare.core.criteria import ByModifiedDate, ByName, BySize, Criterion
from file_compare.core.models import (
    FILE_PAIR_RELATIVE_PATH,
    ComparisonCategory,
    ComparisonResult,
)
from file_compare.core.scanner import build_file_entry, scan_directory, scan_selected_paths


@dataclass(frozen=True)
class ComparisonOptions:
    recursive: bool = False
    compare_name: bool = True
    compare_size: bool = False
    compare_date: bool = False


@dataclass(frozen=True)
class LaunchContext:
    left_dir: Path
    right_dir: Path
    options: ComparisonOptions = field(default_factory=ComparisonOptions)
    left_file: Path | None = None
    right_file: Path | None = None
    left_selected: tuple[Path, ...] = ()
    right_selected: tuple[Path, ...] = ()

    @property
    def uses_file_pair_mode(self) -> bool:
        return self.left_file is not None or self.right_file is not None

    @property
    def uses_selection_mode(self) -> bool:
        return bool(self.left_selected or self.right_selected)


def compare_from_context(context: LaunchContext) -> list[ComparisonResult]:
    validate_context(context)

    if context.uses_file_pair_mode:
        left_entries, right_entries = _scan_explicit_file_pair(context)
    elif context.uses_selection_mode:
        left_entries = scan_selected_paths(
            context.left_dir,
            context.left_selected,
            recursive=context.options.recursive,
        )
        right_entries = scan_selected_paths(
            context.right_dir,
            context.right_selected,
            recursive=context.options.recursive,
        )
    else:
        left_entries = scan_directory(context.left_dir, recursive=context.options.recursive)
        right_entries = scan_directory(context.right_dir, recursive=context.options.recursive)

    comparator = Comparator(build_criteria(context.options))
    return comparator.compare(left_entries, right_entries)


def build_criteria(options: ComparisonOptions) -> list[Criterion]:
    criteria: list[Criterion] = []
    if options.compare_name:
        criteria.append(ByName())
    if options.compare_size:
        criteria.append(BySize())
    if options.compare_date:
        criteria.append(ByModifiedDate())
    return criteria


def summarize_results(results: Iterable[ComparisonResult]) -> dict[ComparisonCategory, int]:
    summary = {category: 0 for category in ComparisonCategory}
    for result in results:
        summary[result.category] += 1
    return summary


def validate_context(context: LaunchContext) -> None:
    if context.uses_file_pair_mode:
        if context.left_file is None or context.right_file is None:
            raise ValueError("Explicit file mode requires both left and right files.")

        if context.left_selected or context.right_selected:
            raise ValueError("Explicit file mode cannot be combined with selection mode.")

        for side, file_path in (("left", context.left_file), ("right", context.right_file)):
            if not file_path.exists() or not file_path.is_file():
                raise ValueError(f"Invalid {side} file: {file_path}")
        return

    for side, directory in (("left", context.left_dir), ("right", context.right_dir)):
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid {side} directory: {directory}")

    if bool(context.left_selected) ^ bool(context.right_selected):
        raise ValueError(
            "Selection mode requires selections on both panels. "
            "Pass both left and right selections, or omit selections entirely."
        )


def _scan_explicit_file_pair(context: LaunchContext) -> tuple[list, list]:
    left_entry = build_file_entry(context.left_file, relative_path=FILE_PAIR_RELATIVE_PATH)
    right_entry = build_file_entry(context.right_file, relative_path=FILE_PAIR_RELATIVE_PATH)

    if left_entry is None or right_entry is None:
        raise ValueError("Unable to read one or both files for explicit file comparison.")

    return [left_entry], [right_entry]
