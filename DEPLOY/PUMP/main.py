# Generic Tests for radio-fast module.
# Modify config.py to provide master_config and slave_config for your hardware.
import machine #, radiofast
import time
from time import ticks_ms, ticks_diff
#from config import master_config, slave_config, FromMaster, ToMaster

from machine import Pin, I2C, SPI,PWM
from machine import Timer
import onewire,ds18x20

import struct

last_run_time = 0

time_wait_start_pump = int(30 * 1000 * 60)
time_wait_stop_pump = int(2 * 1000 * 60)


#led_pin = Pin(25,Pin.OUT)
#load_pin = Pin(22,Pin.OUT)
led_pin = Pin(4,Pin.OUT)
#load_pin = Pin(22,Pin.OUT)
                             
pir_pin = Pin(3,Pin.IN,Pin.PULL_DOWN)

#load_pin.high()
#led_pin.low()


time.sleep(30)


# the device is on GPIO12
dat = machine.Pin(2)

# create the onewire object
try:
    ds = ds18x20.DS18X20(onewire.OneWire(dat))
    rom = ds.scan()[0]
    ds.convert_temp()
    time.sleep_ms(750)
    ds.read_temp(rom)
    print(ds.read_temp(rom), end=' ')
#    print()

except Exception as ex:
    print("Error: ",ex)

sensed = False

timer = Timer()

def load_off(timer):
    global last_run_time
    
    load_pin.high()
    led_pin.low()
    last_run_time = ticks_ms()

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)





def pir_sense(pin):
    global sensed
    
    pin.irq(trigger=0) #0|Pin.IRQ_RISING|Pin.IRQ_FALLING
    print("PIR")
    sensed = True
    pin.irq(trigger=Pin.IRQ_RISING, handler=pir_sense) #Pin.IRQ_RISING|Pin.IRQ_FALLING

pir_pin.irq(trigger=Pin.IRQ_RISING, handler=pir_sense) #Pin.IRQ_RISING|Pin.IRQ_FALLING


while True:
    if ticks_diff(tmp := ticks_ms(), last_run_time) >= time_wait_start_pump or last_run_time == 0:
        
        #print("elapsed")
        #print(sensed)
        if sensed:
            #print("sensed")
            last_run_time = tmp
            
            load_pin.low()
            led_pin.high()

            timer.init(period=time_wait_stop_pump, mode=Timer.ONE_SHOT, callback=load_off)   # Timer.ONE_SHOT . Period in ms
            sensed=False
        else:
            ds.convert_temp()
            time.sleep_ms(750)
            temp = ds.read_temp(rom)
            if int(temp) > 30:
                load_off(temp)

    #print(pir_pin.value())
    time.sleep(0.5)

import onewire,ds18x20

# the device is on GPIO12
dat = machine.Pin(2)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# loop 10 times and print all temperatures
for i in range(100):
    print('temperatures:', end=' ')
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(ds.read_temp(rom), end=' ')
    print()
    
    