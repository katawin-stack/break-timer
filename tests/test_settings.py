import json
import os
import pytest
from settings import Settings

@pytest.fixture
def tmp_settings(tmp_path):
    path = tmp_path / "settings.json"
    return Settings(config_path=str(path))

def test_defaults(tmp_settings):
    s = tmp_settings
    assert s.work_minutes == 45
    assert s.break_minutes == 10
    assert s.snooze_minutes == 5
    assert s.max_snooze_count == 3
    assert s.mode == "warning"
    assert s.sound_enabled is True

def test_save_and_load(tmp_settings, tmp_path):
    s = tmp_settings
    s.work_minutes = 25
    s.mode = "forced"
    s.save()

    s2 = Settings(config_path=str(tmp_path / "settings.json"))
    assert s2.work_minutes == 25
    assert s2.mode == "forced"

def test_missing_file_uses_defaults(tmp_path):
    path = tmp_path / "nonexistent.json"
    s = Settings(config_path=str(path))
    assert s.work_minutes == 45
