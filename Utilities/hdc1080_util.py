#HDC1080 helper
#Usage:
#from hdc1080_util import hdc1080_util
#hdc = hdc1080_util()
#hdc.temperature()

import machine
from HDC1080 import HDC1080
from machine import Pin

class hdc1080_util:
    
    i2c=""
    hdc1080 = ""
    def __init__(self):
    
        
        try:
            self.i2c = machine.I2C(0,scl=Pin(1),sda=Pin(0))
        except:
            print("no i2c")
            
        try:
            self.hdc1080 = HDC1080(self.i2c)
            #print(f"Temp: {round(self.hdc1080.read_temperature(celsius=True),1)}")
            #print(f"Humidity: {int(self.hdc1080.read_humidity())}")


        except:
            print("no humidity")

    def temperature(self):
        temperature = round(self.hdc1080.read_temperature(celsius=True),1)
        return temperature
    
    def humidity(self):
        humidity = int(self.hdc1080.read_humidity())
        return humidity
