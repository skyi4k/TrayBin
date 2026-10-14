# 🗑️ TrayBin

<div align="center">

**Легковесная и быстрая утилита для мониторинга и очистки Корзины Windows прямо из системного трея.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D4?logo=windows)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![GUI](https://img.shields.io/badge/GUI-PyQt6%20Fluent-success)

[Русский](#русский) • [English](#english)

</div>

---

<a name="русский"></a>
## 🇷🇺 Описание

**TrayBin** — это современная программа для Windows 10 и 11, которая добавляет динамическую иконку Корзины в область уведомлений (системный трей). Она позволяет моментально освобождать место на всех дисках одним кликом, просматривать количество удаленных файлов и гибко настраивать управление мышью.

### ⚡ Ключевые особенности

* **Системные иконки Windows 11**: Официальные нативные иконки пустой и полной корзины из системных библиотек Windows (`imageres.dll`) высокого разрешения.
* **Кастомные иконки**: Возможность выбрать собственные файлы `.ico` или `.png` с мгновенным применением без перезапуска приложения.
* **Информативный тултип**: При наведении мыши отображается статус корзины, точное количество объектов и общий размер (например, `TrayBin - Корзина: 14 объектов (1.25 ГБ)`).
* **Очистка всех накопителей**: Моментальное удаление файлов на всех логических дисках (C:, D:, E: и т.д.) через Win32 API `SHEmptyRecycleBinW`.
* **Настройка действий мыши**:
  * Одиночный левый клик (ЛКМ)
  * Двойной левый клик (2x ЛКМ)
  * Клик колёсиком мыши (СКМ / Middle Click)
  * Контекстное меню по правому клику (ПКМ)
* **Звук и уведомления**: Опция включения/выключения системного звука корзины (`SHERB_NOSOUND`) и всплывающие уведомления Windows об освобожденном месте.
* **Защита от дубликатов**: Использование именованного Windows Mutex (`TrayBin_Application_Mutex`) предотвращает случайный запуск нескольких копий программы.
* **Современный интерфейс настроек**: Дизайн в стиле Windows 11 Fluent с поддержкой тёмной и светлой темы.
* **Автозагрузка**: Удобное включение запуска вместе со стартом Windows через реестр (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).

---

## 🛠️ Установка и запуск

### Готовый файл (.exe)
1. Скачайте `TrayBin.exe` из папки `dist/` или вкладки [Releases](https://github.com/skyi4k/TrayBin/releases).
2. Запустите `TrayBin.exe`. Иконка сразу появится в трее рядом с часами.

### Запуск из исходного кода
```bash
# Клонируйте репозиторий
git clone https://github.com/skyi4k/TrayBin.git
cd TrayBin

# Установите зависимости
pip install -r requirements.txt

# Запустите приложение
python main.py
```

### Сборка автономного .exe
```bash
python build.py
```
Собранный исполняемый файл появится в папке `dist/TrayBin.exe`.

---

<a name="english"></a>
## 🇬🇧 English Description

**TrayBin** is a lightweight Windows utility that places a live Recycle Bin icon in your system tray (notification area).

### Features
* **Official Windows 11 Icons**: Native high-resolution icons extracted directly from Windows system libraries.
* **Custom Icons Support**: Load your own `.ico` or `.png` icons with instant live reload.
* **Rich Tooltip**: Shows the exact item count and total size of deleted files on hover.
* **All-Drive Emptying**: Empties the Recycle Bin across all drives instantly using Windows Shell API.
* **Mouse Interactions**: Customizable single click, double click, and middle mouse click actions.
* **Sound & Notifications**: Toggle Windows trash sound and notification toasts.
* **Single Instance Guard**: Prevents duplicate tray instances via Windows Named Mutex.
* **Windows 11 Fluent UI**: Clean settings window supporting both dark and light modes.

---

## 📄 Лицензия / License

Проект распространяется под лицензией [MIT](LICENSE).
Автор: **skyi4k**
