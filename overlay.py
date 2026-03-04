import ctypes
import customtkinter as ctk

def _block_input(block: bool):
    try:
        ctypes.windll.user32.BlockInput(block)
    except Exception:
        pass

class BreakOverlay:
    def __init__(self, break_seconds, snooze_seconds, max_snooze, on_done=None, on_snooze=None):
        self._break_seconds = break_seconds
        self._snooze_seconds = snooze_seconds
        self._max_snooze = max_snooze
        self._snooze_used = 0
        self._on_done = on_done
        self._on_snooze = on_snooze
        self._remaining = break_seconds

    def show(self):
        self._root = ctk.CTk()
        self._root.title("")
        self._root.attributes("-fullscreen", True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.88)
        self._root.configure(fg_color="#1a1a2e")
        self._root.protocol("WM_DELETE_WINDOW", lambda: None)  # nem zárható

        self._build_ui()
        _block_input(True)
        self._tick()
        self._root.mainloop()

    def _build_ui(self):
        frame = ctk.CTkFrame(self._root, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            frame,
            text="🛑  Kényszerű szünet",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white",
        ).pack(pady=(0, 10))

        self._time_label = ctk.CTkLabel(
            frame,
            text=self._format_time(self._remaining),
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color="#e94560",
        )
        self._time_label.pack(pady=(0, 20))

        ctk.CTkLabel(
            frame,
            text="Állj fel, lazíts, pihentesd a szemed.",
            font=ctk.CTkFont(size=18),
            text_color="#aaaaaa",
        ).pack(pady=(0, 30))

        self._snooze_btn = ctk.CTkButton(
            frame,
            text=f"Elhalaszt {self._snooze_seconds // 60} percre",
            command=self._do_snooze,
            width=240,
            height=44,
            fg_color="#533483",
        )
        if self._snooze_used < self._max_snooze:
            self._snooze_btn.pack()

    def _format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _tick(self):
        if self._remaining > 0:
            self._remaining -= 1
            self._time_label.configure(text=self._format_time(self._remaining))
            self._root.after(1000, self._tick)
        else:
            self._finish()

    def _do_snooze(self):
        self._snooze_used += 1
        _block_input(False)
        self._root.destroy()
        if self._on_snooze:
            self._on_snooze(self._snooze_seconds)

    def _finish(self):
        _block_input(False)
        self._root.destroy()
        if self._on_done:
            self._on_done()
