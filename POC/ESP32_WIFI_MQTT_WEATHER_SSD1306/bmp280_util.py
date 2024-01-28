#HDC1080 helper
#Usage:
#from bmp280_util import bmp280_util
#sensor_temp = bmp280_util()
#sensor_temp.temperature()
#sensor_temp.humidity()
#sensor_temp.enabled
from machine import Pin,I2C
from bmp280 import *

class bmp280_util:
    i2c=""
    bmp280 = ""
    enabled = False
    def __init__(self,i2c = ""):
        self.i2c = i2c
        try:
            self.bmp280 = BMP280(i2c=self.i2c)
            self.enabled = True
            print("BME280 initialised")
        except:
            print("no humidity")

    def temperature(self):
        try:
            temperature = self.bmp280.read_compensated_data()[0]
        except:
            temperature = 0
            
        return temperature
    
    def humidity(self):
        try:
            humidity = self.bmp280.read_compensated_data()[2]
        except:
            humidity=0
            
        return humidity

