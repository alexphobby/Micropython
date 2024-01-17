import time

from machine import Pin, I2C, Timer, Signal
from VL53L0X import VL53L0X
import asyncio

threshold = 30
auto_flush_wait = 1000*60*60*24*2
last_flush = 0

print(f"Range threshold: {threshold} cm")
flush_pin = Signal(Pin(22,Pin.OUT,value = 0), invert=True) # Pin(22, Pin.OUT,value=0) #
#led = Signal(Pin(9,Pin.OUT,value = 0), invert=False)
led = Pin(21, Pin.OUT,value=0)

switch = Pin(20,Pin.IN,Pin.PULL_DOWN)

timer1 = Timer()
timer2 = Timer()

print("setting up i2c")

#ESP32: i2c = I2C(0,scl=Pin(3),sda=Pin(4))
#PI PICO:
i2c = I2C(0,scl=Pin(1),sda=Pin(0))
print(i2c.scan())
tof = VL53L0X(i2c)

# the measuting_timing_budget is a value in ms, the longer the budget, the more accurate the reading. 
budget = tof.measurement_timing_budget_us
print("Budget was:", budget)
tof.set_measurement_timing_budget(400000)

# Sets the VCSEL (vertical cavity surface emitting laser) pulse period for the 
# given period type (VL53L0X::VcselPeriodPreRange or VL53L0X::VcselPeriodFinalRange) 
# to the given value (in PCLKs). Longer periods increase the potential range of the sensor. 
# Valid values are (even numbers only):

# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)

# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

async def flush():
    global last_state,last_flush
    print("Flush!")
    
    flush_pin.on()
    await asyncio.sleep_ms(5_000)
    flush_pin.off()
    led.off()
    #timer1.init(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:flush_pin.off())   # Timer.ONE_SHOT
    last_state=0
    last_flush = time.ticks_ms()
    
        

#modes: away(0) -> close +  timer(1) -> timer(2) -> away + timer (3) -> flush(4)

def in_proximity():
    global threshold
    range = int(tof.ping()/10) - 5
    #print(range)
    if range < threshold:
        return True
    else:
        return False
    
if in_proximity():
    last_state = 1
else:
    last_state = 0
    
    
last_test = 0
#while True:
async def main():
    global last_state,last_test,last_flush
    counter = 0
    while True:
        
        if time.ticks_diff(tmp := time.ticks_ms(), last_flush) > auto_flush_wait :
            last_flush = tmp
            print("timer flush")
            flush_pin.on()
            await asyncio.sleep_ms(3000)
            flush_pin.off()

        while switch.value() == 1:
            #print("switch")
            flush_pin.on()
            await asyncio.sleep_ms(500)
            #asyncio.create_task(flush())
        if switch.value() == 0:
            flush_pin.off()
        
        if last_state == 0 and in_proximity() and time.ticks_diff(tmp := time.ticks_ms(), last_test) > auto_flush_wait/2 :
            flush_pin.on()
            await asyncio.sleep_ms(500)
            flush_pin.off()
            
            
        if last_state == 0 and in_proximity():
            last_state = 1
            counter = 0
            print("Close (1)")
        
            
        if last_state == 1:# and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            await asyncio.sleep_ms(1_000)
            #last_test = tmp
            if in_proximity():
                counter += 1
                print(f"Close timer: {counter}")
                if counter == 9:
                    print("Ready to flush!")
                    led.on()
            else:
                if counter >= 9:
                    counter = 0
                    last_state = 2
                    print(f"State = {last_state}")
                else:
                    counter = 0
                    last_state = 0
                    print(f"Just passing thru .. state = {last_state}")
                    
                
        
        if last_state == 2: #and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            #last_test = tmp
            await asyncio.sleep_ms(1_000)
            if not in_proximity():
                counter += 1
            
            else:
                counter = 0
                last_state = 10
                print(f"State 2->10 not leaving")
            
            if counter >= 3:
                counter = 0
                last_state = 3
                print(f"State = {last_state}")
        
        if last_state == 10: # and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            #last_test = tmp
            await asyncio.sleep_ms(1_000)
            if not in_proximity():
                last_state = 3
                print(f"State 10 -> leaving State = {last_state}")
        
        if last_state == 3: #and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            asyncio.create_task(flush())
            last_state = 5 #intermediate while flushing
            #print("should flush")
            await asyncio.sleep_ms(10_000)
        
        await asyncio.sleep_ms(100)

asyncio.run(main())
