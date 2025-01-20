# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import time
from machine import freq
time.sleep(5)

#freq(80000000)
print(f"Frequency set to: {freq()}")
from i2c_init import *

from mqtt_as_init import *


#test()