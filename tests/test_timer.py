import time
import pytest
from timer import TimerThread

def test_callback_fires_after_elapsed():
    fired = []
    t = TimerThread(interval_seconds=0.1, on_break_due=lambda: fired.append(1))
    t.start()
    time.sleep(0.3)
    t.stop()
    assert len(fired) >= 1

def test_reset_delays_callback():
    fired = []
    t = TimerThread(interval_seconds=0.2, on_break_due=lambda: fired.append(1))
    t.start()
    time.sleep(0.1)
    t.reset()
    time.sleep(0.15)
    t.stop()
    assert len(fired) == 0

def test_snooze_delays_callback():
    fired = []
    t = TimerThread(interval_seconds=0.2, on_break_due=lambda: fired.append(1))
    t.start()
    time.sleep(0.25)  # callback fires
    assert len(fired) == 1
    t.snooze(seconds=0.2)
    fired.clear()
    time.sleep(0.1)   # snooze still active
    assert len(fired) == 0
    time.sleep(0.15)  # snooze elapsed
    assert len(fired) >= 1
    t.stop()

def test_remaining_seconds():
    t = TimerThread(interval_seconds=10, on_break_due=lambda: None)
    t.start()
    time.sleep(0.1)
    rem = t.remaining_seconds()
    assert 9 < rem <= 10
    t.stop()
