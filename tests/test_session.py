from pathlib import Path

import pytest

from file_compare.core.models import ComparisonCategory
from file_compare.core.session import ComparisonOptions, LaunchContext, compare_from_context


def test_compare_from_context_scans_directories(left_dir, right_dir, create_file):
    create_file(left_dir / "same.txt", size=10)
    create_file(right_dir / "same.txt", size=10)

    context = LaunchContext(left_dir=left_dir, right_dir=right_dir)
    results = compare_from_context(context)

    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MATCH


def test_compare_from_context_uses_selected_items(left_dir, right_dir, create_file):
    create_file(left_dir / "chosen.txt", size=10)
    create_file(left_dir / "ignored.txt", size=10)
    create_file(right_dir / "chosen.txt", size=20)
    create_file(right_dir / "ignored.txt", size=10)

    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        options=ComparisonOptions(compare_size=True),
        left_selected=(Path("chosen.txt"),),
        right_selected=(Path("chosen.txt"),),
    )
    results = compare_from_context(context)

    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MISMATCH
    assert results[0].name == "chosen.txt"


def test_compare_from_context_uses_explicit_file_pair(left_dir, right_dir, create_file):
    left_file = create_file(left_dir / "left-name.txt", size=10)
    right_file = create_file(right_dir / "right-name.txt", size=20)

    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_size=True),
    )
    results = compare_from_context(context)

    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MISMATCH
    assert str(results[0].relative_path) == "left-name.txt vs right-name.txt"


def test_compare_from_context_can_ignore_name_for_explicit_file_pair(
    left_dir,
    right_dir,
    create_file,
):
    left_file = create_file(left_dir / "left-name.txt", size=10)
    right_file = create_file(right_dir / "right-name.txt", size=10)

    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False, compare_size=True),
    )
    results = compare_from_context(context)

    assert len(results) == 1
    assert results[0].category == ComparisonCategory.MATCH


def test_compare_from_context_rejects_one_sided_selection(left_dir, right_dir):
    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        left_selected=(Path("chosen.txt"),),
    )

    with pytest.raises(ValueError):
        compare_from_context(context)


def test_compare_from_context_rejects_one_sided_explicit_file(left_dir, right_dir):
    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        left_file=left_dir / "chosen.txt",
    )

    with pytest.raises(ValueError):
        compare_from_context(context)
