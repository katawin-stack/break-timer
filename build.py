"""
Build script – létrehozza a BreakTimerSetup.exe fájlt.

Futtatás: python build.py
Eredmény: dist/BreakTimerSetup.exe
"""
import os
import subprocess
import sys


def create_icon():
    from PIL import Image, ImageDraw
    path = os.path.join(os.path.dirname(__file__), "break_timer.ico")
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 248, 248], fill="#4a9eff")
    img.save(path, format="ICO", sizes=[(256, 256), (64, 64), (32, 32), (16, 16)])
    print(f"  Ikon létrehozva: {path}")
    return path


def main():
    print("=== Break Timer build ===\n")

    print("1. PyInstaller telepítése / ellenőrzése…")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"],
        check=True,
    )

    print("2. Ikon létrehozása…")
    ico = create_icon()

    print("3. Exe build indítása (ez 1-2 percet vehet igénybe)…")
    entry = os.path.join(os.path.dirname(__file__), "break_timer_setup.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "BreakTimerSetup",
        "--icon", ico,
        "--collect-all", "customtkinter",
        "--collect-all", "pystray",
        "--hidden-import", "pystray._win32",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "winsound",
        "--hidden-import", "winreg",
        entry,
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        dist = os.path.join(os.path.dirname(__file__), "dist", "BreakTimerSetup.exe")
        size_mb = os.path.getsize(dist) / 1024 / 1024
        print(f"\n✅  Kész!\n   Fájl: {dist}\n   Méret: {size_mb:.1f} MB")
        print("\nEzt a fájlt töltsd fel a weboldaladra.")
    else:
        print("\n❌  Build sikertelen.")
        sys.exit(1)


if __name__ == "__main__":
    main()
