import os
import sys
import re
import urllib.request
import json
import subprocess
import tempfile
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

from config import APP_VERSION, GITHUB_REPO, resource_path
from styles import get_stylesheet

def parse_version(v_str):
    nums = re.findall(r'\d+', str(v_str))
    return tuple(map(int, nums)) if nums else (0,)

def is_newer_version(remote_v, local_v=APP_VERSION):
    return parse_version(remote_v) > parse_version(local_v)

def fetch_latest_release():
    """
    Проверяет наличие свежего релиза на GitHub.
    Использует API, а при превышении rate limit переключается на прямой HTML-редирект.
    Возвращает dict с полями: tag, name, body, download_url
    """
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "TrayBin-Updater",
        "Accept": "application/vnd.github.v3+json"
    })

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            name = data.get("name", tag)
            body = data.get("body", "")
            download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/TrayBin.exe"
            for asset in data.get("assets", []):
                if asset.get("name") == "TrayBin.exe":
                    download_url = asset.get("browser_download_url")
                    break
            return {
                "tag": tag,
                "name": name,
                "body": body,
                "download_url": download_url
            }
    except Exception:
        # Fallback via redirect to /releases/latest
        fallback_url = f"https://github.com/{GITHUB_REPO}/releases/latest"
        fb_req = urllib.request.Request(fallback_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(fb_req, timeout=5) as resp:
            final_url = resp.geturl()
            tag = final_url.split("/")[-1]
            download_url = f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/TrayBin.exe"
            return {
                "tag": tag,
                "name": f"TrayBin {tag}",
                "body": "Ознакомиться со списком изменений можно на странице релиза GitHub.",
                "download_url": download_url
            }

class CheckUpdateWorker(QThread):
    update_found = pyqtSignal(dict)
    already_latest = pyqtSignal(str)
    check_failed = pyqtSignal(str)

    def run(self):
        try:
            rel = fetch_latest_release()
            remote_tag = rel.get("tag", "")
            if is_newer_version(remote_tag, APP_VERSION):
                self.update_found.emit(rel)
            else:
                self.already_latest.emit(APP_VERSION)
        except Exception as e:
            self.check_failed.emit(str(e))

class DownloadWorker(QThread):
    progress = pyqtSignal(int, int) # downloaded, total
    finished = pyqtSignal(str)     # target temp path
    error = pyqtSignal(str)

    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url

    def run(self):
        try:
            temp_dir = tempfile.gettempdir()
            out_file = os.path.join(temp_dir, "TrayBin_new.exe")

            req = urllib.request.Request(self.download_url, headers={"User-Agent": "TrayBin-Updater"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(out_file, "wb") as f:
                total_size = int(resp.headers.get("content-length", 0))
                downloaded = 0
                chunk_size = 64 * 1024

                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    self.progress.emit(downloaded, total_size)

            self.finished.emit(out_file)
        except Exception as e:
            self.error.emit(str(e))

class UpdateDialog(QDialog):
    def __init__(self, release_info, config, parent=None):
        super().__init__(parent)
        self.release_info = release_info
        self.config = config

        self.setWindowTitle("Обновление TrayBin")
        self.setFixedSize(440, 320)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowTitleHint)

        ico_path = resource_path("icons/bin-empty.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        self.setStyleSheet(get_stylesheet(self.config.theme_mode))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        tag = self.release_info.get("tag", "")
        name = self.release_info.get("name", f"Версия {tag}")

        title_lbl = QLabel(f"🎉 Доступна новая версия: {name}")
        title_lbl.setObjectName("headerLabel")
        layout.addWidget(title_lbl)

        ver_sub = QLabel(f"Текущая версия: v{APP_VERSION} ➔ Новая версия: {tag}")
        ver_sub.setStyleSheet("color: #60CDFF; font-weight: bold;")
        layout.addWidget(ver_sub)

        notes_lbl = QLabel("Что нового:")
        layout.addWidget(notes_lbl)

        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setText(self.release_info.get("body", "Нет описания изменений."))
        self.notes_text.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border: 1px solid #444; border-radius: 6px; padding: 6px;")
        layout.addWidget(self.notes_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                background-color: #2D2D2D;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("subHeaderLabel")
        layout.addWidget(self.status_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_later = QPushButton("Позже")
        self.btn_later.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_later)

        self.btn_update = QPushButton("Обновить сейчас")
        self.btn_update.setObjectName("primaryBtn")
        self.btn_update.clicked.connect(self.start_download)
        btn_row.addWidget(self.btn_update)

        layout.addLayout(btn_row)

    def start_download(self):
        # If running from source code
        if not getattr(sys, "frozen", False):
            res = QMessageBox.question(
                self,
                "Исходный код",
                "Вы используете запуск из исходного кода. Открыть страницу релиза на GitHub для скачивания обновления?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                import webbrowser
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            self.accept()
            return

        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_lbl.setText("Загрузка обновления...")

        url = self.release_info.get("download_url")
        self.worker = DownloadWorker(url)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_progress(self, downloaded, total):
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress_bar.setValue(percent)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self.status_lbl.setText(f"Загружено: {mb_down:.1f} МБ из {mb_total:.1f} МБ ({percent}%)")

    def on_download_error(self, err_msg):
        self.status_lbl.setText(f"Ошибка загрузки: {err_msg}")
        self.btn_update.setEnabled(True)
        self.btn_later.setEnabled(True)
        QMessageBox.warning(self, "Ошибка обновления", f"Не удалось скачать обновление:\n{err_msg}")

    def on_download_finished(self, temp_path):
        self.status_lbl.setText("Обновление скачано! Перезапуск программы...")
        apply_update(temp_path)

def apply_update(new_exe_path):
    """
    Создает скрипт обновления Windows batch, который дожидается завершения текущего процесса,
    заменяет исполняемый файл и перезапускает TrayBin.exe.
    """
    current_exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
    pid = os.getpid()

    bat_content = f"""@echo off
chcp 65001 >nul
timeout /t 1 /nobreak >nul
:wait_loop
tasklist /fi "PID eq {pid}" 2>nul | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
copy /y "{new_exe_path}" "{current_exe}" >nul
del /f /q "{new_exe_path}" >nul
start "" "{current_exe}"
del "%~f0" >nul
"""

    temp_dir = tempfile.gettempdir()
    bat_path = os.path.join(temp_dir, "traybin_updater.bat")

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        ["cmd.exe", "/c", bat_path],
        creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
        close_fds=True
    )

    from PyQt6.QtWidgets import QApplication
    QApplication.quit()
