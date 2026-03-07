from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QAction, QColor, QGuiApplication
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMenu, QSizePolicy, QTableView

from file_compare.core.models import ComparisonCategory, ComparisonResult


class ResultsModel(QAbstractTableModel):
    HEADERS = ["Name", "State", "Details", "Size (L)", "Size (R)", "Relative Path"]

    def __init__(self, results: list[ComparisonResult] | None = None):
        super().__init__()
        self._results = results or []

    def result_at(self, row: int) -> ComparisonResult | None:
        if row < 0 or row >= len(self._results):
            return None
        return self._results[row]

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._results)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        result = self._results[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return result.name
            if column == 1:
                return result.category.name
            if column == 2:
                return _format_details(result)
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
            return self.HEADERS[section]
        return None


class ResultsView(QTableView):
    result_selected = Signal(object)
    _MAX_VISIBLE_ROWS = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setVisible(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setModel(ResultsModel())
        self._apply_compact_height()

    def update_results(self, results: list[ComparisonResult]) -> None:
        self.setModel(ResultsModel(results))
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
        copy_action = QAction("Copy Name", self)
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


def _format_details(result: ComparisonResult) -> str:
    if result.category != ComparisonCategory.MISMATCH or not result.details:
        return "-"

    return ", ".join(sorted(result.details))
