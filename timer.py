import threading
import time

class TimerThread(threading.Thread):
    def __init__(self, interval_seconds, on_break_due):
        super().__init__(daemon=True)
        self._interval = interval_seconds
        self._callback = on_break_due
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._deadline = time.monotonic() + self._interval  # azonnal érvényes

    def run(self):
        while not self._stop_event.is_set():
            now = time.monotonic()
            with self._lock:
                deadline = self._deadline
            if now >= deadline:
                self._callback()
                with self._lock:
                    self._deadline = time.monotonic() + self._interval
            self._stop_event.wait(timeout=0.05)

    def stop(self):
        self._stop_event.set()

    def reset(self):
        with self._lock:
            self._deadline = time.monotonic() + self._interval

    def snooze(self, seconds=None):
        """Delay next callback by given seconds (or interval)."""
        delay = seconds if seconds is not None else self._interval
        with self._lock:
            self._deadline = time.monotonic() + delay

    def remaining_seconds(self):
        with self._lock:
            return max(0.0, self._deadline - time.monotonic())

    @classmethod
    def from_settings(cls, settings, on_break_due):
        return cls(
            interval_seconds=settings.work_minutes * 60,
            on_break_due=on_break_due,
        )
