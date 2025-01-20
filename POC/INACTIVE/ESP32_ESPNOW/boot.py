# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import time
time.sleep(2)
from CONNECTWIFI import *
wifi = CONNECTWIFI()
from MACHINES import *
my_machine = MACHINES()

import test_espnow_transmit