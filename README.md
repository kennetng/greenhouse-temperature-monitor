# Greenhouse Temperature Monitor

Logs temperature and humidity from an AHT20 sensor to a CSV file on a Raspberry Pi Zero 2, every 5 minutes.

---

## Hardware

- Raspberry Pi Zero 2 W
- AHT20 temperature/humidity sensor (I2C)
- 4× female-to-female jumper wires
- MicroSD card (8 GB+)

### Wiring

Connect the AHT20 to the Pi's 40-pin header:

| AHT20 pin | Pi pin | GPIO |
|-----------|--------|------|
| VIN       | Pin 1  | 3.3 V |
| GND       | Pin 6  | GND  |
| SDA       | Pin 3  | GPIO 2 |
| SCL       | Pin 5  | GPIO 3 |

---

## Raspberry Pi Setup

### 1. Flash Raspberry Pi OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash **Raspberry Pi OS Lite (64-bit)** to the microSD card.

In the imager's advanced settings (gear icon) before flashing:
- Set hostname (e.g. `greenhouse`)
- Enable SSH
- Configure Wi-Fi SSID and password
- Set username and password

### 2. Boot and connect

Insert the card, power on the Pi, then SSH in:

```bash
ssh pi@greenhouse.local
```

### 3. Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Enable I2C

```bash
sudo raspi-config
```

Navigate to **Interface Options → I2C → Enable**, then reboot:

```bash
sudo reboot
```

After rebooting, verify the sensor is detected (address `0x38`):

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

You should see `38` in the output grid.

---

## Software Setup

### 5. Install Python dependencies

```bash
sudo apt install -y python3-pip python3-venv git
```

```bash
git clone <your-repo-url> ~/greenhouse-temperature-monitor
cd ~/greenhouse-temperature-monitor
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install adafruit-circuitpython-ahtx0
```

### 6. Test the logger

```bash
source .venv/bin/activate
python3 pi_logger.py
```

Expected output:

```
2026-05-01T12:00:00  23.45°C  58.12%
```

A `temperature_log.csv` file will be created in the project directory.

---

## Automatic Logging Every 5 Minutes

Use cron to run the logger automatically.

```bash
crontab -e
```

Add this line at the bottom (replace the path if yours differs):

```
*/5 * * * * /home/pi/greenhouse-temperature-monitor/.venv/bin/python3 /home/pi/greenhouse-temperature-monitor/pi_logger.py >> /home/pi/greenhouse-temperature-monitor/cron.log 2>&1
```

Save and exit. Cron will now log a reading every 5 minutes, even after reboots.

To confirm cron is running:

```bash
tail -f ~/greenhouse-temperature-monitor/cron.log
```

---

## Log Format

`temperature_log.csv` is a plain CSV file:

```
timestamp,temperature_c,humidity_pct
2026-05-01T12:00:00,23.45,58.12
2026-05-01T12:05:00,23.51,57.98
```

To view recent entries:

```bash
tail -20 ~/greenhouse-temperature-monitor/temperature_log.csv
```

---

## File Overview

| File | Purpose |
|------|---------|
| `pi_logger.py` | Reads AHT20 and appends one row to the CSV — run this on the Pi |
| `monitor.py` | Original serial monitor for QT Py ESP32S2 — run this on a laptop |
| `device/code.py` | CircuitPython firmware for the QT Py ESP32S2 |
