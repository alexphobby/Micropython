from i2c_init import *


from mqtt_as_init import *
test()

from senko import Senko
OTA = Senko(user="alexphobby",branch = "main", repo="Micropython", working_dir="POC/ESP32_AS_MQTT_WEATHER_SSD1306", files=["test.py"])
OTA.update()

if OTA.update():
    print("Updated to the latest version! Rebooting...")
    machine.reset()