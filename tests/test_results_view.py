import pytest

from pathlib import Path


pytest.importorskip("PySide6")

from PySide6.QtCore import Qt

from file_compare.core.models import ComparisonCategory, ComparisonResult, FileEntry
from file_compare.gui.results_view import ResultsModel


def test_results_model_formats_mismatch_details():
    left = FileEntry(path=Path("a.txt"), relative_path=Path("a.txt"), size=10, created_time=0, modified_time=0)
    right = FileEntry(path=Path("a.txt"), relative_path=Path("a.txt"), size=20, created_time=0, modified_time=1)
    result = ComparisonResult(
        left=left,
        right=right,
        category=ComparisonCategory.MISMATCH,
        details={"Date": "Differs", "Size": "Differs"},
    )

    model = ResultsModel([result])
    state_index = model.index(0, 1)
    details_index = model.index(0, 2)

    assert model.data(state_index, Qt.DisplayRole) == "MISMATCH"
    assert model.data(details_index, Qt.DisplayRole) == "Date, Size"


def test_results_model_formats_plain_match_state():
    left = FileEntry(path=Path("a.txt"), relative_path=Path("a.txt"), size=10, created_time=0, modified_time=0)
    right = FileEntry(path=Path("a.txt"), relative_path=Path("a.txt"), size=10, created_time=0, modified_time=0)
    result = ComparisonResult(left=left, right=right, category=ComparisonCategory.MATCH)

    model = ResultsModel([result])
    state_index = model.index(0, 1)
    details_index = model.index(0, 2)

    assert model.data(state_index, Qt.DisplayRole) == "MATCH"
    assert model.data(details_index, Qt.DisplayRole) == "-"
