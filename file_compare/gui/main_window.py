from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from file_compare.core.session import LaunchContext, compare_from_context
from file_compare.gui.criteria_panel import CriteriaPanel
from file_compare.gui.content_compare_view import ContentCompareView
from file_compare.gui.dir_selector import DirSelector
from file_compare.gui.results_view import ResultsView


class MainWindow(QMainWindow):
    def __init__(self, initial_context: LaunchContext | None = None):
        super().__init__()
        self._launch_selection_context = initial_context
        self._last_compare_context: LaunchContext | None = None
        self._suppress_path_reset = False
        self._launch_compare_timer = QTimer(self)
        self._launch_compare_timer.setSingleShot(True)
        self._launch_compare_timer.timeout.connect(self.on_compare)

        self.setWindowTitle("File Compare")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        criteria_row = QHBoxLayout()
        criteria_row.setContentsMargins(0, 0, 0, 0)
        criteria_row.setSpacing(4)
        self.criteria_panel = CriteriaPanel()
        criteria_row.addWidget(self.criteria_panel, stretch=1)

        self.compare_btn = QPushButton("Compare")
        self.compare_btn.clicked.connect(self.on_compare)
        self.compare_btn.setStyleSheet("font-weight: bold; padding: 2px 8px;")
        self.compare_btn.setMaximumHeight(26)
        criteria_row.addWidget(self.compare_btn)
        main_layout.addLayout(criteria_row)

        self.paths_row = QWidget()
        top_layout = QHBoxLayout(self.paths_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)
        dirs_layout = QVBoxLayout()
        dirs_layout.setContentsMargins(0, 0, 0, 0)
        dirs_layout.setSpacing(1)
        self.left_dir = DirSelector("Left Directory:")
        self.right_dir = DirSelector("Right Directory:")
        self.left_dir.path_changed.connect(self._clear_launch_selections)
        self.right_dir.path_changed.connect(self._clear_launch_selections)
        dirs_layout.addWidget(self.left_dir)
        dirs_layout.addWidget(self.right_dir)
        top_layout.addLayout(dirs_layout, stretch=1)
        main_layout.addWidget(self.paths_row)

        self.results_view = ResultsView()
        self.results_view.result_selected.connect(self._show_selected_result)
        self.content_compare_view = ContentCompareView()
        self.content_compare_view.recompare_requested.connect(self._on_recompare_requested)
        main_layout.addWidget(self.results_view)
        main_layout.addWidget(self.content_compare_view, stretch=1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        if initial_context is not None:
            self._apply_context(initial_context)
            self._launch_compare_timer.start(0)

    def _apply_context(self, context: LaunchContext) -> None:
        self._suppress_path_reset = True
        self._apply_selector_mode(context)
        self.criteria_panel.set_options(context.options)
        self._suppress_path_reset = False

    def _apply_selector_mode(self, context: LaunchContext | None) -> None:
        if context is not None and context.uses_file_pair_mode:
            self.criteria_panel.set_name_toggle_enabled(True)
            self.paths_row.setVisible(False)
            self.left_dir.set_label_text("Left File:")
            self.right_dir.set_label_text("Right File:")
            self.left_dir.set_browse_enabled(False)
            self.right_dir.set_browse_enabled(False)
            self.left_dir.set_path(context.left_file)
            self.right_dir.set_path(context.right_file)
            return

        self.criteria_panel.set_name_toggle_enabled(False)
        self.paths_row.setVisible(True)
        self.left_dir.set_label_text("Left Directory:")
        self.right_dir.set_label_text("Right Directory:")
        self.left_dir.set_browse_enabled(True)
        self.right_dir.set_browse_enabled(True)
        if context is not None:
            self.left_dir.set_path(context.left_dir)
            self.right_dir.set_path(context.right_dir)

    def _clear_launch_selections(self, path: Path) -> None:
        del path
        if self._suppress_path_reset:
            return
        self._launch_selection_context = None
        self._last_compare_context = None
        self._apply_selector_mode(None)

    def _build_context_from_ui(self) -> LaunchContext:
        return LaunchContext(
            left_dir=self.left_dir.get_path(),
            right_dir=self.right_dir.get_path(),
            options=self.criteria_panel.to_options(),
        )

    def _build_context_for_compare(self) -> LaunchContext:
        current_options = self.criteria_panel.to_options()
        if self._launch_selection_context is None:
            return self._build_context_from_ui()

        context = self._launch_selection_context
        return LaunchContext(
            left_dir=context.left_dir,
            right_dir=context.right_dir,
            options=current_options,
            left_file=context.left_file,
            right_file=context.right_file,
            left_selected=context.left_selected,
            right_selected=context.right_selected,
        )

    @Slot()
    def on_compare(self) -> None:
        self._run_compare(action_name="starting a new comparison")

    @Slot()
    def _on_recompare_requested(self) -> None:
        self._run_compare(action_name="recompare")

    def _run_compare(self, *, action_name: str) -> None:
        if not self.content_compare_view.confirm_pending_changes(self, action_name=action_name):
            self.status_bar.showMessage("Comparison canceled.")
            return

        context = self._build_context_for_compare()
        self.status_bar.showMessage("Scanning...")
        QApplication.processEvents()

        try:
            results = compare_from_context(context)
        except ValueError as exc:
            QMessageBox.warning(self, "Error", str(exc))
            self.status_bar.showMessage("Comparison failed.")
            return
        except Exception as exc:  # pragma: no cover - defensive UI fallback
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("Unexpected error occurred.")
            return

        self._last_compare_context = context
        self.results_view.update_results(results)
        if context.uses_file_pair_mode and results:
            self.results_view.select_first_row()
        else:
            self.content_compare_view.clear_comparison()
        if context.uses_file_pair_mode:
            mode = "file pair"
        elif context.uses_selection_mode:
            mode = "selected items"
        else:
            mode = "directories"
        self.status_bar.showMessage(
            f"Comparison complete for {mode}. Found {len(results)} items."
        )

    @Slot(object)
    def _show_selected_result(self, result) -> None:
        allow_editing = bool(self._last_compare_context and self._last_compare_context.uses_file_pair_mode)
        self.content_compare_view.show_result(result, allow_editing=allow_editing)

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.content_compare_view.confirm_pending_changes(self, action_name="closing the window"):
            event.ignore()
            return
        super().closeEvent(event)


def main(
    argv: Sequence[str] | None = None,
    context: LaunchContext | None = None,
) -> int:
    app = QApplication.instance()
    owns_app = app is None
    if app is None:
        app = QApplication(list(argv) if argv is not None else sys.argv)

    window = MainWindow(initial_context=context)
    window.show()

    if owns_app:
        return app.exec()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
