from pathlib import Path

from file_compare.core.models import (
    FILE_PAIR_RELATIVE_PATH,
    ComparisonCategory,
    ComparisonResult,
    FileEntry,
)

def test_file_entry_properties():
    path = Path("/tmp/test.txt")
    entry = FileEntry(
        path=path,
        relative_path=Path("test.txt"),
        size=100,
        created_time=0.0,
        modified_time=1.0
    )
    assert entry.name == "test.txt"

def test_comparison_result_match():
    left = FileEntry(Path("a"), Path("a"), 10, 0, 0)
    right = FileEntry(Path("b"), Path("b"), 10, 0, 0)
    res = ComparisonResult(left, right, ComparisonCategory.MATCH)
    assert res.name == "a"
    assert res.relative_path == Path("a")

def test_comparison_result_left_only():
    left = FileEntry(Path("a"), Path("a"), 10, 0, 0)
    res = ComparisonResult(left=left, category=ComparisonCategory.LEFT_ONLY)
    assert res.name == "a"
    assert res.relative_path == Path("a")


def test_comparison_result_file_pair_relative_path():
    left = FileEntry(Path("left/a.txt"), FILE_PAIR_RELATIVE_PATH, 10, 0, 0)
    right = FileEntry(Path("right/b.txt"), FILE_PAIR_RELATIVE_PATH, 10, 0, 0)
    res = ComparisonResult(left=left, right=right, category=ComparisonCategory.MISMATCH)
    assert res.relative_path == Path("a.txt vs b.txt")
