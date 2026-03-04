import customtkinter as ctk
from settings import Settings

class SettingsWindow:
    def __init__(self, settings: Settings, on_save=None):
        self._settings = settings
        self._on_save = on_save
        self._win = ctk.CTkToplevel()
        self._win.title("Beállítások")
        self._win.resizable(False, False)
        self._win.attributes("-topmost", True)
        self._win.grab_set()
        self._build_ui()
        self._center()

    def _build_ui(self):
        pad = {"padx": 20, "pady": 6}
        frame = ctk.CTkFrame(self._win)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        def row(label, var, row_idx):
            ctk.CTkLabel(frame, text=label, anchor="w").grid(
                row=row_idx, column=0, sticky="w", **pad
            )
            entry = ctk.CTkEntry(frame, textvariable=var, width=80)
            entry.grid(row=row_idx, column=1, sticky="e", **pad)

        self._work_var = ctk.StringVar(value=str(self._settings.work_minutes))
        self._break_var = ctk.StringVar(value=str(self._settings.break_minutes))
        self._snooze_var = ctk.StringVar(value=str(self._settings.snooze_minutes))
        self._max_snooze_var = ctk.StringVar(value=str(self._settings.max_snooze_count))

        row("Munkaidő (perc):", self._work_var, 0)
        row("Szünet hossza (perc):", self._break_var, 1)
        row("Elhalasztás (perc):", self._snooze_var, 2)
        row("Max elhalasztás (db):", self._max_snooze_var, 3)

        ctk.CTkLabel(frame, text="Mód:", anchor="w").grid(
            row=4, column=0, sticky="w", **pad
        )
        self._mode_var = ctk.StringVar(value=self._settings.mode)
        mode_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mode_frame.grid(row=4, column=1, sticky="e", **pad)
        ctk.CTkRadioButton(mode_frame, text="Figyelmeztető", variable=self._mode_var, value="warning").pack(side="left")
        ctk.CTkRadioButton(mode_frame, text="Kényszerű", variable=self._mode_var, value="forced").pack(side="left", padx=(10, 0))

        self._sound_var = ctk.BooleanVar(value=self._settings.sound_enabled)
        ctk.CTkLabel(frame, text="Hangjelzés:", anchor="w").grid(
            row=5, column=0, sticky="w", **pad
        )
        ctk.CTkCheckBox(frame, text="", variable=self._sound_var).grid(
            row=5, column=1, sticky="e", **pad
        )

        ctk.CTkButton(
            frame, text="Mentés", command=self._save, width=120, height=36
        ).grid(row=6, column=0, columnspan=2, pady=(16, 6))

    def _save(self):
        try:
            self._settings.work_minutes = int(self._work_var.get())
            self._settings.break_minutes = int(self._break_var.get())
            self._settings.snooze_minutes = int(self._snooze_var.get())
            self._settings.max_snooze_count = int(self._max_snooze_var.get())
        except ValueError:
            return
        self._settings.mode = self._mode_var.get()
        self._settings.sound_enabled = self._sound_var.get()
        self._settings.save()
        self._win.destroy()
        if self._on_save:
            self._on_save()

    def _center(self):
        self._win.update_idletasks()
        w = self._win.winfo_width()
        h = self._win.winfo_height()
        sw = self._win.winfo_screenwidth()
        sh = self._win.winfo_screenheight()
        self._win.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")
