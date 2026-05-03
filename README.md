# Greenhouse Temperature Monitor

Logs temperature and humidity from an AHT20 sensor to a CSV file on a Raspberry Pi Zero 2, every 5 minutes. Optionally displays the current temperature on a SH5461AS 4-digit 7-segment display.

---

## Hardware

- Raspberry Pi Zero 2 W
- AHT20 temperature/humidity sensor (I2C)
- SH5461AS 4-digit 7-segment display (optional)
- 8× 470Ω resistors (for display)
- Female-to-female jumper wires
- MicroSD card (8 GB+)

### Wiring

Connect the AHT20 to the Pi's 40-pin header:

| AHT20 pin | Pi pin | GPIO |
|-----------|--------|------|
| VIN       | Pin 1  | 3.3 V |
| GND       | Pin 6  | GND  |
| SDA       | Pin 3  | GPIO 2 |
| SCL       | Pin 5  | GPIO 3 |

#### SH5461AS Display (optional)

Connect segment pins through a **470Ω resistor** each. Digit pins connect directly.

| Display pin | Function      | Resistor | Pi GPIO (BCM) | Pi physical pin |
|-------------|---------------|----------|---------------|-----------------|
| 11          | A             | 470Ω     | 17            | 11              |
| 7           | B             | 470Ω     | 18            | 12              |
| 4           | C             | 470Ω     | 27            | 13              |
| 2           | D             | 470Ω     | 22            | 15              |
| 1           | E             | 470Ω     | 23            | 16              |
| 10          | F             | 470Ω     | 24            | 18              |
| 5           | G             | 470Ω     | 25            | 22              |
| 3           | DP            | 470Ω     | 12            | 32              |
| 12          | D1 (leftmost) | direct   | 5             | 29              |
| 9           | D2            | direct   | 6             | 31              |
| 8           | D3            | direct   | 13            | 33              |
| 6           | D4 (rightmost)| direct   | 19            | 35              |

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
pip install adafruit-circuitpython-ahtx0 RPi.GPIO
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

## Display Setup (SH5461AS)

`display.py` reads the latest temperature from the CSV and continuously multiplexes the 4-digit display. It shows readings like `23.4C`.

### Test the display

```bash
source .venv/bin/activate
python3 display.py
```

Press `Ctrl+C` to stop.

### Run the display automatically on boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/greenhouse-display.service
```

Paste the following:

```ini
[Unit]
Description=Greenhouse temperature display
After=multi-user.target

[Service]
ExecStart=/home/pi/greenhouse-temperature-monitor/.venv/bin/python3 /home/pi/greenhouse-temperature-monitor/display.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable greenhouse-display
sudo systemctl start greenhouse-display
```

Check status:

```bash
sudo systemctl status greenhouse-display
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
| `display.py` | Drives the SH5461AS display, showing the latest temperature from the CSV |
| `monitor.py` | Original serial monitor for QT Py ESP32S2 — run this on a laptop |
| `device/code.py` | CircuitPython firmware for the QT Py ESP32S2 |
