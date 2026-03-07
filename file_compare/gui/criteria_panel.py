from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout

from file_compare.core.session import ComparisonOptions


class CriteriaPanel(QGroupBox):
    criteria_changed = Signal()

    def __init__(self, parent=None):
        super().__init__("Comparison Criteria", parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 6)
        layout.setSpacing(10)

        self.name_cb = QCheckBox("Name (Always On)")
        self.name_cb.setChecked(True)
        self.name_cb.setEnabled(False)
        self.name_cb.toggled.connect(self.criteria_changed.emit)
        layout.addWidget(self.name_cb)

        self.size_cb = QCheckBox("Size")
        self.size_cb.toggled.connect(self.criteria_changed.emit)
        layout.addWidget(self.size_cb)

        self.date_cb = QCheckBox("Date Modified")
        self.date_cb.toggled.connect(self.criteria_changed.emit)
        layout.addWidget(self.date_cb)

        self.recursive_cb = QCheckBox("Include subdirectories (Recursive)")
        self.recursive_cb.toggled.connect(self.criteria_changed.emit)
        layout.addWidget(self.recursive_cb)

        layout.addStretch()

    def set_options(self, options: ComparisonOptions) -> None:
        self.name_cb.setChecked(options.compare_name)
        self.size_cb.setChecked(options.compare_size)
        self.date_cb.setChecked(options.compare_date)
        self.recursive_cb.setChecked(options.recursive)

    def set_name_toggle_enabled(self, enabled: bool) -> None:
        if enabled:
            self.name_cb.setText("Compare file names")
            self.name_cb.setEnabled(True)
            return

        self.name_cb.setText("Name (Always On)")
        self.name_cb.setChecked(True)
        self.name_cb.setEnabled(False)

    def to_options(self) -> ComparisonOptions:
        return ComparisonOptions(
            recursive=self.recursive_cb.isChecked(),
            compare_name=self.name_cb.isChecked(),
            compare_size=self.size_cb.isChecked(),
            compare_date=self.date_cb.isChecked(),
        )
