import os
import sys
import winreg

REGISTRY_KEY = r"Software\TrayBin"
LEGACY_REGISTRY_KEY = r"Software\MiniBinKT"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_RUN_NAME = "TrayBin"

def resource_path(relative_path):
    """Возвращает корректный абсолютный путь для dev-режима и PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def open_reg_key(write=False):
    access = winreg.KEY_READ | (winreg.KEY_WRITE if write else 0)
    try:
        return winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0, access)
    except WindowsError:
        return None

def save_setting(name, value):
    """Сохраняет числовой или булевый параметр в реестр."""
    key = open_reg_key(write=True)
    if key:
        try:
            val_int = int(value)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, val_int)
        finally:
            winreg.CloseKey(key)

def load_setting(name, default=True):
    """Загружает булевый параметр из реестра с проверкой legacy-ключа."""
    for reg_path in [REGISTRY_KEY, LEGACY_REGISTRY_KEY]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return bool(val)
        except (FileNotFoundError, WindowsError):
            pass
    return default

def save_string_setting(name, value):
    """Сохраняет строковый параметр в реестр."""
    key = open_reg_key(write=True)
    if key:
        try:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
        finally:
            winreg.CloseKey(key)

def load_string_setting(name, default=""):
    """Загружает строковый параметр из реестра с проверкой legacy-ключа."""
    for reg_path in [REGISTRY_KEY, LEGACY_REGISTRY_KEY]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return str(val)
        except (FileNotFoundError, WindowsError):
            pass
    return default

def is_autostart_enabled():
    """Проверяет, включен ли автозапуск в Windows."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_RUN_NAME)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, WindowsError):
            pass
        winreg.CloseKey(key)
    except (FileNotFoundError, WindowsError):
        pass
    return False

def set_autostart(enabled):
    """Включает или выключает автозапуск программы при старте Windows."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        if enabled:
            exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, APP_RUN_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        else:
            try:
                winreg.DeleteValue(key, APP_RUN_NAME)
            except (FileNotFoundError, WindowsError):
                pass
        winreg.CloseKey(key)
    except WindowsError:
        pass

def save_icon_path(icon_type, path):
    """Сохраняет путь к кастомной иконке ('empty' или 'full')."""
    save_string_setting(f"custom_icon_{icon_type}", path)

def load_icon_path(icon_type):
    """Загружает путь к кастомной иконке."""
    val = load_string_setting(f"custom_icon_{icon_type}", "")
    return val if val else None

def delete_icon_setting(icon_type):
    """Удаляет запись о кастомной иконке."""
    key = open_reg_key(write=True)
    if key:
        try:
            winreg.DeleteValue(key, f"custom_icon_{icon_type}")
        except (FileNotFoundError, WindowsError):
            pass
        finally:
            winreg.CloseKey(key)

class AppConfig:
    def __init__(self):
        self.load()

    def load(self):
        self.show_notification = load_setting("show_notification", True)
        self.show_confirmation = load_setting("show_confirmation", False)
        self.play_sound = load_setting("play_sound", True)
        self.autostart = is_autostart_enabled()

        self.single_click_action = load_string_setting("single_click_action", "empty_bin")
        self.double_click_action = load_string_setting("double_click_action", "open_settings")
        self.middle_click_action = load_string_setting("middle_click_action", "open_bin")

        self.icon_theme = load_string_setting("icon_theme", "windows") # "windows" or "custom"
        self.custom_icon_empty = load_icon_path("empty")
        self.custom_icon_full = load_icon_path("full")
        self.theme_mode = load_string_setting("theme_mode", "dark") # "dark" or "light"

    def save(self):
        save_setting("show_notification", self.show_notification)
        save_setting("show_confirmation", self.show_confirmation)
        save_setting("play_sound", self.play_sound)
        set_autostart(self.autostart)

        save_string_setting("single_click_action", self.single_click_action)
        save_string_setting("double_click_action", self.double_click_action)
        save_string_setting("middle_click_action", self.middle_click_action)

        save_string_setting("icon_theme", self.icon_theme)
        save_string_setting("theme_mode", self.theme_mode)

        if self.custom_icon_empty:
            save_icon_path("empty", self.custom_icon_empty)
        else:
            delete_icon_setting("empty")

        if self.custom_icon_full:
            save_icon_path("full", self.custom_icon_full)
        else:
            delete_icon_setting("full")
