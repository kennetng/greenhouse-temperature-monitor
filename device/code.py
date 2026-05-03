import time
import board
import adafruit_ahtx0

i2c = board.STEMMA_I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    temp = sensor.temperature
    humidity = sensor.relative_humidity
    print(f"TEMP:{temp:.2f},HUMIDITY:{humidity:.2f}")
    time.sleep(2)
