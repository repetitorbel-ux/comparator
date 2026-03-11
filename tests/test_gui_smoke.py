import pytest


pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication

from file_compare.core.session import ComparisonOptions, LaunchContext
from file_compare.gui.content_compare_view import PendingChangesDecision
from file_compare.gui.localization import UiLocalizer
from file_compare.gui.main_window import MainWindow


class _FakeMessageBox:
    Warning = object()
    AcceptRole = object()
    DestructiveRole = object()
    RejectRole = object()
    last_title = None
    last_text = None
    last_buttons = []

    def __init__(self, parent=None):
        self.parent = parent
        self._buttons = []
        self._clicked = None

    def setIcon(self, icon):
        self.icon = icon

    def setWindowTitle(self, title):
        _FakeMessageBox.last_title = title

    def setText(self, text):
        _FakeMessageBox.last_text = text

    def addButton(self, text, role):
        button = (text, role)
        self._buttons.append(button)
        _FakeMessageBox.last_buttons.append(button)
        if role is self.RejectRole:
            self._clicked = button
        return button

    def setDefaultButton(self, button):
        self.default = button

    def exec(self):
        return 0

    def clickedButton(self):
        return self._clicked


def _settings_path(temp_dir):
    return temp_dir / "ui.ini"


def make_localizer(temp_dir, *, language=None, system_locale_name="en_US"):
    settings = QSettings(str(_settings_path(temp_dir)), QSettings.IniFormat)
    settings.clear()
    if language is not None:
        settings.setValue("ui/language", language)
    settings.sync()
    return UiLocalizer(settings=settings, system_locale_name=system_locale_name)


def make_persistent_localizer(settings_path, *, system_locale_name="en_US"):
    settings = QSettings(str(settings_path), QSettings.IniFormat)
    return UiLocalizer(settings=settings, system_locale_name=system_locale_name)


def test_main_window_accepts_context(temp_dir):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(localizer=make_localizer(temp_dir))
    assert window.windowTitle() == "File Compare"
    assert window.compare_btn.text() == "Compare"
    assert window.language_combo.currentData() == "en"
    assert window.criteria_panel.name_cb.isEnabled() is False
    assert window.criteria_panel.name_cb.isChecked() is True
    assert window.paths_row.isHidden() is False
    assert window.content_compare_view.paths_header.isHidden() is False
    assert window.active_mode_label.text() == "Active mode: directories"
    window.close()
    del app


def test_main_window_uses_russian_from_system_locale(temp_dir):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(localizer=make_localizer(temp_dir, system_locale_name="ru_RU"))
    assert window.windowTitle() == "Сравнение файлов"
    assert window.compare_btn.text() == "Сравнить"
    assert window.language_combo.currentData() == "ru"
    window.close()
    del app


def test_main_window_shows_file_labels_for_explicit_file_mode(left_dir, right_dir, create_file, temp_dir):
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
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    assert window.paths_row.isHidden() is True
    assert window.criteria_panel.name_cb.isEnabled() is True
    assert window.criteria_panel.name_cb.isChecked() is False
    assert window.content_compare_view.paths_header.isHidden() is False
    assert window.active_mode_label.text() == "Active mode: file pair"

    window.close()
    del app


