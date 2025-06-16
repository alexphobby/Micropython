# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from machine import Pin,PWM,Timer,ADC
from time import sleep
debug_pin = Pin(39, mode = Pin.IN,pull=Pin.PULL_DOWN)

 
if debug_pin.value() == 0:
    import espnow_transceiver_as

