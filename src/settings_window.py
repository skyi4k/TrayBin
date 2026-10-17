import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QComboBox, QTabWidget, QWidget, QFileDialog, 
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from config import AppConfig, resource_path, APP_VERSION
from styles import get_stylesheet
from updater import CheckUpdateWorker, UpdateDialog
import bin_manager

class SettingsWindow(QDialog):
    settings_changed = pyqtSignal()

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config

        self.setWindowTitle("Настройки TrayBin")
        self.setFixedSize(460, 360)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowTitleHint)

        # Set window icon
        settings_ico = resource_path("icons/settings.ico")
        if os.path.exists(settings_ico):
            self.setWindowIcon(QIcon(settings_ico))

        self.apply_theme()
        self.init_ui()
        self.load_values()

    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.config.theme_mode))

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Tab Widget
        self.tabs = QTabWidget()

        # Tab 1: General
        self.tab_general = QWidget()
        self.setup_general_tab()
        self.tabs.addTab(self.tab_general, "Основные")

        # Tab 2: Appearance & Icons
        self.tab_icons = QWidget()
        self.setup_icons_tab()
        self.tabs.addTab(self.tab_icons, "Иконки")

        # Tab 3: Interaction
        self.tab_interaction = QWidget()
        self.setup_interaction_tab()
        self.tabs.addTab(self.tab_interaction, "Управление")

        # Tab 4: About
        self.tab_about = QWidget()
        self.setup_about_tab()
        self.tabs.addTab(self.tab_about, "О программе")

        main_layout.addWidget(self.tabs)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.hide)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setObjectName("primaryBtn")
        self.btn_save.clicked.connect(self.save_and_close)
        bottom_layout.addWidget(self.btn_save)

        main_layout.addLayout(bottom_layout)

    def setup_general_tab(self):
        layout = QVBoxLayout(self.tab_general)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)

        self.cb_autostart = QCheckBox("Запускать при старте Windows")
        self.cb_confirmation = QCheckBox("Запрашивать подтверждение перед очисткой")
        self.cb_notification = QCheckBox("Всплывающие уведомления при очистке")
        self.cb_sound = QCheckBox("Воспроизводить системный звук корзины")
        self.cb_check_updates = QCheckBox("Автоматически проверять обновления")

        layout.addWidget(self.cb_autostart)
        layout.addWidget(self.cb_confirmation)
        layout.addWidget(self.cb_notification)
        layout.addWidget(self.cb_sound)
        layout.addWidget(self.cb_check_updates)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Тема оформления окна:")
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("Тёмная (Dark)", "dark")
        self.combo_theme.addItem("Светлая (Light)", "light")
        self.combo_theme.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(self.combo_theme)

        layout.addSpacing(6)
        layout.addLayout(theme_layout)
        layout.addStretch()

    def setup_icons_tab(self):
        layout = QVBoxLayout(self.tab_icons)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)

        # Preset selection
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Набор иконок:")
        self.combo_icon_preset = QComboBox()
        self.combo_icon_preset.addItem("Windows (Системные)", "windows")
        self.combo_icon_preset.addItem("Пользовательские файлы (.ico, .png)", "custom")
        self.combo_icon_preset.currentIndexChanged.connect(self.on_icon_preset_changed)
        preset_layout.addWidget(preset_label)
        preset_layout.addStretch()
        preset_layout.addWidget(self.combo_icon_preset)
        layout.addLayout(preset_layout)

        # Custom icon pickers
        self.custom_icons_widget = QWidget()
        custom_layout = QVBoxLayout(self.custom_icons_widget)
        custom_layout.setContentsMargins(0, 4, 0, 0)
        custom_layout.setSpacing(8)

        # Empty icon picker
        empty_row = QHBoxLayout()
        empty_lbl = QLabel("Пустая корзина:")
        self.btn_empty_pick = QPushButton("Выбрать...")
        self.btn_empty_pick.clicked.connect(lambda: self.pick_custom_icon("empty"))
        self.btn_empty_reset = QPushButton("Сброс")
        self.btn_empty_reset.clicked.connect(lambda: self.reset_custom_icon("empty"))
        empty_row.addWidget(empty_lbl)
        empty_row.addStretch()
        empty_row.addWidget(self.btn_empty_pick)
        empty_row.addWidget(self.btn_empty_reset)
        custom_layout.addLayout(empty_row)

        # Full icon picker
        full_row = QHBoxLayout()
        full_lbl = QLabel("Полная корзина:")
        self.btn_full_pick = QPushButton("Выбрать...")
        self.btn_full_pick.clicked.connect(lambda: self.pick_custom_icon("full"))
        self.btn_full_reset = QPushButton("Сброс")
        self.btn_full_reset.clicked.connect(lambda: self.reset_custom_icon("full"))
        full_row.addWidget(full_lbl)
        full_row.addStretch()
        full_row.addWidget(self.btn_full_pick)
        full_row.addWidget(self.btn_full_reset)
        custom_layout.addLayout(full_row)

        layout.addWidget(self.custom_icons_widget)

        # Preview area
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 6px;")
        prev_layout = QHBoxLayout(preview_frame)
        prev_layout.addStretch()

        self.lbl_prev_empty = QLabel()
        self.lbl_prev_empty.setFixedSize(36, 36)
        self.lbl_prev_empty.setScaledContents(True)

        self.lbl_prev_full = QLabel()
        self.lbl_prev_full.setFixedSize(36, 36)
        self.lbl_prev_full.setScaledContents(True)

        prev_layout.addWidget(QLabel("Предпросмотр: "))
        prev_layout.addWidget(self.lbl_prev_empty)
        prev_layout.addSpacing(16)
        prev_layout.addWidget(self.lbl_prev_full)
        prev_layout.addStretch()
        layout.addWidget(preview_frame)

        layout.addStretch()

    def setup_interaction_tab(self):
        layout = QVBoxLayout(self.tab_interaction)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)

        actions = [
            ("Очистить корзину", "empty_bin"),
            ("Открыть корзину", "open_bin"),
            ("Открыть настройки", "open_settings"),
            ("Ничего не делать", "none")
        ]

        # Single click
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Одиночный клик (ЛКМ):"))
        self.combo_single = QComboBox()
        for text, data in actions:
            self.combo_single.addItem(text, data)
        row1.addStretch()
        row1.addWidget(self.combo_single)
        layout.addLayout(row1)

        # Double click
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Двойной клик (2x ЛКМ):"))
        self.combo_double = QComboBox()
        for text, data in actions:
            self.combo_double.addItem(text, data)
        row2.addStretch()
        row2.addWidget(self.combo_double)
        layout.addLayout(row2)

        # Middle click
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Клик колёсиком (СКМ):"))
        self.combo_middle = QComboBox()
        for text, data in actions:
            self.combo_middle.addItem(text, data)
        row3.addStretch()
        row3.addWidget(self.combo_middle)
        layout.addLayout(row3)

        info_lbl = QLabel("Примечание: Правый клик мыши всегда открывает контекстное меню приложения.")
        info_lbl.setObjectName("subHeaderLabel")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)
        layout.addStretch()

    def setup_about_tab(self):
        layout = QVBoxLayout(self.tab_about)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(8)

        title = QLabel(f"TrayBin v{APP_VERSION}")
        title.setObjectName("headerLabel")
        layout.addWidget(title)

        desc = QLabel(
            "Легковесная и быстрая утилита для Windows 10/11.\n"
            "Позволяет отслеживать состояние и моментально очищать Корзину прямо из системного трея."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Live stats
        self.lbl_stats = QLabel("Статус корзины: загрузка...")
        self.lbl_stats.setStyleSheet("color: #60CDFF; font-weight: bold;")
        layout.addWidget(self.lbl_stats)

        # Quick actions
        btn_row = QHBoxLayout()
        btn_empty_now = QPushButton("Очистить корзину")
        btn_empty_now.clicked.connect(self.quick_empty)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.update_stats)
        self.btn_check_update = QPushButton("Проверить обновления...")
        self.btn_check_update.clicked.connect(self.check_for_updates_manual)

        btn_row.addWidget(btn_empty_now)
        btn_row.addWidget(btn_refresh)
        btn_row.addWidget(self.btn_check_update)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()

        footer = QLabel("GitHub: github.com/skyi4k/TrayBin • Лицензия MIT")
        footer.setObjectName("subHeaderLabel")
        layout.addWidget(footer)

    def check_for_updates_manual(self):
        self.btn_check_update.setEnabled(False)
        self.btn_check_update.setText("Проверка...")
        self.update_worker = CheckUpdateWorker()
        self.update_worker.update_found.connect(self.on_update_found)
        self.update_worker.already_latest.connect(self.on_already_latest)
        self.update_worker.check_failed.connect(self.on_update_check_failed)
        self.update_worker.start()

    def on_update_found(self, rel_info):
        self.btn_check_update.setEnabled(True)
        self.btn_check_update.setText("Проверить обновления...")
        dlg = UpdateDialog(rel_info, self.config, self)
        dlg.exec()

    def on_already_latest(self, ver):
        self.btn_check_update.setEnabled(True)
        self.btn_check_update.setText("Проверить обновления...")
        QMessageBox.information(self, "Обновления", f"У вас установлена последняя версия TrayBin (v{ver}).")

    def on_update_check_failed(self, err):
        self.btn_check_update.setEnabled(True)
        self.btn_check_update.setText("Проверить обновления...")
        QMessageBox.warning(self, "Обновления", f"Не удалось проверить обновления:\n{err}")

    def load_values(self):
        self.cb_autostart.setChecked(self.config.autostart)
        self.cb_confirmation.setChecked(self.config.show_confirmation)
        self.cb_notification.setChecked(self.config.show_notification)
        self.cb_sound.setChecked(self.config.play_sound)
        self.cb_check_updates.setChecked(self.config.check_updates)

        # Theme
        idx_theme = self.combo_theme.findData(self.config.theme_mode)
        if idx_theme != -1:
            self.combo_theme.setCurrentIndex(idx_theme)

        # Icon Preset
        idx_preset = self.combo_icon_preset.findData(self.config.icon_theme)
        if idx_preset != -1:
            self.combo_icon_preset.setCurrentIndex(idx_preset)
        else:
            self.combo_icon_preset.setCurrentIndex(0)

        # Actions
        idx_single = self.combo_single.findData(self.config.single_click_action)
        if idx_single != -1:
            self.combo_single.setCurrentIndex(idx_single)

        idx_double = self.combo_double.findData(self.config.double_click_action)
        if idx_double != -1:
            self.combo_double.setCurrentIndex(idx_double)

        idx_middle = self.combo_middle.findData(self.config.middle_click_action)
        if idx_middle != -1:
            self.combo_middle.setCurrentIndex(idx_middle)

        self.on_icon_preset_changed()
        self.update_stats()

    def on_theme_changed(self):
        selected_theme = self.combo_theme.currentData()
        self.setStyleSheet(get_stylesheet(selected_theme))

    def on_icon_preset_changed(self):
        preset = self.combo_icon_preset.currentData()
        self.custom_icons_widget.setVisible(preset == "custom")
        self.update_icon_preview()

    def pick_custom_icon(self, icon_type):
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Выберите иконку ({icon_type})",
            "",
            "Иконки (*.ico *.png);;Все файлы (*.*)"
        )
        if path:
            if icon_type == "empty":
                self.config.custom_icon_empty = path
            else:
                self.config.custom_icon_full = path
            self.combo_icon_preset.setCurrentIndex(self.combo_icon_preset.findData("custom"))
            self.update_icon_preview()

    def reset_custom_icon(self, icon_type):
        if icon_type == "empty":
            self.config.custom_icon_empty = None
        else:
            self.config.custom_icon_full = None
        self.update_icon_preview()

    def update_icon_preview(self):
        preset = self.combo_icon_preset.currentData()
        empty_path = None
        full_path = None

        if preset == "custom":
            empty_path = self.config.custom_icon_empty
            full_path = self.config.custom_icon_full

        if not empty_path or not os.path.exists(empty_path):
            empty_path = resource_path("icons/bin-empty.ico")

        if not full_path or not os.path.exists(full_path):
            full_path = resource_path("icons/bin-full.ico")

        if os.path.exists(empty_path):
            self.lbl_prev_empty.setPixmap(QPixmap(empty_path))
        if os.path.exists(full_path):
            self.lbl_prev_full.setPixmap(QPixmap(full_path))

    def update_stats(self):
        items, size_bytes = bin_manager.get_recycle_bin_info()
        formatted = bin_manager.format_size(size_bytes)
        if items == 0:
            self.lbl_stats.setText("Корзина пуста (0 файлов, 0 Б)")
        else:
            self.lbl_stats.setText(f"В корзине: {items} объектов ({formatted})")

    def quick_empty(self):
        items, size = bin_manager.get_recycle_bin_info()
        if items == 0:
            QMessageBox.information(self, "TrayBin", "Корзина уже пуста.")
            return

        success, err, cleared_items, cleared_size = bin_manager.empty_recycle_bin(
            confirm=self.cb_confirmation.isChecked(),
            play_sound=self.cb_sound.isChecked()
        )
        self.update_stats()
        self.settings_changed.emit()

    def save_and_close(self):
        self.config.autostart = self.cb_autostart.isChecked()
        self.config.show_confirmation = self.cb_confirmation.isChecked()
        self.config.show_notification = self.cb_notification.isChecked()
        self.config.play_sound = self.cb_sound.isChecked()
        self.config.check_updates = self.cb_check_updates.isChecked()
        self.config.theme_mode = self.combo_theme.currentData()
        self.config.icon_theme = self.combo_icon_preset.currentData()

        self.config.single_click_action = self.combo_single.currentData()
        self.config.double_click_action = self.combo_double.currentData()
        self.config.middle_click_action = self.combo_middle.currentData()

        self.config.save()
        self.settings_changed.emit()
        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_values()
        screen = self.screen().availableGeometry()
        w = self.width()
        h = self.height()
        self.move(screen.right() - w - 24, screen.bottom() - h - 24)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
