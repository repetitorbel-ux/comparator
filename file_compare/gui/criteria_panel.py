from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout

from file_compare.core.session import ComparisonOptions
from file_compare.gui.localization import UiLocalizer


class CriteriaPanel(QGroupBox):
    criteria_changed = Signal()

    def __init__(self, localizer: UiLocalizer, parent=None):
        super().__init__(parent)
        self.localizer = localizer
        self._name_toggle_enabled = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 6)
        layout.setSpacing(10)

        self.name_cb = QCheckBox()
        self.name_cb.setChecked(True)
        self.name_cb.setEnabled(False)
        self.name_cb.toggled.connect(lambda _checked=False: self.criteria_changed.emit())
        layout.addWidget(self.name_cb)

        self.size_cb = QCheckBox()
        self.size_cb.toggled.connect(lambda _checked=False: self.criteria_changed.emit())
        layout.addWidget(self.size_cb)

        self.date_cb = QCheckBox()
        self.date_cb.toggled.connect(lambda _checked=False: self.criteria_changed.emit())
        layout.addWidget(self.date_cb)

        self.recursive_cb = QCheckBox()
        self.recursive_cb.toggled.connect(lambda _checked=False: self.criteria_changed.emit())
        layout.addWidget(self.recursive_cb)

        layout.addStretch()
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setTitle(self.localizer.tr("criteria.group"))
        self.size_cb.setText(self.localizer.tr("criteria.size"))
        self.date_cb.setText(self.localizer.tr("criteria.date_modified"))
        self.recursive_cb.setText(self.localizer.tr("criteria.recursive"))
        if self._name_toggle_enabled:
            self.name_cb.setText(self.localizer.tr("criteria.compare_file_names"))
        else:
            self.name_cb.setText(self.localizer.tr("criteria.name_always_on"))

    def set_options(self, options: ComparisonOptions) -> None:
        self.name_cb.setChecked(options.compare_name)
        self.size_cb.setChecked(options.compare_size)
        self.date_cb.setChecked(options.compare_date)
        self.recursive_cb.setChecked(options.recursive)

    def set_name_toggle_enabled(self, enabled: bool) -> None:
        self._name_toggle_enabled = enabled
        if enabled:
            self.name_cb.setEnabled(True)
            self.name_cb.setText(self.localizer.tr("criteria.compare_file_names"))
            return

        self.name_cb.setText(self.localizer.tr("criteria.name_always_on"))
        self.name_cb.setChecked(True)
        self.name_cb.setEnabled(False)

    def to_options(self) -> ComparisonOptions:
        return ComparisonOptions(
            recursive=self.recursive_cb.isChecked(),
            compare_name=self.name_cb.isChecked(),
            compare_size=self.size_cb.isChecked(),
            compare_date=self.date_cb.isChecked(),
        )
