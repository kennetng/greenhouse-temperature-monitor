# Greenhouse Temperature Monitor

Logs temperature and humidity from an AHT20 sensor every 10 seconds, and optionally shows the current temperature on a SH5461AS 4-digit display.

---

## What you need

- Raspberry Pi Zero 2 W
- AHT20 temperature/humidity sensor
- SH5461AS 4-digit 7-segment display *(optional)*
- 8× 470Ω resistors *(for the display)*
- Female-to-female jumper wires
- MicroSD card (8 GB+)

---

## Step 1 — Flash the Pi

1. Download and open [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Choose **Raspberry Pi OS Lite (64-bit)**
3. Click the **gear icon** before flashing and set:
   - Hostname (e.g. `greenhouse`)
   - Enable SSH
   - Wi-Fi SSID and password
   - Username and password
4. Flash to the microSD card, insert it into the Pi, and power on

---

## Step 2 — Connect via SSH

From your computer:

```bash
ssh pi@greenhouse.local
```

---

## Step 3 — Update and enable I2C

```bash
sudo apt update && sudo apt upgrade -y
```

```bash
sudo raspi-config
```

Go to **Interface Options → I2C → Enable**, then reboot:

```bash
sudo reboot
```

---

## Step 4 — Wire the AHT20 sensor

| AHT20 pin | Pi physical pin |
|-----------|-----------------|
| VIN       | Pin 1 (3.3 V)   |
| GND       | Pin 6 (GND)     |
| SDA       | Pin 3 (GPIO 2)  |
| SCL       | Pin 5 (GPIO 3)  |

After wiring, verify the sensor is detected:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

You should see `38` in the output grid.

---

## Step 5 — Install the software

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

---

## Step 6 — Test the logger

```bash
source .venv/bin/activate
python3 pi_logger.py
```

Expected output:

```
2026-05-01T12:00:00  23.45°C  58.12%
```

A `temperature_log.csv` file will be created in the project folder.

---

## Step 7 — Log automatically every 10 seconds

Create a systemd service so the logger runs on boot:

```bash
sudo nano /etc/systemd/system/greenhouse-logger.service
```

Paste this:

```ini
[Unit]
Description=Greenhouse temperature logger
After=multi-user.target

[Service]
ExecStart=/bin/bash -c 'while true; do /home/pi/greenhouse-temperature-monitor/.venv/bin/python3 /home/pi/greenhouse-temperature-monitor/pi_logger.py >> /home/pi/greenhouse-temperature-monitor/cron.log 2>&1; sleep 10; done'
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl enable greenhouse-logger
sudo systemctl start greenhouse-logger
```

Check it is running:

```bash
sudo systemctl status greenhouse-logger
```

View the log:

```bash
tail -f ~/greenhouse-temperature-monitor/cron.log
```

---

## Step 8 — Wire the display *(optional)*

The SH5461AS is a common cathode display. Segment pins need a **470Ω resistor** each. Digit pins connect directly.

| Display pin | Function       | Resistor | Pi GPIO (BCM) | Pi physical pin |
|-------------|----------------|----------|---------------|-----------------|
| 11          | A              | 470Ω     | 17            | 11              |
| 7           | B              | 470Ω     | 18            | 12              |
| 4           | C              | 470Ω     | 27            | 13              |
| 2           | D              | 470Ω     | 22            | 15              |
| 1           | E              | 470Ω     | 23            | 16              |
| 10          | F              | 470Ω     | 24            | 18              |
| 5           | G              | 470Ω     | 25            | 22              |
| 3           | DP             | 470Ω     | 12            | 32              |
| 12          | D1 (leftmost)  | direct   | 5             | 29              |
| 9           | D2             | direct   | 6             | 31              |
| 8           | D3             | direct   | 13            | 33              |
| 6           | D4 (rightmost) | direct   | 19            | 35              |

---

## Step 9 — Test the display *(optional)*

```bash
source .venv/bin/activate
python3 display.py
```

The display will show the latest temperature from the CSV, e.g. `23.4C`. Press `Ctrl+C` to stop.

---

## Step 10 — Run the display on boot *(optional)*

```bash
sudo nano /etc/systemd/system/greenhouse-display.service
```

Paste this:

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

Enable and start it:

```bash
sudo systemctl enable greenhouse-display
sudo systemctl start greenhouse-display
```

---

## Viewing logged data

`temperature_log.csv` looks like this:

```
timestamp,temperature_c,humidity_pct
2026-05-01T12:00:00,23.45,58.12
2026-05-01T12:05:00,23.51,57.98
```

To view the most recent entries:

```bash
tail -20 ~/greenhouse-temperature-monitor/temperature_log.csv
```

---

## File overview

| File | Purpose |
|------|---------|
| `pi_logger.py` | Reads the AHT20 and appends one row to the CSV |
| `display.py` | Drives the SH5461AS display, showing the latest temperature |
| `monitor.py` | Original serial monitor for QT Py ESP32S2 — run on a laptop |
| `device/code.py` | CircuitPython firmware for the QT Py ESP32S2 |
