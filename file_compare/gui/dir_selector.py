from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class DirSelector(QWidget):
    path_changed = Signal(Path)

    def __init__(self, label_text: str = "Directory:", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.label = QLabel(label_text)
        layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setMaximumHeight(24)
        layout.addWidget(self.line_edit)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setMaximumHeight(24)
        self.browse_btn.clicked.connect(self._browse)
        layout.addWidget(self.browse_btn)

        self._path = Path(".")

    def _browse(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", str(self._path))
        if dir_path:
            self.set_path(Path(dir_path))

    def set_label_text(self, label_text: str) -> None:
        self.label.setText(label_text)

    def set_browse_enabled(self, enabled: bool) -> None:
        self.browse_btn.setEnabled(enabled)

    def set_path(self, path: Path) -> None:
        self._path = path
        self.line_edit.setText(str(path))
        self.path_changed.emit(path)

    def get_path(self) -> Path:
        return self._path
