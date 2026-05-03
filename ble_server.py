#!/usr/bin/env python3
"""BLE GATT server broadcasting temperature and humidity from the CSV log."""

import csv
import os
import struct
from bluezero import adapter, peripheral

LOG_FILE = os.path.join(os.path.dirname(__file__), "temperature_log.csv")

ENV_SENSING_SVC  = '0000181A-0000-1000-8000-00805f9b34fb'
TEMPERATURE_CHR  = '00002A6E-0000-1000-8000-00805f9b34fb'
HUMIDITY_CHR     = '00002A6F-0000-1000-8000-00805f9b34fb'


def read_latest():
    try:
        with open(LOG_FILE) as f:
            rows = list(csv.DictReader(f))
            if rows:
                return float(rows[-1]['temperature_c']), float(rows[-1]['humidity_pct'])
    except (FileNotFoundError, ValueError, KeyError):
        pass
    return None, None


def temp_value():
    temp, _ = read_latest()
    raw = int(round(temp * 100)) if temp is not None else 0
    return list(struct.pack('<h', raw))  # 16-bit signed, units of 0.01 °C


def humidity_value():
    _, humidity = read_latest()
    raw = int(round(humidity * 100)) if humidity is not None else 0
    return list(struct.pack('<H', raw))  # 16-bit unsigned, units of 0.01 %


def main():
    addr = list(adapter.Adapter.available())[0].address
    greenhouse = peripheral.Peripheral(addr, local_name='Greenhouse')

    greenhouse.add_service(srv_id=1, uuid=ENV_SENSING_SVC, primary=True)

    greenhouse.add_characteristic(
        srv_id=1, chr_id=1, uuid=TEMPERATURE_CHR,
        value=[], notifying=False,
        flags=['read'],
        read_callback=temp_value,
        write_callback=None,
        notify_callback=None,
    )
    greenhouse.add_characteristic(
        srv_id=1, chr_id=2, uuid=HUMIDITY_CHR,
        value=[], notifying=False,
        flags=['read'],
        read_callback=humidity_value,
        write_callback=None,
        notify_callback=None,
    )

    print('BLE server running — connect with nRF Connect and look for "Greenhouse"')
    greenhouse.publish()


if __name__ == '__main__':
    main()
