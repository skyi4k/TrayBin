import ctypes
import os
import subprocess

class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("i64Size", ctypes.c_int64),
        ("i64NumItems", ctypes.c_int64)
    ]

# Windows Shell Recycle Bin Flags
SHERB_NOCONFIRMATION = 0x00000001
SHERB_NOPROGRESSUI   = 0x00000002
SHERB_NOSOUND        = 0x00000004

def get_recycle_bin_info():
    """
    Получает информацию о состоянии корзины Windows:
    Возвращает кортеж (num_items: int, size_bytes: int).
    """
    rb_info = SHQUERYRBINFO()
    rb_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
    res = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rb_info))
    if res != 0:
        return 0, 0
    return int(rb_info.i64NumItems), int(rb_info.i64Size)

def is_recycle_bin_empty():
    items, _ = get_recycle_bin_info()
    return items == 0

def format_size(bytes_val):
    """Форматирует байты в читаемый вид (Б, КБ, МБ, ГБ)."""
    if bytes_val <= 0:
        return "0 Б"
    units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    size = float(bytes_val)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    if i == 0:
        return f"{int(size)} {units[i]}"
    return f"{size:.1f} {units[i]}"

def open_recycle_bin():
    """Открывает системную папку корзины в Проводнике."""
    try:
        os.startfile("shell:RecycleBinFolder")
    except Exception:
        subprocess.Popen(["explorer.exe", "shell:RecycleBinFolder"])

def empty_recycle_bin(confirm=False, play_sound=True, show_progress=False):
    """
    Очищает корзину на всех дисках.
    confirm: запрашивать ли системное подтверждение (True - показать диалог Windows)
    play_sound: проигрывать ли звук очистки
    show_progress: отображать ли окно прогресса удаления

    Возвращает:
      success (bool), error_code (int), items_cleared (int), bytes_cleared (int)
    """
    prev_items, prev_size = get_recycle_bin_info()
    if prev_items == 0:
        return True, 0, 0, 0

    flags = 0
    if not confirm:
        flags |= SHERB_NOCONFIRMATION
    if not play_sound:
        flags |= SHERB_NOSOUND
    if not show_progress:
        flags |= SHERB_NOPROGRESSUI

    res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)

    # 0 = S_OK
    # -2147418113 = 0x8000FFFF or cancelled
    # 0x800704C7 = -2147023673 (ERROR_CANCELLED)
    if res in (0, -2147418113, -2147023673):
        cur_items, cur_size = get_recycle_bin_info()
        items_cleared = max(0, prev_items - cur_items)
        bytes_cleared = max(0, prev_size - cur_size)
        return True, res, items_cleared, bytes_cleared
    else:
        return False, res, 0, 0
