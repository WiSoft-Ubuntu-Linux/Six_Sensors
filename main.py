import time
import adafruit_dht
import board

dht_device = adafruit_dht.DHT22(board.D4)

try:
  while True:
    try:
      temperature = dht_device.temperature
      humidity = dht_device.humidity
      print(f"Temperature = {temperature:0.1f}*C Humidity = {humidity:0.1f}%")
    except RuntimeError:
      time.sleep(1.0)

    time.sleep(2.0)

except KeyboardInterrupt:
  print("I'm done!")
finally:
  dht_device.exit()