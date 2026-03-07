from __future__ import annotations

from pathlib import Path
from typing import Sequence

from file_compare.core.criteria import Criterion
from file_compare.core.models import ComparisonCategory, ComparisonResult, FileEntry


class Comparator:
    def __init__(self, criteria: Sequence[Criterion]):
        self.criteria = list(criteria)

    def compare(
        self,
        left_entries: Sequence[FileEntry],
        right_entries: Sequence[FileEntry],
    ) -> list[ComparisonResult]:
        """Compare file entries by relative path and configured criteria."""

        left_map = {entry.relative_path: entry for entry in left_entries}
        right_map = {entry.relative_path: entry for entry in right_entries}

        results: list[ComparisonResult] = []
        for relative_path in sorted(set(left_map) | set(right_map), key=_sort_key):
            left = left_map.get(relative_path)
            right = right_map.get(relative_path)
            result = ComparisonResult(left=left, right=right)

            if left and right:
                mismatch_details: dict[str, str] = {}
                for criterion in self.criteria:
                    if not criterion.matches(left, right):
                        mismatch_details[criterion.name] = "Differs"

                if mismatch_details:
                    result.category = ComparisonCategory.MISMATCH
                    result.details = mismatch_details
                else:
                    result.category = ComparisonCategory.MATCH
            elif left:
                result.category = ComparisonCategory.LEFT_ONLY
            else:
                result.category = ComparisonCategory.RIGHT_ONLY

            results.append(result)

        return results


def _sort_key(path: Path) -> tuple[int, str]:
    return (len(path.parts), str(path).lower())
