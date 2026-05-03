"""Tests for pi_logger.py — runs on Mac without hardware."""

import csv
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# Stub out hardware modules so imports don't fail on Mac
sys.modules["board"] = MagicMock()
sys.modules["adafruit_ahtx0"] = MagicMock()

import pi_logger  # noqa: E402 — must come after stubs


def make_sensor(temp=22.5, humidity=55.0):
    sensor = MagicMock()
    sensor.temperature = temp
    sensor.relative_humidity = humidity
    return sensor


def test_first_run_creates_file_with_header(tmp_path, monkeypatch):
    log = tmp_path / "temperature_log.csv"
    monkeypatch.setattr(pi_logger, "LOG_FILE", str(log))

    pi_logger.append_log(22.5, 55.0)

    rows = log.read_text().splitlines()
    assert rows[0] == "timestamp,temperature_c,humidity_pct"
    assert len(rows) == 2


def test_second_run_appends_without_duplicate_header(tmp_path, monkeypatch):
    log = tmp_path / "temperature_log.csv"
    monkeypatch.setattr(pi_logger, "LOG_FILE", str(log))

    pi_logger.append_log(22.5, 55.0)
    pi_logger.append_log(23.0, 60.0)

    rows = log.read_text().splitlines()
    assert rows[0] == "timestamp,temperature_c,humidity_pct"
    assert len(rows) == 3  # header + 2 data rows


def test_log_values_are_correct(tmp_path, monkeypatch):
    log = tmp_path / "temperature_log.csv"
    monkeypatch.setattr(pi_logger, "LOG_FILE", str(log))

    pi_logger.append_log(21.123, 48.999)

    with open(log) as f:
        reader = csv.DictReader(f)
        row = next(reader)

    assert row["temperature_c"] == "21.12"
    assert row["humidity_pct"] == "49.00"


def test_main_reads_sensor_and_logs(tmp_path, monkeypatch):
    log = tmp_path / "temperature_log.csv"
    monkeypatch.setattr(pi_logger, "LOG_FILE", str(log))

    mock_sensor = make_sensor(temp=25.0, humidity=70.0)
    with patch("pi_logger.read_sensor", return_value=(25.0, 70.0)):
        pi_logger.main()

    with open(log) as f:
        reader = csv.DictReader(f)
        row = next(reader)

    assert row["temperature_c"] == "25.00"
    assert row["humidity_pct"] == "70.00"


def test_main_exits_on_sensor_error(tmp_path, monkeypatch, capsys):
    log = tmp_path / "temperature_log.csv"
    monkeypatch.setattr(pi_logger, "LOG_FILE", str(log))

    with patch("pi_logger.read_sensor", side_effect=OSError("I2C error")):
        try:
            pi_logger.main()
        except SystemExit as e:
            assert e.code == 1

    captured = capsys.readouterr()
    assert "I2C error" in captured.err
