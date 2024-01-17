<<<<<<< HEAD
#HDC1080 helper
#Usage:
#from hdc1080_util import hdc1080_util
#hdc = hdc1080_util()
#hdc.temperature()

import machine
import sys
from HDC1080 import HDC1080
from machine import Pin

class hdc1080_util:
    
    i2c=""
    hdc1080 = ""
    def __init__(self,i2c = ""):
        self.i2c = i2c
        try:
            if (self.i2c == "" and sys.platform == "esp32"):
                print("ESP32")
                self.i2c = machine.I2C(0,scl=machine.Pin(3),sda=machine.Pin(4))
            elif (self.i2c == ""):
                print("non ESP32")
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
        try:
            temperature = round(self.hdc1080.read_temperature(celsius=True),1)
        except:
            temperature = 0
            
        return temperature
    
    def humidity(self):
        try:
            humidity = int(self.hdc1080.read_humidity())
        except:
            humidity=0
            
        return humidity
=======
#HDC1080 helper
#Usage:
#from hdc1080_util import hdc1080_util
#hdc = hdc1080_util()
#hdc.temperature()

import machine
import sys
from HDC1080 import HDC1080
from machine import Pin

class hdc1080_util:
    
    i2c=""
    hdc1080 = ""
    def __init__(self,i2c = ""):
        self.i2c = i2c
        try:
            if (self.i2c == "" and sys.platform == "esp32"):
                print("ESP32")
                self.i2c = machine.I2C(0,scl=machine.Pin(3),sda=machine.Pin(4))
            elif (self.i2c == ""):
                print("non ESP32")
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
        try:
            temperature = round(self.hdc1080.read_temperature(celsius=True),1)
        except:
            temperature = 0
            
        return temperature
    
    def humidity(self):
        try:
            humidity = int(self.hdc1080.read_humidity())
        except:
            humidity=0
            
        return humidity
>>>>>>> 73a687a57bf723080c2979a422d007515a7e9b11
