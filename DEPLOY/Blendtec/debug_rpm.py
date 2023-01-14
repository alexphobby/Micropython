from machine import Pin
from machine import Timer
import time

i=0

motor_in_pin = Pin(21,Pin.IN) #, Pin.PULL_DOWN
led = Pin(2,Pin.OUT)

time.sleep(2)


def count(pin):
    global i
    i += 1
    print(i)
    
motor_in_pin.irq(trigger=Pin.IRQ_RISING, handler=count) #Pin.IRQ_RISING|Pin.IRQ_FALLING


while True:
    time.sleep(0.2)
    #print(motor_in_pin.value())