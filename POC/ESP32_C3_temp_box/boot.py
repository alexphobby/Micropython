# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import time
from machine import freq,reset_cause
time.sleep(2)

#freq(80000000)
print(f"Frequency set to: {freq()}")
print(f"Reset cause: {reset_cause()}")
#import oled_temperature
from i2c_init import *
#oled.poweroff()



#import temperature
import toothbrush
#test()