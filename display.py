#!/usr/bin/env python3
"""Drive SH5461AS 4-digit 7-segment display showing current temperature from CSV."""

import csv
import os
import time
import RPi.GPIO as GPIO

SEG_PINS = {'A': 17, 'B': 18, 'C': 27, 'D': 22, 'E': 23, 'F': 24, 'G': 25, 'DP': 12}
DIGIT_PINS = [5, 6, 13, 19]  # D1–D4, left to right

# A, B, C, D, E, F, G
CHAR_MAP = {
    '0': (1,1,1,1,1,1,0),
    '1': (0,1,1,0,0,0,0),
    '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1),
    '4': (0,1,1,0,0,1,1),
    '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1),
    '7': (1,1,1,0,0,0,0),
    '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1),
    '-': (0,0,0,0,0,0,1),
    ' ': (0,0,0,0,0,0,0),
    'C': (1,0,0,1,1,1,0),
}

LOG_FILE = os.path.join(os.path.dirname(__file__), "temperature_log.csv")
CSV_REFRESH_SECS = 10


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in SEG_PINS.values():
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    for pin in DIGIT_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)  # HIGH = digit off (common cathode)


def show_digit(pos, char, dp=False):
    pattern = CHAR_MAP.get(char, CHAR_MAP[' '])
    GPIO.output(DIGIT_PINS[pos], GPIO.LOW)
    for seg, state in zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], pattern):
        GPIO.output(SEG_PINS[seg], state)
    GPIO.output(SEG_PINS['DP'], GPIO.HIGH if dp else GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(DIGIT_PINS[pos], GPIO.HIGH)
    for pin in SEG_PINS.values():
        GPIO.output(pin, GPIO.LOW)


def temp_to_display(temp):
    """Return list of (char, dp) tuples for 4 digit positions."""
    if temp is None:
        return [('-', False)] * 4

    if temp >= 100:
        s = str(int(round(temp)))[:3].rjust(3)
        return [(c, False) for c in s] + [('C', False)]

    if temp >= 0:
        integer, decimal = f"{temp:.1f}".split('.')
        integer = integer.rjust(2)
        return [
            (integer[0], False),
            (integer[1], True),   # decimal point after second digit: e.g. 23.4
            (decimal[0], False),
            ('C', False),
        ]

    # Negative
    abs_temp = abs(temp)
    if abs_temp < 10:
        integer, decimal = f"{abs_temp:.1f}".split('.')
        return [('-', False), (integer, True), (decimal[0], False), ('C', False)]
    else:
        s = str(int(abs_temp)).rjust(2)
        return [('-', False), (s[0], False), (s[1], False), ('C', False)]


def read_latest_temp():
    try:
        with open(LOG_FILE) as f:
            rows = list(csv.DictReader(f))
            if rows:
                return float(rows[-1]['temperature_c'])
    except (FileNotFoundError, ValueError, KeyError):
        pass
    return None


def main():
    setup_gpio()
    temp = read_latest_temp()
    display_data = temp_to_display(temp)
    last_read = time.time()

    try:
        while True:
            if time.time() - last_read >= CSV_REFRESH_SECS:
                temp = read_latest_temp()
                display_data = temp_to_display(temp)
                last_read = time.time()
            for pos, (char, dp) in enumerate(display_data):
                show_digit(pos, char, dp)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
