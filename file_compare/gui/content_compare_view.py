from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontDatabase, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from file_compare.core.content_diff import DiffKind, DiffRow, build_side_by_side_rows, read_text_lines
from file_compare.core.models import ComparisonResult


class ContentCompareView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_rows: list[DiffRow] = []
        self._diff_row_indexes: list[int] = []
        self._current_diff_position = -1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)
        self.prev_diff_btn = QPushButton("Previous Difference")
        self.prev_diff_btn.clicked.connect(self.show_previous_difference)
        self.prev_diff_btn.setMaximumHeight(22)
        self.next_diff_btn = QPushButton("Next Difference")
        self.next_diff_btn.clicked.connect(self.show_next_difference)
        self.next_diff_btn.setMaximumHeight(22)
        self.diff_counter = QLabel("Differences: 0/0")
        controls_layout.addWidget(self.prev_diff_btn)
        controls_layout.addWidget(self.next_diff_btn)
        controls_layout.addWidget(self.diff_counter)
        controls_layout.addStretch(1)
        layout.addLayout(controls_layout)

        self.paths_header = QWidget()
        self.paths_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.paths_header.setMaximumHeight(24)
        header_layout = QHBoxLayout(self.paths_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        self.left_path = QLineEdit()
        self.left_path.setReadOnly(True)
        self.left_path.setMaximumHeight(22)
        self.right_path = QLineEdit()
        self.right_path.setReadOnly(True)
        self.right_path.setMaximumHeight(22)
        header_layout.addWidget(_build_labeled_field("Left:", self.left_path))
        header_layout.addWidget(_build_labeled_field("Right:", self.right_path))
        layout.addWidget(self.paths_header)

        editors_splitter = QSplitter(Qt.Horizontal)
        self.left_editor = _build_editor()
        self.right_editor = _build_editor()
        editors_splitter.addWidget(self.left_editor)
        editors_splitter.addWidget(self.right_editor)
        editors_splitter.setChildrenCollapsible(False)
        editors_splitter.setHandleWidth(1)
        editors_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(editors_splitter, stretch=1)

        self._syncing_scroll = False
        self._bind_scrollbars(self.left_editor, self.right_editor)
        self._bind_scrollbars(self.right_editor, self.left_editor)
        self._bind_horizontal_scrollbars(self.left_editor, self.right_editor)
        self._bind_horizontal_scrollbars(self.right_editor, self.left_editor)

        self.clear_comparison()

    def set_paths_visible(self, visible: bool) -> None:
        self.paths_header.setVisible(visible)

    def clear_comparison(self) -> None:
        self._current_rows = []
        self._diff_row_indexes = []
        self._current_diff_position = -1
        self.left_path.setText("")
        self.right_path.setText("")
        self.left_editor.setPlainText("Select a compared row to inspect file contents.")
        self.right_editor.setPlainText("Select a compared row to inspect file contents.")
        self.left_editor.setExtraSelections([])
        self.right_editor.setExtraSelections([])
        self._update_diff_controls()

    def show_result(self, result: ComparisonResult | None) -> None:
        if result is None:
            self.clear_comparison()
            return

        if result.left and result.right:
            self.show_file_pair(result.left.path, result.right.path)
            return

        if result.left:
            self.show_single_file(result.left.path, missing_side="right")
            return

        if result.right:
            self.show_single_file(result.right.path, missing_side="left")
            return

        self.clear_comparison()

    def show_file_pair(self, left_path: Path, right_path: Path) -> None:
        rows = build_side_by_side_rows(left_path, right_path)
        self.left_path.setText(str(left_path))
        self.right_path.setText(str(right_path))
        self._populate_editors(rows)

    def show_single_file(self, file_path: Path, *, missing_side: str) -> None:
        lines = read_text_lines(file_path)
        line_count_width = max(2, len(str(max(len(lines), 1))))
        formatted_lines = [
            _format_line(line_no=index + 1, text=line, width=line_count_width)
            for index, line in enumerate(lines)
        ]
        if not formatted_lines:
            formatted_lines = [_format_line(line_no=1, text="", width=line_count_width)]

        if missing_side == "right":
            self.left_path.setText(str(file_path))
            self.right_path.setText("Missing on right side")
            self.left_editor.setPlainText("\n".join(formatted_lines))
            self.right_editor.setPlainText("\n".join(_format_blank_line(line_count_width) for _ in formatted_lines))
            self.left_editor.setExtraSelections(_build_uniform_selections(self.left_editor, QColor(255, 230, 230)))
            self.right_editor.setExtraSelections([])
            self._current_rows = []
            self._diff_row_indexes = []
            self._current_diff_position = -1
            self._update_diff_controls()
            return

        self.left_path.setText("Missing on left side")
        self.right_path.setText(str(file_path))
        self.left_editor.setPlainText("\n".join(_format_blank_line(line_count_width) for _ in formatted_lines))
        self.right_editor.setPlainText("\n".join(formatted_lines))
        self.left_editor.setExtraSelections([])
        self.right_editor.setExtraSelections(_build_uniform_selections(self.right_editor, QColor(230, 235, 255)))
        self._current_rows = []
        self._diff_row_indexes = []
        self._current_diff_position = -1
        self._update_diff_controls()

    def _populate_editors(self, rows: list[DiffRow]) -> None:
        self._current_rows = rows
        self._diff_row_indexes = [
            line_index for line_index, row in enumerate(rows) if row.kind != DiffKind.EQUAL
        ]
        self._current_diff_position = 0 if self._diff_row_indexes else -1
        line_count_width = max(
            2,
            len(
                str(
                    max(
                        (row.left_line_no or 0 for row in rows),
                        default=0,
                    )
                )
            ),
            len(
                str(
                    max(
                        (row.right_line_no or 0 for row in rows),
                        default=0,
                    )
                )
            ),
        )

        if not rows:
            self.left_editor.setPlainText("")
            self.right_editor.setPlainText("")
            self.left_editor.setExtraSelections([])
            self.right_editor.setExtraSelections([])
            return

        left_lines = [
            _format_line(row.left_line_no, row.left_text, line_count_width)
            for row in rows
        ]
        right_lines = [
            _format_line(row.right_line_no, row.right_text, line_count_width)
            for row in rows
        ]
        self.left_editor.setPlainText("\n".join(left_lines))
        self.right_editor.setPlainText("\n".join(right_lines))
        self.left_editor.setExtraSelections(
            _build_diff_selections(self.left_editor, rows, pane="left", line_no_width=line_count_width)
        )
        self.right_editor.setExtraSelections(
            _build_diff_selections(self.right_editor, rows, pane="right", line_no_width=line_count_width)
        )
        self._update_diff_controls()
        if self._current_diff_position >= 0:
            self._scroll_to_diff(self._current_diff_position)

    def _bind_scrollbars(self, source: QPlainTextEdit, target: QPlainTextEdit) -> None:
        source.verticalScrollBar().valueChanged.connect(
            lambda value, source=source, target=target: self._sync_scroll(source, target, value)
        )

    def _bind_horizontal_scrollbars(self, source: QPlainTextEdit, target: QPlainTextEdit) -> None:
        source.horizontalScrollBar().valueChanged.connect(
            lambda value, source=source, target=target: self._sync_horizontal_scroll(source, target, value)
        )

    def _sync_scroll(self, source: QPlainTextEdit, target: QPlainTextEdit, value: int) -> None:
        del source
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        target.verticalScrollBar().setValue(value)
        self._syncing_scroll = False

    def _sync_horizontal_scroll(self, source: QPlainTextEdit, target: QPlainTextEdit, value: int) -> None:
        del source
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        target.horizontalScrollBar().setValue(value)
        self._syncing_scroll = False

    def show_next_difference(self) -> None:
        if not self._diff_row_indexes:
            return
        self._current_diff_position = (self._current_diff_position + 1) % len(self._diff_row_indexes)
        self._update_diff_controls()
        self._scroll_to_diff(self._current_diff_position)

    def show_previous_difference(self) -> None:
        if not self._diff_row_indexes:
            return
        self._current_diff_position = (self._current_diff_position - 1) % len(self._diff_row_indexes)
        self._update_diff_controls()
        self._scroll_to_diff(self._current_diff_position)

    def _update_diff_controls(self) -> None:
        has_diffs = bool(self._diff_row_indexes)
        self.prev_diff_btn.setEnabled(has_diffs)
        self.next_diff_btn.setEnabled(has_diffs)
        current = self._current_diff_position + 1 if has_diffs and self._current_diff_position >= 0 else 0
        total = len(self._diff_row_indexes)
        self.diff_counter.setText(f"Differences: {current}/{total}")

    def _scroll_to_diff(self, diff_position: int) -> None:
        if diff_position < 0 or diff_position >= len(self._diff_row_indexes):
            return
        line_index = self._diff_row_indexes[diff_position]
        _scroll_editor_to_line(self.left_editor, line_index)
        _scroll_editor_to_line(self.right_editor, line_index)


def _build_editor() -> QPlainTextEdit:
    editor = QPlainTextEdit()
    editor.setReadOnly(True)
    editor.setLineWrapMode(QPlainTextEdit.NoWrap)
    editor.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
    return editor


def _build_labeled_field(label_text: str, field: QLineEdit) -> QWidget:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    layout.addWidget(QLabel(label_text))
    layout.addWidget(field)
    return container


def _format_line(line_no: int | None, text: str, width: int) -> str:
    if line_no is None:
        return _format_blank_line(width)
    return f"{line_no:>{width}}: {text}"


def _format_blank_line(width: int) -> str:
    return " " * (width + 2)


def _build_diff_selections(
    editor: QPlainTextEdit,
    rows: list[DiffRow],
    *,
    pane: str,
    line_no_width: int,
) -> list[QPlainTextEdit.ExtraSelection]:
    selections: list[QTextEdit.ExtraSelection] = []
    for line_index, row in enumerate(rows):
        color = _color_for_row(row.kind, pane=pane)
        if color is None:
            continue
        selections.append(_make_line_selection(editor, line_index, color))
        spans = row.left_spans if pane == "left" else row.right_spans
        for start, end in spans:
            selections.append(
                _make_inline_selection(
                    editor,
                    line_index=line_index,
                    start_offset=line_no_width + 2 + start,
                    end_offset=line_no_width + 2 + end,
                    color=QColor(255, 210, 120),
                )
            )
    return selections


def _build_uniform_selections(
    editor: QPlainTextEdit,
    color: QColor,
) -> list[QPlainTextEdit.ExtraSelection]:
    block_count = editor.document().blockCount()
    return [_make_line_selection(editor, line_index, color) for line_index in range(block_count)]


def _make_line_selection(
    editor: QPlainTextEdit,
    line_index: int,
    color: QColor,
) -> QTextEdit.ExtraSelection:
    selection = QTextEdit.ExtraSelection()
    block = editor.document().findBlockByLineNumber(line_index)
    cursor = QTextCursor(block)
    selection.cursor = cursor
    selection.format = QTextCharFormat()
    selection.format.setBackground(color)
    selection.format.setProperty(QTextFormat.FullWidthSelection, True)
    return selection


def _make_inline_selection(
    editor: QPlainTextEdit,
    *,
    line_index: int,
    start_offset: int,
    end_offset: int,
    color: QColor,
) -> QTextEdit.ExtraSelection:
    selection = QTextEdit.ExtraSelection()
    block = editor.document().findBlockByLineNumber(line_index)
    cursor = QTextCursor(block)
    cursor.setPosition(block.position() + start_offset)
    cursor.setPosition(block.position() + end_offset, QTextCursor.KeepAnchor)
    selection.cursor = cursor
    selection.format = QTextCharFormat()
    selection.format.setBackground(color)
    return selection


def _scroll_editor_to_line(editor: QPlainTextEdit, line_index: int) -> None:
    block = editor.document().findBlockByLineNumber(line_index)
    if not block.isValid():
        return
    cursor = QTextCursor(block)
    editor.setTextCursor(cursor)
    editor.centerCursor()


def _color_for_row(kind: DiffKind, *, pane: str) -> QColor | None:
    if kind == DiffKind.EQUAL:
        return None
    if kind == DiffKind.REPLACE:
        return QColor(255, 245, 190)
    if kind == DiffKind.LEFT_ONLY:
        return QColor(255, 230, 230) if pane == "left" else QColor(250, 245, 245)
    if kind == DiffKind.RIGHT_ONLY:
        return QColor(245, 245, 250) if pane == "left" else QColor(230, 235, 255)
    return None
