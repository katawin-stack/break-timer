"""
Break Timer – egyetlen futtatható fájl.

Ha a letöltött helyen fut: telepítő módban indul.
Ha a telepítési mappából fut: tálca-appként indul.
"""
import os
import shutil
import subprocess
import sys
import winreg

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

INSTALL_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "BreakTimer"
)
INSTALL_EXE = os.path.join(INSTALL_DIR, "BreakTimer.exe")
APP_NAME = "BreakTimer"


def _running_from_install_dir():
    if not getattr(sys, "frozen", False):
        return False
    return os.path.normcase(sys.executable) == os.path.normcase(INSTALL_EXE)


# ──────────────────────────────────────────────────────────────────────────────
# Tálca-app mód
# ──────────────────────────────────────────────────────────────────────────────

def run_app():
    from main import TrayApp
    app = TrayApp()
    if "--settings" in sys.argv:
        app._root.after(800, app._do_open_settings)
    app.run()


# ──────────────────────────────────────────────────────────────────────────────
# Telepítő mód
# ──────────────────────────────────────────────────────────────────────────────

class InstallerWindow:
    def __init__(self):
        self._root = ctk.CTk()
        self._root.title("Break Timer – Telepítő")
        self._root.resizable(False, False)
        self._root.attributes("-topmost", True)
        self._already_installed = os.path.isfile(INSTALL_EXE)
        self._build_ui()
        self._center()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = ctk.CTkFrame(self._root, corner_radius=12)
        outer.pack(padx=30, pady=30, fill="both", expand=True)

        # Fejléc
        ctk.CTkLabel(
            outer, text="☕  Break Timer",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(20, 2))
        ctk.CTkLabel(
            outer, text="Szünet-emlékeztető Windows-ra",
            font=ctk.CTkFont(size=13), text_color="gray",
        ).pack(pady=(0, 18))

        # Tálca ikon magyarázat
        self._info_box(
            outer,
            title="🔵  Hol találod a programot telepítés után?",
            body=(
                "A program a háttérben fut — a tálca jobb sarkában\n"
                "egy kék kör ikon jelzi a jelenlétét.\n\n"
                "  ➜  Kattints az ikonra JOBB egérgombbal a menü megnyitásához:\n"
                "       Szünet most  ·  Beállítások  ·  Kilépés\n\n"
                "Ha az ikon nem látszik, kattints a tálcán a  ᨈ  nyílra\n"
                "( Rejtett ikonok megjelenítése )."
            ),
            bg="#0d1b2a",
        )

        # Mit csinál a telepítő
        self._info_box(
            outer,
            title="✅  A telepítő elvégzi:",
            body=(
                "  •  Telepítési hely: %LOCALAPPDATA%\\BreakTimer\\\n"
                "  •  Asztali parancsikon létrehozása ( Break Timer )\n"
                "  •  Automatikus indítás Windows bejelentkezéskor\n"
                "  •  Beállítások ablak megnyitása az első konfigurációhoz"
            ),
            bg="#0d2a0d",
        )

        # Már telepített esetén figyelmeztetés
        if self._already_installed:
            self._info_box(
                outer,
                title="⚠️  Már telepítve van",
                body="A Telepítés gomb felülírja a meglévő telepítést.",
                bg="#2a1a00",
            )

        self._status_lbl = ctk.CTkLabel(
            outer, text="", font=ctk.CTkFont(size=12), text_color="#4a9eff",
        )
        self._status_lbl.pack(pady=(4, 4))

        btn_text = "Frissítés / Újratelepítés" if self._already_installed else "Telepítés"
        self._btn = ctk.CTkButton(
            outer, text=btn_text, command=self._on_install,
            width=240, height=46, font=ctk.CTkFont(size=15, weight="bold"),
        )
        self._btn.pack(pady=(4, 24))

    @staticmethod
    def _info_box(parent, title, body, bg):
        box = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8)
        box.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(
            box, text=title,
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).pack(padx=16, pady=(12, 4), anchor="w")
        ctk.CTkLabel(
            box, text=body,
            font=ctk.CTkFont(size=12), justify="left",
            text_color="#cccccc", anchor="w",
        ).pack(padx=16, pady=(0, 14), anchor="w")

    def _set_status(self, text):
        self._status_lbl.configure(text=text)
        self._root.update()

    # ── Telepítési logika ──────────────────────────────────────────────────────

    def _on_install(self):
        self._btn.configure(state="disabled", text="Telepítés folyamatban…")
        try:
            self._set_status("Könyvtár létrehozása…")
            os.makedirs(INSTALL_DIR, exist_ok=True)

            self._set_status("Fájlok másolása…")
            self._safe_copy()

            self._set_status("Asztali parancsikon létrehozása…")
            self._create_shortcut()

            self._set_status("Automatikus indítás beállítása…")
            self._set_autostart()

            self._set_status("✅  Telepítés sikeres!")
            self._btn.configure(
                text="Befejezés  ✓", fg_color="#2d6a2d",
                state="normal", command=self._finish,
            )
            self._root.after(1500, self._finish)

        except Exception as exc:
            self._set_status(f"❌  Hiba: {exc}")
            self._btn.configure(state="normal", text="Újrapróbálás")

    def _safe_copy(self):
        """Copy exe; if destination is locked (app running), stop it first."""
        if os.path.isfile(INSTALL_EXE):
            try:
                os.replace(INSTALL_EXE, INSTALL_EXE + ".old")
                os.remove(INSTALL_EXE + ".old")
            except PermissionError:
                # Try to terminate running instance
                subprocess.run(
                    ["taskkill", "/F", "/IM", "BreakTimer.exe"],
                    capture_output=True,
                )
        shutil.copy2(sys.executable, INSTALL_EXE)

    def _create_shortcut(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        lnk = os.path.join(desktop, "Break Timer.lnk")
        ps = (
            f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");'
            f'$s.TargetPath="{INSTALL_EXE}";'
            f'$s.WorkingDirectory="{INSTALL_DIR}";'
            f'$s.Description="Break Timer - szünet emlékeztető";'
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-Command", ps], capture_output=True)

    def _set_autostart(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{INSTALL_EXE}"')
        winreg.CloseKey(key)

    def _finish(self):
        self._root.destroy()
        subprocess.Popen(
            [INSTALL_EXE, "--settings"],
            creationflags=subprocess.DETACHED_PROCESS,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _center(self):
        self._root.update_idletasks()
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def run(self):
        self._root.mainloop()


# ──────────────────────────────────────────────────────────────────────────────
# Belépési pont
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__" or getattr(sys, "frozen", False):
    if _running_from_install_dir() or "--app" in sys.argv:
        run_app()
    else:
        InstallerWindow().run()
