from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFontDatabase, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from file_compare.core.content_diff import (
    DiffKind,
    DiffRow,
    build_side_by_side_rows,
    read_editable_text,
    read_text_lines,
)
from file_compare.core.models import ComparisonResult


class PendingChangesDecision(Enum):
    SAVE = auto()
    DISCARD = auto()
    CANCEL = auto()


@dataclass
class _OpenDocumentState:
    path: Path | None = None
    original_text: str = ""
    editable: bool = False
    reason: str = ""


class ContentCompareView(QWidget):
    recompare_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_rows: list[DiffRow] = []
        self._diff_row_indexes: list[int] = []
        self._current_diff_position = -1
        self._loading_editors = False
        self._explicit_pair_mode = False
        self._edit_supported = False
        self._in_edit_mode = False
        self._left_doc = _OpenDocumentState()
        self._right_doc = _OpenDocumentState()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)

        self.edit_mode_btn = QPushButton("Edit Mode")
        self.edit_mode_btn.clicked.connect(self.enter_edit_mode)
        self.edit_mode_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.edit_mode_btn)

        self.save_left_btn = QPushButton("Save Left")
        self.save_left_btn.clicked.connect(lambda: self.save_document("left"))
        self.save_left_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.save_left_btn)

        self.save_right_btn = QPushButton("Save Right")
        self.save_right_btn.clicked.connect(lambda: self.save_document("right"))
        self.save_right_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.save_right_btn)

        self.recompare_btn = QPushButton("Recompare")
        self.recompare_btn.clicked.connect(self.recompare_requested.emit)
        self.recompare_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.recompare_btn)

        self.prev_diff_btn = QPushButton("Previous Difference")
        self.prev_diff_btn.clicked.connect(self.show_previous_difference)
        self.prev_diff_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.prev_diff_btn)

        self.next_diff_btn = QPushButton("Next Difference")
        self.next_diff_btn.clicked.connect(self.show_next_difference)
        self.next_diff_btn.setMaximumHeight(22)
        controls_layout.addWidget(self.next_diff_btn)

        self.diff_counter = QLabel("Differences: 0/0")
        controls_layout.addWidget(self.diff_counter)

        self.edit_status = QLabel("")
        controls_layout.addWidget(self.edit_status)

        self.edit_hint = QLabel("")
        self.edit_hint.setWordWrap(False)
        controls_layout.addWidget(self.edit_hint, stretch=1)

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
        self.left_editor.textChanged.connect(lambda: self._on_editor_text_changed("left"))
        self.right_editor.textChanged.connect(lambda: self._on_editor_text_changed("right"))
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
        self._explicit_pair_mode = False
        self._edit_supported = False
        self._in_edit_mode = False
        self._left_doc = _OpenDocumentState()
        self._right_doc = _OpenDocumentState()
        self.left_path.setText("")
        self.right_path.setText("")
        self._set_editor_texts(
            "Select a compared row to inspect file contents.",
            "Select a compared row to inspect file contents.",
        )
        self.left_editor.setExtraSelections([])
        self.right_editor.setExtraSelections([])
        self._update_diff_controls()
        self._update_edit_controls()

    def show_result(self, result: ComparisonResult | None, *, allow_editing: bool = False) -> None:
        if result is None:
            self.clear_comparison()
            return

        if result.left and result.right:
            self.show_file_pair(result.left.path, result.right.path, allow_editing=allow_editing)
            return

        if result.left:
            self.show_single_file(result.left.path, missing_side="right")
            return

        if result.right:
            self.show_single_file(result.right.path, missing_side="left")
            return

        self.clear_comparison()

    def show_file_pair(self, left_path: Path, right_path: Path, *, allow_editing: bool = False) -> None:
        rows = build_side_by_side_rows(left_path, right_path)
        self.left_path.setText(str(left_path))
        self.right_path.setText(str(right_path))
        self._configure_pair_editing(left_path, right_path, allow_editing=allow_editing)
        self._populate_diff_editors(rows)

    def show_single_file(self, file_path: Path, *, missing_side: str) -> None:
        self._explicit_pair_mode = False
        self._edit_supported = False
        self._in_edit_mode = False
        self._left_doc = _OpenDocumentState()
        self._right_doc = _OpenDocumentState()

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
            self._set_editor_texts(
                "\n".join(formatted_lines),
                "\n".join(_format_blank_line(line_count_width) for _ in formatted_lines),
            )
            self.left_editor.setExtraSelections(_build_uniform_selections(self.left_editor, QColor(255, 230, 230)))
            self.right_editor.setExtraSelections([])
            self._current_rows = []
            self._diff_row_indexes = []
            self._current_diff_position = -1
            self._update_diff_controls()
            self._update_edit_controls()
            return

        self.left_path.setText("Missing on left side")
        self.right_path.setText(str(file_path))
        self._set_editor_texts(
            "\n".join(_format_blank_line(line_count_width) for _ in formatted_lines),
            "\n".join(formatted_lines),
        )
        self.left_editor.setExtraSelections([])
        self.right_editor.setExtraSelections(_build_uniform_selections(self.right_editor, QColor(230, 235, 255)))
        self._current_rows = []
        self._diff_row_indexes = []
        self._current_diff_position = -1
        self._update_diff_controls()
        self._update_edit_controls()

    def enter_edit_mode(self) -> None:
        if not self._edit_supported or self._in_edit_mode:
            return
        self._in_edit_mode = True
        self.left_editor.setExtraSelections([])
        self.right_editor.setExtraSelections([])
        self._set_editor_texts(self._left_doc.original_text, self._right_doc.original_text)
        self.left_editor.setReadOnly(False)
        self.right_editor.setReadOnly(False)
        self._update_diff_controls()
        self._update_edit_controls()

    def has_unsaved_changes(self) -> bool:
        return self._left_dirty() or self._right_dirty()

    def confirm_pending_changes(self, parent: QWidget, *, action_name: str) -> bool:
        if not self.has_unsaved_changes():
            return True

        decision = self._prompt_unsaved_changes(parent, action_name)
        if decision == PendingChangesDecision.CANCEL:
            return False
        if decision == PendingChangesDecision.DISCARD:
            self._discard_unsaved_changes()
            return True
        return self.save_all_dirty(parent)

    def save_document(self, side: str, parent: QWidget | None = None) -> bool:
        if side not in {"left", "right"}:
            raise ValueError(f"Unknown document side: {side}")

        document_state, editor = self._document_and_editor(side)
        if not document_state.editable or document_state.path is None:
            return False
        if editor.toPlainText() == document_state.original_text:
            self._update_edit_controls()
            return True

        try:
            document_state.path.write_text(editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(
                parent or self,
                "Save Error",
                f"Unable to save {side} file:\n{document_state.path}\n\n{exc}",
            )
            self._update_edit_controls()
            return False

        document_state.original_text = editor.toPlainText()
        self._update_edit_controls()
        return True

    def save_all_dirty(self, parent: QWidget | None = None) -> bool:
        if self._left_dirty() and not self.save_document("left", parent):
            return False
        if self._right_dirty() and not self.save_document("right", parent):
            return False
        return True

    def show_next_difference(self) -> None:
        if self._in_edit_mode or not self._diff_row_indexes:
            return
        self._current_diff_position = (self._current_diff_position + 1) % len(self._diff_row_indexes)
        self._update_diff_controls()
        self._scroll_to_diff(self._current_diff_position)

    def show_previous_difference(self) -> None:
        if self._in_edit_mode or not self._diff_row_indexes:
            return
        self._current_diff_position = (self._current_diff_position - 1) % len(self._diff_row_indexes)
        self._update_diff_controls()
        self._scroll_to_diff(self._current_diff_position)

    def _prompt_unsaved_changes(
        self,
        parent: QWidget,
        action_name: str,
    ) -> PendingChangesDecision:
        message_box = QMessageBox(parent)
        message_box.setIcon(QMessageBox.Warning)
        message_box.setWindowTitle("Unsaved Changes")
        message_box.setText(f"There are unsaved changes. What should happen before {action_name}?")
        save_button = message_box.addButton("Save", QMessageBox.AcceptRole)
        discard_button = message_box.addButton("Discard", QMessageBox.DestructiveRole)
        message_box.addButton("Cancel", QMessageBox.RejectRole)
        message_box.setDefaultButton(save_button)
        message_box.exec()

        clicked = message_box.clickedButton()
        if clicked == save_button:
            return PendingChangesDecision.SAVE
        if clicked == discard_button:
            return PendingChangesDecision.DISCARD
        return PendingChangesDecision.CANCEL

    def _discard_unsaved_changes(self) -> None:
        if self._in_edit_mode:
            self._set_editor_texts(self._left_doc.original_text, self._right_doc.original_text)
        self._update_edit_controls()

    def _configure_pair_editing(self, left_path: Path, right_path: Path, *, allow_editing: bool) -> None:
        self._explicit_pair_mode = allow_editing
        self._in_edit_mode = False
        self.left_editor.setReadOnly(True)
        self.right_editor.setReadOnly(True)
        self._left_doc = _load_document_state(left_path)
        self._right_doc = _load_document_state(right_path)
        self._edit_supported = (
            allow_editing and self._left_doc.editable and self._right_doc.editable
        )
        self._update_edit_controls()

    def _populate_diff_editors(self, rows: list[DiffRow]) -> None:
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
            self._set_editor_texts("", "")
            self.left_editor.setExtraSelections([])
            self.right_editor.setExtraSelections([])
            self._update_diff_controls()
            return

        left_lines = [
            _format_line(row.left_line_no, row.left_text, line_count_width)
            for row in rows
        ]
        right_lines = [
            _format_line(row.right_line_no, row.right_text, line_count_width)
            for row in rows
        ]
        self._set_editor_texts("\n".join(left_lines), "\n".join(right_lines))
        self.left_editor.setExtraSelections(
            _build_diff_selections(self.left_editor, rows, pane="left", line_no_width=line_count_width)
        )
        self.right_editor.setExtraSelections(
            _build_diff_selections(self.right_editor, rows, pane="right", line_no_width=line_count_width)
        )
        self._update_diff_controls()
        if self._current_diff_position >= 0:
            self._scroll_to_diff(self._current_diff_position)

    def _update_diff_controls(self) -> None:
        if self._in_edit_mode:
            self.prev_diff_btn.setEnabled(False)
            self.next_diff_btn.setEnabled(False)
            self.diff_counter.setText("Differences: pending recompare")
            return

        has_diffs = bool(self._diff_row_indexes)
        self.prev_diff_btn.setEnabled(has_diffs)
        self.next_diff_btn.setEnabled(has_diffs)
        current = self._current_diff_position + 1 if has_diffs and self._current_diff_position >= 0 else 0
        total = len(self._diff_row_indexes)
        self.diff_counter.setText(f"Differences: {current}/{total}")

    def _update_edit_controls(self) -> None:
        left_dirty = self._left_dirty()
        right_dirty = self._right_dirty()
        self.edit_mode_btn.setEnabled(self._edit_supported and not self._in_edit_mode)
        self.save_left_btn.setEnabled(self._in_edit_mode and left_dirty and self._left_doc.editable)
        self.save_right_btn.setEnabled(self._in_edit_mode and right_dirty and self._right_doc.editable)
        self.recompare_btn.setEnabled(self._explicit_pair_mode)

        if self._in_edit_mode:
            self.edit_status.setText(
                f"Mode: Edit | Left: {'modified' if left_dirty else 'saved'} | "
                f"Right: {'modified' if right_dirty else 'saved'}"
            )
        elif self._explicit_pair_mode:
            self.edit_status.setText("Mode: View")
        else:
            self.edit_status.setText("")

        if not self._explicit_pair_mode:
            self.edit_hint.setText("")
            return
        if not self._edit_supported:
            reason = self._left_doc.reason or self._right_doc.reason or "Editing is unavailable for this file pair."
            self.edit_hint.setText(reason)
            return
        if self._in_edit_mode:
            self.edit_hint.setText("Editing local buffers. Use Recompare to refresh the diff.")
            return
        self.edit_hint.setText("Edit mode is available for UTF-8 text files.")

    def _on_editor_text_changed(self, side: str) -> None:
        if self._loading_editors:
            return
        if not self._in_edit_mode:
            return
        self._update_edit_controls()

    def _document_and_editor(self, side: str) -> tuple[_OpenDocumentState, QPlainTextEdit]:
        if side == "left":
            return self._left_doc, self.left_editor
        return self._right_doc, self.right_editor

    def _left_dirty(self) -> bool:
        return self._in_edit_mode and self.left_editor.toPlainText() != self._left_doc.original_text

    def _right_dirty(self) -> bool:
        return self._in_edit_mode and self.right_editor.toPlainText() != self._right_doc.original_text

    def _set_editor_texts(self, left_text: str, right_text: str) -> None:
        self._loading_editors = True
        try:
            self.left_editor.setPlainText(left_text)
            self.right_editor.setPlainText(right_text)
        finally:
            self._loading_editors = False

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

    def _scroll_to_diff(self, diff_position: int) -> None:
        if diff_position < 0 or diff_position >= len(self._diff_row_indexes):
            return
        line_index = self._diff_row_indexes[diff_position]
        _scroll_editor_to_line(self.left_editor, line_index)
        _scroll_editor_to_line(self.right_editor, line_index)


def _load_document_state(path: Path) -> _OpenDocumentState:
    try:
        text = read_editable_text(path)
    except ValueError as exc:
        return _OpenDocumentState(path=path, editable=False, reason=str(exc))
    return _OpenDocumentState(path=path, original_text=text, editable=True)


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