def test_main_window_populates_content_compare_for_explicit_file_mode(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
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
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    assert window.content_compare_view.left_path.text() == str(left_file)
    assert window.content_compare_view.right_path.text() == str(right_file)
    assert "1: alpha" in window.content_compare_view.left_editor.toPlainText()
    assert "2: beta" in window.content_compare_view.left_editor.toPlainText()
    assert "2: gamma" in window.content_compare_view.right_editor.toPlainText()
    assert window.content_compare_view.diff_counter.text() == "Differences: 1/1"
    assert window.content_compare_view.edit_mode_btn.isEnabled() is True
    assert window.content_compare_view.left_editor.isReadOnly() is True
    assert window.content_compare_view.right_editor.isReadOnly() is True

    window.close()
    del app


def test_main_window_uses_updated_name_checkbox_for_explicit_file_mode(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
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
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
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
    temp_dir,
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
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
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


def test_content_compare_view_enters_edit_mode_and_saves_left_file(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.content_compare_view.enter_edit_mode()
    app.processEvents()

    assert window.content_compare_view.left_editor.isReadOnly() is False
    assert window.content_compare_view.right_editor.isReadOnly() is False
    assert window.content_compare_view.left_editor.toPlainText() == "alpha\nbeta\n"
    assert window.content_compare_view.diff_counter.text() == "Differences: pending recompare"

    window.content_compare_view.left_editor.setPlainText("updated\nleft\n")
    app.processEvents()
    assert window.content_compare_view.save_left_btn.isEnabled() is True
    assert window.content_compare_view.save_right_btn.isEnabled() is False

    assert window.content_compare_view.save_document("left", window) is True
    assert left_file.read_text(encoding="utf-8") == "updated\nleft\n"
    assert window.content_compare_view.save_left_btn.isEnabled() is False

    window.close()
    del app


def test_content_compare_view_confirms_discard_before_recompare(
    left_dir,
    right_dir,
    create_file,
    monkeypatch,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.content_compare_view.enter_edit_mode()
    window.content_compare_view.left_editor.setPlainText("draft")
    app.processEvents()

    monkeypatch.setattr(
        window.content_compare_view,
        "_prompt_unsaved_changes",
        lambda parent, action_name: PendingChangesDecision.DISCARD,
    )

    assert window.content_compare_view.confirm_pending_changes(window, action_name="recompare") is True
    assert window.content_compare_view.left_editor.toPlainText() == "alpha\nbeta\n"

    window.close()
    del app


def test_content_compare_view_cancel_keeps_unsaved_changes(
    left_dir,
    right_dir,
    create_file,
    monkeypatch,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.content_compare_view.enter_edit_mode()
    window.content_compare_view.left_editor.setPlainText("draft")
    app.processEvents()

    monkeypatch.setattr(
        window.content_compare_view,
        "_prompt_unsaved_changes",
        lambda parent, action_name: PendingChangesDecision.CANCEL,
    )

    assert window.content_compare_view.confirm_pending_changes(window, action_name="closing the window") is False
    assert window.content_compare_view.left_editor.toPlainText() == "draft"

    monkeypatch.setattr(
        window.content_compare_view,
        "_prompt_unsaved_changes",
        lambda parent, action_name: PendingChangesDecision.DISCARD,
    )
    window.close()
    del app


def test_non_utf8_file_pair_can_be_edited_and_saved_in_original_encoding(
    left_dir,
    right_dir,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = left_dir / "left.txt"
    right_file = right_dir / "right.txt"
    left_file.write_text("alpha", encoding="utf-16")
    right_file.write_text("beta", encoding="utf-8")

    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    assert window.content_compare_view.edit_mode_btn.isEnabled() is True
    window.content_compare_view.enter_edit_mode()
    window.content_compare_view.left_editor.setPlainText("updated")
    app.processEvents()

    assert window.content_compare_view.save_document("left", window) is True
    assert left_file.read_text(encoding="utf-16") == "updated"

    window.close()
    del app



def test_language_switch_updates_visible_gui_texts_and_preserves_compare_state(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")
    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    before_left_text = window.content_compare_view.left_editor.toPlainText()
    before_right_text = window.content_compare_view.right_editor.toPlainText()
    assert window.results_view.model().headerData(1, Qt.Horizontal) == "State"

    window.language_combo.setCurrentIndex(1)
    app.processEvents()

    assert window.windowTitle() == "Сравнение файлов"
    assert window.compare_btn.text() == "Сравнить"
    assert window.criteria_panel.size_cb.text() == "Размер"
    assert window.results_view.model().headerData(1, Qt.Horizontal) == "Состояние"
    assert window.content_compare_view.edit_mode_btn.text() == "Режим редактирования"
    assert window.active_mode_label.text() == "Активный режим: пара файлов"
    assert window.content_compare_view.diff_counter.text() == "Отличия: 1/1"
    assert window.content_compare_view.left_path.text() == str(left_file)
    assert window.content_compare_view.right_path.text() == str(right_file)
    assert window.content_compare_view.left_editor.toPlainText() == before_left_text
    assert window.content_compare_view.right_editor.toPlainText() == before_right_text

    window.close()
    del app


def test_language_choice_persists_between_windows(temp_dir):
    app = QApplication.instance() or QApplication([])
    settings_path = _settings_path(temp_dir)
    window = MainWindow(localizer=make_persistent_localizer(settings_path))
    app.processEvents()

    window.language_combo.setCurrentIndex(1)
    app.processEvents()
    assert window.localizer.current_language == "ru"
    window.close()

    second_window = MainWindow(localizer=make_persistent_localizer(settings_path, system_locale_name="en_US"))
    app.processEvents()
    assert second_window.localizer.current_language == "ru"
    assert second_window.compare_btn.text() == "Сравнить"
    second_window.close()
    del app


def test_unsaved_changes_prompt_uses_active_language(
    left_dir,
    right_dir,
    create_file,
    monkeypatch,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    left_file = create_file(left_dir / "left.txt", content="alpha\nbeta\n")
    right_file = create_file(right_dir / "right.txt", content="alpha\ngamma\n")
    context = LaunchContext(
        left_dir=left_file.parent,
        right_dir=right_file.parent,
        left_file=left_file,
        right_file=right_file,
        options=ComparisonOptions(compare_name=False),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.language_combo.setCurrentIndex(1)
    window.content_compare_view.enter_edit_mode()
    window.content_compare_view.left_editor.setPlainText("draft")
    app.processEvents()

    import file_compare.gui.content_compare_view as content_compare_module

    _FakeMessageBox.last_title = None
    _FakeMessageBox.last_text = None
    _FakeMessageBox.last_buttons = []
    monkeypatch.setattr(content_compare_module, "QMessageBox", _FakeMessageBox)

    result = window.content_compare_view.confirm_pending_changes(
        window,
        action_name=window.localizer.tr("action.recompare"),
    )
    assert result is False
    assert _FakeMessageBox.last_title == "Несохраненные изменения"
    assert "повторным сравнением" in _FakeMessageBox.last_text
    assert any(button[0] == "Отмена" for button in _FakeMessageBox.last_buttons)

    window.content_compare_view._prompt_unsaved_changes = lambda parent, action_name: PendingChangesDecision.DISCARD
    window.close()
    del app

def test_directory_mode_selected_pair_allows_edit_mode(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    create_file(left_dir / "same.txt", content="left")
    create_file(right_dir / "same.txt", content="right-right")

    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        options=ComparisonOptions(compare_size=True),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.results_view.select_first_row()
    app.processEvents()

    assert window.content_compare_view.edit_mode_btn.isEnabled() is True
    window.content_compare_view.enter_edit_mode()
    app.processEvents()
    assert window.content_compare_view.left_editor.isReadOnly() is False
    assert window.content_compare_view.right_editor.isReadOnly() is False

    window.close()
    del app

def test_directory_mode_row_with_missing_side_disables_edit_mode(
    left_dir,
    right_dir,
    create_file,
    temp_dir,
):
    app = QApplication.instance() or QApplication([])
    create_file(left_dir / "a-left-only.txt", content="left")
    create_file(right_dir / "z-right-only.txt", content="right")

    context = LaunchContext(
        left_dir=left_dir,
        right_dir=right_dir,
        options=ComparisonOptions(),
    )
    window = MainWindow(initial_context=context, localizer=make_localizer(temp_dir))
    app.processEvents()

    window.results_view.selectRow(0)
    app.processEvents()

    assert window.content_compare_view.edit_mode_btn.isEnabled() is False
    assert window.content_compare_view.left_editor.isReadOnly() is True
    assert window.content_compare_view.right_editor.isReadOnly() is True

    window.close()
    del app
