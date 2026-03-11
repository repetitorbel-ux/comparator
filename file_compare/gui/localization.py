from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QLocale, QSettings


_TRANSLATIONS = {
    "en": {
        "window.title": "File Compare",
        "language.label": "Language:",
        "language.option.en": "EN",
        "language.option.ru": "RU",
        "button.compare": "Compare",
        "status.ready": "Ready",
        "status.scanning": "Scanning...",
        "status.comparison_failed": "Comparison failed.",
        "status.unexpected_error": "Unexpected error occurred.",
        "status.comparison_canceled": "Comparison canceled.",
        "status.comparison_complete": "Mode: {mode} | Found: {count}",
        "status.active_mode": "Active mode: {mode}",
        "mode.file_pair": "file pair",
        "mode.selected_items": "selected items",
        "mode.directories": "directories",
        "dialog.error.title": "Error",
        "dir_selector.browse": "Browse...",
        "dir_selector.select_directory": "Select Directory",
        "main.left_directory": "Left Directory:",
        "main.right_directory": "Right Directory:",
        "main.left_file": "Left File:",
        "main.right_file": "Right File:",
        "criteria.group": "Comparison Criteria",
        "criteria.name_always_on": "Name (Always On)",
        "criteria.compare_file_names": "Compare file names",
        "criteria.size": "Size",
        "criteria.date_modified": "Date Modified",
        "criteria.recursive": "Include subdirectories (Recursive)",
        "results.header.name": "Name",
        "results.header.state": "State",
        "results.header.details": "Details",
        "results.header.size_left": "Size (L)",
        "results.header.size_right": "Size (R)",
        "results.header.relative_path": "Relative Path",
        "results.copy_name": "Copy Name",
        "results.category.match": "MATCH",
        "results.category.left_only": "LEFT_ONLY",
        "results.category.right_only": "RIGHT_ONLY",
        "results.category.mismatch": "MISMATCH",
        "results.detail.name": "Name",
        "results.detail.size": "Size",
        "results.detail.date": "Date",
        "content.edit_mode": "Edit Mode",
        "content.save_left": "Save Left",
        "content.save_right": "Save Right",
        "content.recompare": "Recompare",
        "content.prev_difference": "Previous Difference",
        "content.next_difference": "Next Difference",
        "content.diff_counter": "Differences: {current}/{total}",
        "content.diff_counter_pending": "Differences: pending recompare",
        "content.left_label": "Left:",
        "content.right_label": "Right:",
        "content.placeholder.select_row": "Select a compared row to inspect file contents.",
        "content.missing_right": "Missing on right side",
        "content.missing_left": "Missing on left side",
        "content.edit_status.mode_edit": "Mode: Edit | Left: {left_state} | Right: {right_state}",
        "content.edit_status.mode_view": "Mode: View",
        "content.edit_state.modified": "modified",
        "content.edit_state.saved": "saved",
        "content.edit_hint.unavailable": "Editing is unavailable for this file pair.",
        "content.edit_hint.in_progress": "Editing local buffers. Use Recompare to refresh the diff.",
        "content.edit_hint.available": "Edit mode is available for text files.",
        "content.save_error.title": "Save Error",
        "content.save_error.message": "Unable to save {side} file:\n{path}\n\n{error}",
        "content.side.left": "left",
        "content.side.right": "right",
        "content.unsaved.title": "Unsaved Changes",
        "content.unsaved.message": "There are unsaved changes. What should happen before {action}?",
        "content.unsaved.save": "Save",
        "content.unsaved.discard": "Discard",
        "content.unsaved.cancel": "Cancel",
        "action.new_comparison": "starting a new comparison",
        "action.recompare": "recompare",
        "action.close_window": "closing the window",
    },
    "ru": {
        "window.title": "Сравнение файлов",
        "language.label": "Язык:",
        "language.option.en": "EN",
        "language.option.ru": "RU",
        "button.compare": "Сравнить",
        "status.ready": "Готово",
        "status.scanning": "Сканирование...",
        "status.comparison_failed": "Сравнение завершилось ошибкой.",
        "status.unexpected_error": "Произошла непредвиденная ошибка.",
        "status.comparison_canceled": "Сравнение отменено.",
        "status.comparison_complete": "Режим: {mode} | Найдено: {count}",
        "status.active_mode": "Активный режим: {mode}",
        "mode.file_pair": "пара файлов",
        "mode.selected_items": "выделенные элементы",
        "mode.directories": "каталоги",
        "dialog.error.title": "Ошибка",
        "dir_selector.browse": "Обзор...",
        "dir_selector.select_directory": "Выберите каталог",
        "main.left_directory": "Левый каталог:",
        "main.right_directory": "Правый каталог:",
        "main.left_file": "Левый файл:",
        "main.right_file": "Правый файл:",
        "criteria.group": "Критерии сравнения",
        "criteria.name_always_on": "Имя (всегда включено)",
        "criteria.compare_file_names": "Сравнивать имена файлов",
        "criteria.size": "Размер",
        "criteria.date_modified": "Дата изменения",
        "criteria.recursive": "Включая подкаталоги (рекурсивно)",
        "results.header.name": "Имя",
        "results.header.state": "Состояние",
        "results.header.details": "Детали",
        "results.header.size_left": "Размер (Л)",
        "results.header.size_right": "Размер (П)",
        "results.header.relative_path": "Относительный путь",
        "results.copy_name": "Копировать имя",
        "results.category.match": "СОВПАДАЕТ",
        "results.category.left_only": "ТОЛЬКО СЛЕВА",
        "results.category.right_only": "ТОЛЬКО СПРАВА",
        "results.category.mismatch": "НЕ СОВПАДАЕТ",
        "results.detail.name": "Имя",
        "results.detail.size": "Размер",
        "results.detail.date": "Дата",
        "content.edit_mode": "Режим редактирования",
        "content.save_left": "Сохранить слева",
        "content.save_right": "Сохранить справа",
        "content.recompare": "Сравнить заново",
        "content.prev_difference": "Предыдущее отличие",
        "content.next_difference": "Следующее отличие",
        "content.diff_counter": "Отличия: {current}/{total}",
        "content.diff_counter_pending": "Отличия: ожидание повторного сравнения",
        "content.left_label": "Слева:",
        "content.right_label": "Справа:",
        "content.placeholder.select_row": "Выберите строку сравнения, чтобы просмотреть содержимое файлов.",
        "content.missing_right": "Отсутствует справа",
        "content.missing_left": "Отсутствует слева",
        "content.edit_status.mode_edit": "Режим: редактирование | Левый: {left_state} | Правый: {right_state}",
        "content.edit_status.mode_view": "Режим: просмотр",
        "content.edit_state.modified": "изменен",
        "content.edit_state.saved": "сохранен",
        "content.edit_hint.unavailable": "Редактирование недоступно для этой пары файлов.",
        "content.edit_hint.in_progress": "Вы редактируете локальные буферы. Используйте повторное сравнение, чтобы обновить diff.",
        "content.edit_hint.available": "Режим редактирования доступен для текстовых файлов.",
        "content.save_error.title": "Ошибка сохранения",
        "content.save_error.message": "Не удалось сохранить {side} файл:\n{path}\n\n{error}",
        "content.side.left": "левый",
        "content.side.right": "правый",
        "content.unsaved.title": "Несохраненные изменения",
        "content.unsaved.message": "Есть несохраненные изменения. Что сделать перед действием: {action}?",
        "content.unsaved.save": "Сохранить",
        "content.unsaved.discard": "Отбросить",
        "content.unsaved.cancel": "Отмена",
        "action.new_comparison": "запуском нового сравнения",
        "action.recompare": "повторным сравнением",
        "action.close_window": "закрытием окна",
    },
}


@dataclass(slots=True)
class UiLocalizer:
    settings: QSettings | None = None
    system_locale_name: str | None = None
    current_language: str = field(init=False)

    def __post_init__(self) -> None:
        if self.settings is None:
            self.settings = QSettings("repetitorbel-ux", "file_compare")
        self.current_language = self.load_saved_language()

    def load_saved_language(self) -> str:
        saved = self.settings.value("ui/language", type=str)
        if saved in _TRANSLATIONS:
            return saved

        locale_name = self.system_locale_name or QLocale.system().name()
        return "ru" if str(locale_name).lower().startswith("ru") else "en"

    def save_language(self, code: str) -> None:
        self.settings.setValue("ui/language", code)
        self.settings.sync()

    def set_language(self, code: str) -> None:
        if code not in _TRANSLATIONS:
            raise ValueError(f"Unsupported language: {code}")
        self.current_language = code
        self.save_language(code)

    def tr(self, key: str, **kwargs: object) -> str:
        text = _TRANSLATIONS[self.current_language].get(key)
        if text is None:
            text = _TRANSLATIONS["en"].get(key, key)
        return text.format(**kwargs) if kwargs else text


