import network
from machine import Pin
from machine import PWM
from hdc1080_util import hdc1080_util
hdc1080 = hdc1080_util()
#print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
#print(f"Humidity: {int(hdc1080.read_humidity())}")
print(hdc1080.temperature())
print(hdc1080.humidity())
