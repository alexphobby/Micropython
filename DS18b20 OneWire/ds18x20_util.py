#HDC1080 helper
#Usage:
#from bmp280_util import bmp280_util
#sensor_temp = bmp280_util()
#sensor_temp.temperature()
#sensor_temp.humidity()
#sensor_temp.enabled
from machine import Pin
import onewire,ds18x20
import time
class ds18x20_util:
    enabled = False
    def __init__(self,pin = 4):

        try:
            self.ds = ds18x20.DS18X20(onewire.OneWire(Pin(pin)))
            self.rom = self.ds.scan()[0]
            self.enabled = True
            print("DS18X20 initialised")
        except:
            print("no DS sensor")
            self.enabled = False

    def temperature(self):
        if not self.enabled:
            return "-100"
        try:
            self.ds.convert_temp()
            time.sleep_ms(750)
            _temperature = self.ds.read_temp(self.rom)
            
        except Exception as ex:
            print(f"temp error: {ex}")
            _temperature = 0
            
        return _temperature
    def humidity(self):
        return -1
