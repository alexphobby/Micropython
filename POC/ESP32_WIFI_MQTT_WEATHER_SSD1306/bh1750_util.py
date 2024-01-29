#HDC1080 helper
#Usage:
#from bmp280_util import bmp280_util
#sensor_temp = bmp280_util()
#sensor_temp.temperature()
#sensor_temp.humidity()
#sensor_temp.enabled

from BH1750 import BH1750

class bh1750_util:
    i2c=""
    bh1750 = ""
    enabled = False
    def __init__(self,i2c = ""):
        self.i2c = i2c
        try:
            self.bh1750 = BH1750(i2c)
            self.enabled = True
            print("BH1750 initialised")
        except:
            print("no BH1750 light sensor")

    def light(self):
        try:
            _light = self.bh1750.luminance(self.bh1750.ONCE_HIRES_2)
            if _light > 1:
                return round(_light)
            else:
                return round(self.bh1750.luminance(self.bh1750.ONCE_HIRES_2),1)

        except:
            _light = -1
            
        return _light