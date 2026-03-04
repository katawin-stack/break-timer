import json
import os

DEFAULTS = {
    "work_minutes": 45,
    "break_minutes": 10,
    "snooze_minutes": 5,
    "max_snooze_count": 3,
    "mode": "warning",
    "sound_enabled": True,
}

class Settings:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.expanduser("~"), ".break_timer.json")
        self._path = config_path
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data.update(loaded)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def work_minutes(self): return self._data["work_minutes"]
    @work_minutes.setter
    def work_minutes(self, v): self._data["work_minutes"] = int(v)

    @property
    def break_minutes(self): return self._data["break_minutes"]
    @break_minutes.setter
    def break_minutes(self, v): self._data["break_minutes"] = int(v)

    @property
    def snooze_minutes(self): return self._data["snooze_minutes"]
    @snooze_minutes.setter
    def snooze_minutes(self, v): self._data["snooze_minutes"] = int(v)

    @property
    def max_snooze_count(self): return self._data["max_snooze_count"]
    @max_snooze_count.setter
    def max_snooze_count(self, v): self._data["max_snooze_count"] = int(v)

    @property
    def mode(self): return self._data["mode"]
    @mode.setter
    def mode(self, v): self._data["mode"] = v

    @property
    def sound_enabled(self): return self._data["sound_enabled"]
    @sound_enabled.setter
    def sound_enabled(self, v): self._data["sound_enabled"] = bool(v)
