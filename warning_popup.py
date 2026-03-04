import customtkinter as ctk

class WarningPopup:
    def __init__(self, on_close=None):
        self._on_close = on_close
        self._root = ctk.CTk()
        self._root.title("Szünet emlékeztető")
        self._root.resizable(False, False)
        self._root.attributes("-topmost", True)
        self._build_ui()
        self._center()

    def _build_ui(self):
        frame = ctk.CTkFrame(self._root, corner_radius=12)
        frame.pack(padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="☕  Ideje szünetet tartani!",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(padx=30, pady=(20, 10))

        ctk.CTkLabel(
            frame,
            text="Állj fel, nyújtózkodj, igyál vizet.",
            font=ctk.CTkFont(size=14),
        ).pack(padx=30, pady=(0, 20))

        ctk.CTkButton(
            frame,
            text="Rendben, bezárom",
            command=self._close,
            width=200,
            height=40,
        ).pack(pady=(0, 20))

    def _center(self):
        self._root.update_idletasks()
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self._root.geometry(f"+{x}+{y}")

    def _close(self):
        self._root.destroy()
        if self._on_close:
            self._on_close()

    def show(self):
        self._root.mainloop()
