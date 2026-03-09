from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from PySide6.QtCore import QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
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
from file_compare.gui.localization import UiLocalizer
from file_compare.gui.results_view import ResultsView


class MainWindow(QMainWindow):
    def __init__(
        self,
        initial_context: LaunchContext | None = None,
        *,
        localizer: UiLocalizer | None = None,
    ):
        super().__init__()
        self.localizer = localizer or UiLocalizer()
        self._launch_selection_context = initial_context
        self._last_compare_context: LaunchContext | None = None
        self._suppress_path_reset = False
        self._updating_language_selector = False
        self._status_key = "status.ready"
        self._status_kwargs: dict[str, object] = {}
        self._launch_compare_timer = QTimer(self)
        self._launch_compare_timer.setSingleShot(True)
        self._launch_compare_timer.timeout.connect(self.on_compare)

        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        criteria_row = QHBoxLayout()
        criteria_row.setContentsMargins(0, 0, 0, 0)
        criteria_row.setSpacing(4)
        self.criteria_panel = CriteriaPanel(self.localizer)
        criteria_row.addWidget(self.criteria_panel, stretch=1)

        self.language_label = QLabel()
        criteria_row.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.setMaximumHeight(26)
        self.language_combo.addItem("", "en")
        self.language_combo.addItem("", "ru")
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        criteria_row.addWidget(self.language_combo)

        self.compare_btn = QPushButton()
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
        self.left_dir = DirSelector(self.localizer)
        self.right_dir = DirSelector(self.localizer)
        self.left_dir.path_changed.connect(self._clear_launch_selections)
        self.right_dir.path_changed.connect(self._clear_launch_selections)
        dirs_layout.addWidget(self.left_dir)
        dirs_layout.addWidget(self.right_dir)
        top_layout.addLayout(dirs_layout, stretch=1)
        main_layout.addWidget(self.paths_row)

        self.results_view = ResultsView(self.localizer)
        self.results_view.result_selected.connect(self._show_selected_result)
        self.content_compare_view = ContentCompareView(self.localizer)
        self.content_compare_view.recompare_requested.connect(self._on_recompare_requested)
        main_layout.addWidget(self.results_view)
        main_layout.addWidget(self.content_compare_view, stretch=1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        if initial_context is not None:
            self._apply_context(initial_context)

        self.retranslate_ui()
        if initial_context is not None:
            self._launch_compare_timer.start(0)

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self.localizer.tr("window.title"))
        self.language_label.setText(self.localizer.tr("language.label"))
        self.language_combo.setItemText(0, self.localizer.tr("language.option.en"))
        self.language_combo.setItemText(1, self.localizer.tr("language.option.ru"))
        self._updating_language_selector = True
        try:
            index = 0 if self.localizer.current_language == "en" else 1
            self.language_combo.setCurrentIndex(index)
        finally:
            self._updating_language_selector = False

        self.compare_btn.setText(self.localizer.tr("button.compare"))
        self.left_dir.retranslate_ui()
        self.right_dir.retranslate_ui()
        self.criteria_panel.retranslate_ui()
        self.results_view.retranslate_ui()
        self.content_compare_view.retranslate_ui()
        self._apply_selector_mode(self._launch_selection_context)
        self._refresh_status_message()

    def _set_status_message(self, key: str, **kwargs: object) -> None:
        self._status_key = key
        self._status_kwargs = kwargs
        self._refresh_status_message()

    def _refresh_status_message(self) -> None:
        self.status_bar.showMessage(self.localizer.tr(self._status_key, **self._status_kwargs))

    @Slot()
    def _on_language_changed(self) -> None:
        if self._updating_language_selector:
            return
        language = self.language_combo.currentData()
        if language == self.localizer.current_language:
            return
        self.localizer.set_language(language)
        self.retranslate_ui()

    def _apply_context(self, context: LaunchContext) -> None:
        self._suppress_path_reset = True
        self._apply_selector_mode(context)
        self.criteria_panel.set_options(context.options)
        self._suppress_path_reset = False

    def _apply_selector_mode(self, context: LaunchContext | None) -> None:
        self._suppress_path_reset = True
        try:
            if context is not None and context.uses_file_pair_mode:
                self.criteria_panel.set_name_toggle_enabled(True)
                self.paths_row.setVisible(False)
                self.left_dir.set_label_text(self.localizer.tr("main.left_file"))
                self.right_dir.set_label_text(self.localizer.tr("main.right_file"))
                self.left_dir.set_browse_enabled(False)
                self.right_dir.set_browse_enabled(False)
                self.left_dir.set_path(context.left_file)
                self.right_dir.set_path(context.right_file)
                return

            self.criteria_panel.set_name_toggle_enabled(False)
            self.paths_row.setVisible(True)
            self.left_dir.set_label_text(self.localizer.tr("main.left_directory"))
            self.right_dir.set_label_text(self.localizer.tr("main.right_directory"))
            self.left_dir.set_browse_enabled(True)
            self.right_dir.set_browse_enabled(True)
            if context is not None:
                self.left_dir.set_path(context.left_dir)
                self.right_dir.set_path(context.right_dir)
        finally:
            self._suppress_path_reset = False

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
        self._run_compare(action_name=self.localizer.tr("action.new_comparison"))

    @Slot()
    def _on_recompare_requested(self) -> None:
        self._run_compare(action_name=self.localizer.tr("action.recompare"))

    def _run_compare(self, *, action_name: str) -> None:
        if not self.content_compare_view.confirm_pending_changes(self, action_name=action_name):
            self._set_status_message("status.comparison_canceled")
            return

        context = self._build_context_for_compare()
        self._set_status_message("status.scanning")
        QApplication.processEvents()

        try:
            results = compare_from_context(context)
        except ValueError as exc:
            QMessageBox.warning(self, self.localizer.tr("dialog.error.title"), str(exc))
            self._set_status_message("status.comparison_failed")
            return
        except Exception as exc:  # pragma: no cover - defensive UI fallback
            QMessageBox.critical(self, self.localizer.tr("dialog.error.title"), str(exc))
            self._set_status_message("status.unexpected_error")
            return

        self._last_compare_context = context
        self.results_view.update_results(results)
        if context.uses_file_pair_mode and results:
            self.results_view.select_first_row()
        else:
            self.content_compare_view.clear_comparison()
        if context.uses_file_pair_mode:
            mode = self.localizer.tr("mode.file_pair")
        elif context.uses_selection_mode:
            mode = self.localizer.tr("mode.selected_items")
        else:
            mode = self.localizer.tr("mode.directories")
        self._set_status_message("status.comparison_complete", mode=mode, count=len(results))

    @Slot(object)
    def _show_selected_result(self, result) -> None:
        allow_editing = bool(self._last_compare_context and self._last_compare_context.uses_file_pair_mode)
        self.content_compare_view.show_result(result, allow_editing=allow_editing)

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.content_compare_view.confirm_pending_changes(
            self,
            action_name=self.localizer.tr("action.close_window"),
        ):
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

