# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#from time import sleep

#sleep(5)
#import test_sleep
#import test_uart
from machine import Pin,PWM,Timer,ADC
debug_pin = Pin(39, mode = Pin.IN, pull = Pin.PULL_DOWN)
if debug_pin.value() != 1:
    print("import")
    import presence_espnow
else:
    print("debug")