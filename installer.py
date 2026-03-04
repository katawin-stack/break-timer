import os
import subprocess
import sys
import winreg

import customtkinter as ctk
from PIL import Image, ImageDraw

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(APP_DIR, "main.py")
PYTHONW = sys.executable.replace("python.exe", "pythonw.exe")
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable


def _create_ico():
    ico_path = os.path.join(APP_DIR, "break_timer.ico")
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#4a9eff")
    img.save(ico_path, format="ICO", sizes=[(64, 64), (32, 32), (16, 16)])
    return ico_path


class Installer:
    def __init__(self):
        self._root = ctk.CTk()
        self._root.title("Break Timer – Telepítő")
        self._root.resizable(False, False)
        self._root.attributes("-topmost", True)
        self._build_ui()
        self._center()

    def _build_ui(self):
        frame = ctk.CTkFrame(self._root, corner_radius=12)
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            frame, text="☕  Break Timer",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(20, 2))
        ctk.CTkLabel(
            frame, text="Szünet-emlékeztető Windows-ra",
            font=ctk.CTkFont(size=13), text_color="gray",
        ).pack(pady=(0, 20))

        # Tray icon explanation
        info = ctk.CTkFrame(frame, fg_color="#0d1b2a", corner_radius=8)
        info.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            info, text="🔵  Hol találod a programot?",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(padx=16, pady=(12, 4), anchor="w")
        ctk.CTkLabel(
            info,
            text=(
                "A program a háttérben fut, és a tálca jobb sarkában\n"
                "egy kék kör ikon jelzi a jelenlétét.\n\n"
                "  ➜  Kattints az ikonra JOBB egérgombbal a menü megnyitásához.\n\n"
                "Ha az ikon nem látszik, kattints a tálcán a  ᨈ  nyílra\n"
                "(Rejtett ikonok megjelenítése)."
            ),
            font=ctk.CTkFont(size=12), justify="left", anchor="w",
            text_color="#cccccc",
        ).pack(padx=16, pady=(0, 14), anchor="w")

        # What the installer does
        steps = ctk.CTkFrame(frame, fg_color="#0d2a0d", corner_radius=8)
        steps.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(
            steps, text="✅  A telepítő elvégzi:",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(padx=16, pady=(12, 4), anchor="w")
        ctk.CTkLabel(
            steps,
            text=(
                "  •  Asztali parancsikon létrehozása (Break Timer)\n"
                "  •  Automatikus indítás Windows bejelentkezéskor\n"
                "  •  Beállítások ablak megnyitása az első konfiguráció elvégzéséhez"
            ),
            font=ctk.CTkFont(size=12), justify="left", anchor="w",
            text_color="#cccccc",
        ).pack(padx=16, pady=(0, 14), anchor="w")

        self._status = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=12), text_color="#4a9eff",
        )
        self._status.pack(pady=(0, 6))

        self._btn = ctk.CTkButton(
            frame, text="Telepítés", command=self._install,
            width=220, height=46, font=ctk.CTkFont(size=15, weight="bold"),
        )
        self._btn.pack(pady=(0, 24))

    def _set_status(self, text):
        self._status.configure(text=text)
        self._root.update()

    def _install(self):
        self._btn.configure(state="disabled", text="Telepítés folyamatban…")

        self._set_status("Ikon létrehozása…")
        ico_path = _create_ico()

        self._set_status("Asztali parancsikon létrehozása…")
        self._create_shortcut(ico_path)

        self._set_status("Automatikus indítás beállítása…")
        self._set_autostart()

        self._set_status("✅  Telepítés kész!")
        self._btn.configure(text="Kész  ✓", fg_color="#2d6a2d", state="normal",
                            command=self._finish)
        self._root.after(1200, self._finish)

    def _create_shortcut(self, ico_path):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        lnk = os.path.join(desktop, "Break Timer.lnk").replace("\\", "\\\\")
        target = PYTHONW.replace("\\", "\\\\")
        args = f'\\"{MAIN_PY.replace(chr(92), chr(92)*2)}\\"'
        work = APP_DIR.replace("\\", "\\\\")
        icon = ico_path.replace("\\", "\\\\")

        ps = (
            f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");'
            f'$s.TargetPath="{target}";'
            f'$s.Arguments=\'"{MAIN_PY.replace(chr(92), "/")}\"\';'
            f'$s.WorkingDirectory="{work}";'
            f'$s.IconLocation="{icon}";'
            f'$s.Description="Break Timer - Szünet emlékeztető";'
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-Command", ps], capture_output=True)

    def _set_autostart(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "BreakTimer", 0, winreg.REG_SZ,
                          f'"{PYTHONW}" "{MAIN_PY}"')
        winreg.CloseKey(key)

    def _finish(self):
        self._root.destroy()
        subprocess.Popen(
            [PYTHONW, MAIN_PY, "--settings"],
            creationflags=0x00000008,  # DETACHED_PROCESS
        )

    def _center(self):
        self._root.update_idletasks()
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def run(self):
        self._root.mainloop()


if __name__ == "__main__":
    app = Installer()
    app.run()
