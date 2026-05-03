#!/usr/bin/env python3
"""Log AHT20 temperature and humidity to CSV on Raspberry Pi Zero 2."""

import csv
import os
import sys
from datetime import datetime

import board
import adafruit_ahtx0

LOG_FILE = os.path.join(os.path.dirname(__file__), "temperature_log.csv")
FIELDNAMES = ["timestamp", "temperature_c", "humidity_pct"]


def read_sensor():
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)
    return sensor.temperature, sensor.relative_humidity


def append_log(temp: float, humidity: float):
    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "temperature_c": f"{temp:.2f}",
            "humidity_pct": f"{humidity:.2f}",
        })


def main():
    try:
        temp, humidity = read_sensor()
        append_log(temp, humidity)
        print(f"{datetime.now().isoformat(timespec='seconds')}  {temp:.2f}°C  {humidity:.2f}%")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
