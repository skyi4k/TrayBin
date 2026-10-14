import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

from config import AppConfig, resource_path
from settings_window import SettingsWindow
from single_instance import SingleInstance
import bin_manager

class TrayBinApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Single instance check
        self.single_instance = SingleInstance("TrayBin_Application_Mutex")
        if self.single_instance.is_running():
            print("TrayBin уже запущен в фоновом режиме.")
            msg = QMessageBox()
            msg.setWindowTitle("TrayBin")
            msg.setText("Приложение TrayBin уже запущено и находится в системном трее.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            sys.exit(0)

        self.config = AppConfig()
        self.settings_window = None

        # State tracking
        self.last_item_count = -1
        self.last_empty_state = None

        # Setup Tray
        self.tray_icon = QSystemTrayIcon()
        self.init_tray_menu()
        self.init_click_handler()

        self.tray_icon.show()

        # Update loop
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_bin_state)
        self.update_timer.start(1500)

        # Initial check
        self.check_bin_state(force=True)

    def init_tray_menu(self):
        self.tray_menu = QMenu()

        self.act_empty = QAction("🗑️  Очистить корзину", triggered=self.action_empty_bin)
        self.act_open = QAction("📂  Открыть корзину", triggered=self.action_open_bin)
        self.act_refresh = QAction("🔄  Обновить статус", triggered=lambda: self.check_bin_state(force=True))
        self.act_settings = QAction("⚙️  Настройки", triggered=self.action_open_settings)
        self.act_exit = QAction("❌  Выход", triggered=self.action_exit)

        self.tray_menu.addAction(self.act_empty)
        self.tray_menu.addAction(self.act_open)
        self.tray_menu.addAction(self.act_refresh)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.act_settings)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.act_exit)

        self.tray_icon.setContextMenu(self.tray_menu)

    def init_click_handler(self):
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.handle_single_click)

        self.tray_icon.activated.connect(self.on_tray_activated)

    def get_action_callable(self, action_key):
        mapping = {
            "empty_bin": self.action_empty_bin,
            "open_bin": self.action_open_bin,
            "open_settings": self.action_open_settings,
            "none": lambda: None
        }
        return mapping.get(action_key, lambda: None)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single Left Click
            self.click_timer.start(250)

        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.click_timer.stop()
            action = self.get_action_callable(self.config.double_click_action)
            action()

        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            action = self.get_action_callable(self.config.middle_click_action)
            action()

    def handle_single_click(self):
        action = self.get_action_callable(self.config.single_click_action)
        action()

    def load_icon_for_state(self, is_empty):
        preset = self.config.icon_theme
        custom_path = self.config.custom_icon_empty if is_empty else self.config.custom_icon_full

        if preset == "custom" and custom_path and os.path.exists(custom_path):
            return QIcon(custom_path)

        icon_file = "icons/bin-empty.ico" if is_empty else "icons/bin-full.ico"
        full_path = resource_path(icon_file)
        if os.path.exists(full_path):
            return QIcon(full_path)

        return QIcon()

    def check_bin_state(self, force=False):
        items, size_bytes = bin_manager.get_recycle_bin_info()
        is_empty = (items == 0)

        if force or (is_empty != self.last_empty_state) or (items != self.last_item_count):
            self.last_empty_state = is_empty
            self.last_item_count = items

            icon = self.load_icon_for_state(is_empty)
            self.tray_icon.setIcon(icon)

            if is_empty:
                tooltip = "TrayBin - Корзина: пуста"
            else:
                formatted = bin_manager.format_size(size_bytes)
                tooltip = f"TrayBin - Корзина: {items} объектов ({formatted})"
            self.tray_icon.setToolTip(tooltip)

            self.act_empty.setEnabled(not is_empty)

    def action_empty_bin(self):
        items_before, size_before = bin_manager.get_recycle_bin_info()
        if items_before == 0:
            if self.config.show_notification:
                self.tray_icon.showMessage(
                    "TrayBin",
                    "Корзина уже пуста.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500
                )
            return

        success, err, cleared_items, cleared_size = bin_manager.empty_recycle_bin(
            confirm=self.config.show_confirmation,
            play_sound=self.config.play_sound
        )

        self.check_bin_state(force=True)

        if success and self.config.show_notification:
            freed_str = bin_manager.format_size(cleared_size)
            if cleared_items > 0:
                msg = f"Корзина очищена! Удалено файлов: {cleared_items} ({freed_str})."
            else:
                msg = "Корзина успешно очищена."

            empty_icon = self.load_icon_for_state(True)
            self.tray_icon.showMessage("TrayBin", msg, empty_icon, 4000)
        elif not success and self.config.show_notification:
            self.tray_icon.showMessage(
                "TrayBin",
                f"Ошибка очистки корзины (Код: {err})",
                QSystemTrayIcon.MessageIcon.Warning,
                4000
            )

    def action_open_bin(self):
        bin_manager.open_recycle_bin()

    def action_open_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.config)
            self.settings_window.settings_changed.connect(lambda: self.check_bin_state(force=True))

        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def action_exit(self):
        self.single_instance.release()
        self.app.quit()

    def run(self):
        return self.app.exec()

def main():
    app = TrayBinApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
