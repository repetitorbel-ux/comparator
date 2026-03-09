from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QAction, QColor, QGuiApplication
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMenu, QSizePolicy, QTableView

from file_compare.core.models import ComparisonCategory, ComparisonResult
from file_compare.gui.localization import UiLocalizer


class ResultsModel(QAbstractTableModel):
    def __init__(self, localizer: UiLocalizer | list[ComparisonResult] | None = None, results: list[ComparisonResult] | None = None):
        super().__init__()
        if isinstance(localizer, UiLocalizer):
            self.localizer = localizer
            self._results = results or []
        else:
            self.localizer = UiLocalizer(system_locale_name="en_US")
            self._results = localizer or []

    def result_at(self, row: int) -> ComparisonResult | None:
        if row < 0 or row >= len(self._results):
            return None
        return self._results[row]

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._results)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 6

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        result = self._results[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return result.name
            if column == 1:
                return _category_text(self.localizer, result.category)
            if column == 2:
                return _format_details(self.localizer, result)
            if column == 3:
                return str(result.left.size) if result.left else "-"
            if column == 4:
                return str(result.right.size) if result.right else "-"
            if column == 5:
                return str(result.relative_path)

        if role == Qt.BackgroundRole:
            if result.category == ComparisonCategory.MATCH:
                return QColor(200, 255, 200)
            if result.category == ComparisonCategory.LEFT_ONLY:
                return QColor(255, 200, 200)
            if result.category == ComparisonCategory.RIGHT_ONLY:
                return QColor(200, 200, 255)
            if result.category == ComparisonCategory.MISMATCH:
                return QColor(255, 255, 200)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return _header_text(self.localizer, section)
        return None

    def retranslate(self) -> None:
        if self.columnCount() > 0:
            self.headerDataChanged.emit(Qt.Horizontal, 0, self.columnCount() - 1)
        if self.rowCount() > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])


class ResultsView(QTableView):
    result_selected = Signal(object)
    _MAX_VISIBLE_ROWS = 6

    def __init__(self, localizer: UiLocalizer, parent=None):
        super().__init__(parent)
        self.localizer = localizer
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setModel(ResultsModel(self.localizer))
        self._apply_compact_height()

    def retranslate_ui(self) -> None:
        model = self.model()
        if isinstance(model, ResultsModel):
            model.retranslate()
        self.viewport().update()

    def update_results(self, results: list[ComparisonResult]) -> None:
        self.setModel(ResultsModel(self.localizer, results))
        self.selectionModel().currentRowChanged.connect(self._on_current_row_changed)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self._apply_compact_height()
        self.result_selected.emit(None)

    def select_first_row(self) -> None:
        model = self.model()
        if model.rowCount() == 0:
            return
        self.selectRow(0)

    def _on_current_row_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        del previous
        model = self.model()
        if not isinstance(model, ResultsModel):
            self.result_selected.emit(None)
            return
        self.result_selected.emit(model.result_at(current.row()))

    def _show_context_menu(self, pos) -> None:
        index = self.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu(self)
        copy_action = QAction(self.localizer.tr("results.copy_name"), self)
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(index))
        menu.addAction(copy_action)
        menu.exec(self.mapToGlobal(pos))

    def _copy_to_clipboard(self, index: QModelIndex) -> None:
        name_index = index.siblingAtColumn(0)
        data = self.model().data(name_index, Qt.DisplayRole)
        if data is not None:
            QGuiApplication.clipboard().setText(data)

    def _apply_compact_height(self) -> None:
        model = self.model()
        visible_rows = min(model.rowCount(), self._MAX_VISIBLE_ROWS)
        rows_height = sum(self.rowHeight(row) for row in range(visible_rows))
        if visible_rows == 0:
            rows_height = self.fontMetrics().height() + 8

        total_height = (
            self.horizontalHeader().height()
            + rows_height
            + (self.horizontalScrollBar().sizeHint().height() if self.horizontalScrollBar().isVisible() else 0)
            + (self.frameWidth() * 2)
        )
        self.setFixedHeight(total_height)


def _header_text(localizer: UiLocalizer, section: int) -> str:
    keys = (
        "results.header.name",
        "results.header.state",
        "results.header.details",
        "results.header.size_left",
        "results.header.size_right",
        "results.header.relative_path",
    )
    return localizer.tr(keys[section])


def _category_text(localizer: UiLocalizer, category: ComparisonCategory) -> str:
    if category == ComparisonCategory.MATCH:
        return localizer.tr("results.category.match")
    if category == ComparisonCategory.LEFT_ONLY:
        return localizer.tr("results.category.left_only")
    if category == ComparisonCategory.RIGHT_ONLY:
        return localizer.tr("results.category.right_only")
    return localizer.tr("results.category.mismatch")


def _format_details(localizer: UiLocalizer, result: ComparisonResult) -> str:
    if result.category != ComparisonCategory.MISMATCH or not result.details:
        return "-"

    translated = []
    for key in sorted(result.details):
        normalized = key.lower()
        if normalized == "name":
            translated.append(localizer.tr("results.detail.name"))
        elif normalized == "size":
            translated.append(localizer.tr("results.detail.size"))
        elif normalized == "date":
            translated.append(localizer.tr("results.detail.date"))
        else:
            translated.append(key)
    return ", ".join(translated)
