import pytest


pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from file_compare.core.session import ComparisonOptions, LaunchContext
from file_compare.gui.main_window import MainWindow


def test_main_window_accepts_context():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    assert window.windowTitle() == "File Compare"
    assert window.criteria_panel.name_cb.isEnabled() is False
    assert window.criteria_panel.name_cb.isChecked() is True
    assert window.paths_row.isHidden() is False
    assert window.content_compare_view.paths_header.isHidden() is False
    window.close()
    del app


def test_main_window_shows_file_labels_for_explicit_file_mode(left_dir, right_dir, create_file):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="left")
    right_file = create_file(right_dir / "right.txt", content="right")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        options=ComparisonOptions(compare_name=False),
        left_file=left_file,
        right_file=right_file,
    )
    window = MainWindow(initial_context=context)
    app.processEvents()

    assert window.paths_row.isHidden() is True
    assert window.criteria_panel.name_cb.isEnabled() is True
    assert window.criteria_panel.name_cb.isChecked() is False
    assert window.content_compare_view.paths_header.isHidden() is False

    window.close()
    del app


def test_main_window_populates_content_compare_for_explicit_file_mode(
    left_dir,
    right_dir,
    create_file,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        options=ComparisonOptions(compare_name=False),
        left_file=left_file,
        right_file=right_file,
    )
    window = MainWindow(initial_context=context)
    app.processEvents()

    assert window.content_compare_view.left_path.text() == str(left_file)
    assert window.content_compare_view.right_path.text() == str(right_file)
    assert "1: alpha" in window.content_compare_view.left_editor.toPlainText()
    assert "2: beta" in window.content_compare_view.left_editor.toPlainText()
    assert "2: gamma" in window.content_compare_view.right_editor.toPlainText()
    assert window.content_compare_view.diff_counter.text() == "Differences: 1/1"

    window.close()
    del app


def test_main_window_uses_updated_name_checkbox_for_explicit_file_mode(
    left_dir,
    right_dir,
    create_file,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "a.txt", size=10)
    right_file = create_file(right_dir / "b.txt", size=10)

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=True),
    )
    window = MainWindow(initial_context=context)
    app.processEvents()

    assert window.criteria_panel.name_cb.isChecked() is True
    state_index = window.results_view.model().index(0, 1)
    assert window.results_view.model().data(state_index) == "MISMATCH"

    window.criteria_panel.name_cb.setChecked(False)
    window.on_compare()

    state_index = window.results_view.model().index(0, 1)
    assert window.results_view.model().data(state_index) == "MATCH"

    window.close()
    del app


def test_content_compare_view_syncs_horizontal_scroll_and_navigates_differences(
    left_dir,
    right_dir,
    create_file,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="same\n" + ("x" * 200) + "\nother-left\n")
    right_file = create_file(right_dir / "right.txt", content="same\n" + ("y" * 200) + "\nother-right\n")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
    )
    window = MainWindow(initial_context=context)
    app.processEvents()

    window.content_compare_view.left_editor.horizontalScrollBar().setValue(40)
    app.processEvents()
    assert window.content_compare_view.right_editor.horizontalScrollBar().value() == 40

    window.content_compare_view.show_next_difference()
    assert window.content_compare_view.diff_counter.text() == "Differences: 2/2"

    window.content_compare_view.show_previous_difference()
    assert window.content_compare_view.diff_counter.text() == "Differences: 1/2"

    window.close()
    del app
