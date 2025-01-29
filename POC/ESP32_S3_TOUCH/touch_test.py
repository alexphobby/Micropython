
from machine import TouchPad, Pin
from time import sleep
import esp32
import sys

if "ESP32S3" in sys.implementation._machine:
    from neopixel_util import *
    led = NEOPIXEL_UTIL()
    
t = TouchPad(Pin(5))
sleep(1)
previous=t.read()

for i in range(10):
    current=t.read()
    if current-previous< 100:
        previous = int((previous + current)/2)

base = round(previous)
print(f'Base value: {base}')
t.config(base + 500)
#while True:
#    
#    if abs(base - t.read()) > 800:
#        print(t.read())
#        
#    sleep(0.1)
 
 
    
esp32.wake_on_touch(True)

while True:
    led.toggle()
    machine.lightsleep()
    #sleep(0.2)
    
    

