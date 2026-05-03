#!/usr/bin/env python3
"""Read temperature and humidity from AHT20 via QT Py ESP32S2."""

import serial
import serial.tools.list_ports
import sys
import time

BAUD_RATE = 115200

# Injected into CircuitPython's raw REPL at startup
SENSOR_CODE = b"""\
import board, adafruit_ahtx0, time
i2c = board.STEMMA_I2C()
s = adafruit_ahtx0.AHTx0(i2c)
while True:
    print(f"TEMP:{s.temperature:.2f},HUMIDITY:{s.relative_humidity:.2f}")
    time.sleep(2)
"""


def find_qtpy_port():
    for port in serial.tools.list_ports.comports():
        if port.vid == 0x239A:  # Adafruit vendor ID
            return port.device
    return None


def enter_raw_repl(ser):
    """Interrupt running code and enter CircuitPython raw REPL mode."""
    ser.write(b"\x03\x03")  # Ctrl+C twice to stop current script
    time.sleep(0.5)
    ser.write(b"\x01")  # Ctrl+A to enter raw REPL
    time.sleep(0.5)
    ser.read_all()  # Flush response


def start_sensor_loop(ser):
    """Send sensor code via raw REPL; consume exactly the 'OK' preamble."""
    ser.write(SENSOR_CODE + b"\x04")  # Ctrl+D executes the block
    # Raw REPL sends exactly 2 bytes "OK" before streaming output
    deadline = time.time() + 5
    while time.time() < deadline:
        if ser.in_waiting >= 2:
            ack = ser.read(2)
            if ack == b"OK":
                return
            raise RuntimeError(f"Expected 'OK' from device, got: {ack!r}")
    raise RuntimeError("Timeout waiting for device acknowledgment")


def parse_reading(line: str) -> tuple[float, float] | None:
    try:
        parts = dict(item.split(":") for item in line.strip().split(","))
        return float(parts["TEMP"]), float(parts["HUMIDITY"])
    except (ValueError, KeyError):
        return None


def main():
    port = find_qtpy_port()
    if not port:
        print("QT Py not found. Is it connected?")
        sys.exit(1)

    print(f"Connecting to {port}...")
    with serial.Serial(port, BAUD_RATE, timeout=5) as ser:
        enter_raw_repl(ser)
        start_sensor_loop(ser)

        print(f"{'Time':<12} {'Temperature':>14} {'Humidity':>12}")
        print("-" * 40)

        while True:
            try:
                raw = ser.readline().decode("utf-8", errors="ignore")
                reading = parse_reading(raw)
                if reading:
                    temp, humidity = reading
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"{timestamp:<12} {temp:>12.2f}°C {humidity:>10.2f}%")
            except KeyboardInterrupt:
                print("\nStopped.")
                break
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break


if __name__ == "__main__":
    main()
