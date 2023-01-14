from machine import Pin
import time

led = Pin(25,Pin.OUT)
command_220 = Pin(22,Pin.OUT)



while True:
    led.toggle()
    command_220.toggle()
    time.sleep(2)
