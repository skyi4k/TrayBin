import os
import subprocess
import sys
import shutil

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "main.py")
    icon_path = os.path.join(base_dir, "icons", "bin-empty.ico")
    icons_dir = os.path.join(base_dir, "icons")

    # Clean previous builds
    for folder in ["build", "dist"]:
        p = os.path.join(base_dir, folder)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)

    spec_file = os.path.join(base_dir, "TrayBin.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        "--name", "TrayBin",
        f"--icon={icon_path}",
        f"--add-data={icons_dir};icons",
        f"--paths={os.path.join(base_dir, 'src')}",
        main_script
    ]

    print("Запуск сборки PyInstaller...")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=base_dir)

    if res.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "TrayBin.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n[УСПЕХ] Исполняемый файл успешно собран:")
            print(f"Путь: {exe_path}")
            print(f"Размер: {size_mb:.2f} МБ")
        else:
            print("\n[ОШИБКА] Файл .exe не найден в папке dist.")
    else:
        print(f"\n[ОШИБКА] Сборка завершилась с ошибкой (код {res.returncode}).")

if __name__ == "__main__":
    build()
