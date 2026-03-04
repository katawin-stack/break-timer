import sys
import threading
import winsound
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw

from settings import Settings
from timer import TimerThread
from warning_popup import WarningPopup
from overlay import BreakOverlay
from settings_ui import SettingsWindow

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _make_tray_icon(color="#4a9eff"):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=color)
    return img


class TrayApp:
    def __init__(self):
        self._settings = Settings()
        self._root = ctk.CTk()
        self._root.withdraw()  # főablak rejtett
        self._snooze_count = 0
        self._timer = self._make_timer()
        self._tray = self._make_tray()

    def _make_timer(self):
        return TimerThread.from_settings(self._settings, self._on_break_due)

    def _remaining_label(self, _item=None):
        rem = int(self._timer.remaining_seconds())
        m, s = divmod(rem, 60)
        return f"Következő szünet: {m:02d}:{s:02d}"

    def _make_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem(self._remaining_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Szünet most", self._manual_break),
            pystray.MenuItem("Beállítások", self._open_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Kilépés", self._quit),
        )
        return pystray.Icon(
            "break_timer",
            _make_tray_icon(),
            "Break Timer",
            menu,
        )

    def _on_break_due(self):
        if self._settings.sound_enabled:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        self._root.after(0, self._show_break_ui)

    def _show_break_ui(self):
        self._snooze_count = 0
        if self._settings.mode == "forced":
            self._show_overlay()
        else:
            self._show_warning()

    def _show_warning(self):
        popup = WarningPopup(on_close=None)
        popup.show()

    def _show_overlay(self):
        overlay = BreakOverlay(
            break_seconds=self._settings.break_minutes * 60,
            snooze_seconds=self._settings.snooze_minutes * 60,
            max_snooze=self._settings.max_snooze_count,
            on_done=self._on_break_finished,
            on_snooze=self._on_snooze,
            snooze_used=self._snooze_count,
        )
        threading.Thread(target=overlay.show, daemon=True).start()

    def _on_snooze(self, delay_seconds):
        self._snooze_count += 1
        self._timer.snooze(seconds=delay_seconds)

    def _on_break_finished(self):
        self._timer.reset()

    def _manual_break(self):
        self._root.after(0, self._show_break_ui)

    def _open_settings(self):
        self._root.after(0, self._do_open_settings)

    def _do_open_settings(self):
        def on_save():
            self._timer.stop()
            self._timer = self._make_timer()
            self._timer.start()

        SettingsWindow(self._settings, on_save=on_save)

    def _quit(self):
        self._timer.stop()
        self._tray.stop()
        self._root.quit()
        sys.exit(0)

    def _tick_tray(self):
        self._tray.update_menu()
        self._root.after(10000, self._tick_tray)

    def run(self):
        self._timer.start()
        threading.Thread(target=self._tray.run, daemon=True).start()
        self._root.after(1000, self._tick_tray)
        self._root.mainloop()


if __name__ == "__main__":
    app = TrayApp()
    if "--settings" in sys.argv:
        app._root.after(800, app._do_open_settings)
    app.run()
