import time

from machine import Pin, I2C, Timer, Signal
from VL53L0X import VL53L0X
import asyncio

threshold = 26
auto_flush_wait = 1000*60*60*24*2
last_flush = 0

print(f"Range threshold: {threshold} cm")
flush_pin = Signal(Pin(22,Pin.OUT,value = 1), invert=True) # Pin(22, Pin.OUT,value=0) #
event_flush = asyncio.Event()
event_close = asyncio.Event()
event_button_pressed = asyncio.Event()

#led = Signal(Pin(9,Pin.OUT,value = 0), invert=False)
led = Pin(21, Pin.OUT,value=0)

switch = Pin(20,Pin.IN,Pin.PULL_DOWN)
    
#switch.irq(handler=button_pressed,trigger=Pin.IRQ_RISING)

async def poll_button():
    while True:
        if switch.value():
            event_flush.set()
        
        await asyncio.sleep(0.2)

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
#tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)

# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
#tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
async def flush(duration = 5000,on_demand = False ):
    if on_demand:
        print("Flush on demand")
        flush_pin.on()
        await asyncio.sleep_ms(duration)
        flush_pin.off()
        event_flush.clear()
        last_flush = time.ticks_ms()
        last_state=0
        led.off()
        
    else:        
        while True:
            await event_flush.wait()
            led.on()
            print("Flush after wait event")
            flush_pin.on()
            await asyncio.sleep_ms(duration)
            flush_pin.off()
            led.off()
            event_flush.clear()
            last_flush = time.ticks_ms()
            last_state=0

    print("Flush on demand ended")
        

#modes: away(0) -> close +  timer(1) -> timer(2) -> away + timer (3) -> flush(4)

def in_proximity():
    global threshold
    range = int(tof.ping()/10) - 5
    print(range)
    if 10 < range < threshold:
        return True
    else:
        return False
    
if in_proximity():
    last_state = 1
else:
    last_state = 0
    
    
last_test = 0


async def timed_refresh():
    last_flush = 0
    while True:
        if time.ticks_diff(tmp := time.ticks_ms(), last_flush) > auto_flush_wait :
            last_flush = tmp
            print("timer flush")
            event_flush.set()
        
        await asyncio.sleep(360)


    
    
#while True:
async def main():
    global last_state,last_test,last_flush
    counter = 0
    while True:
        
         
        if last_state == 0 and in_proximity():
            if time.ticks_diff(tmp := time.ticks_ms(), last_test) > auto_flush_wait*0.8 :
                print("timed flush in proximity")
                await flush()
            else:              
                last_state = 1
                counter = 0
                print("Close (1)")
            
            
        if last_state == 1:# and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            print("State = 1")
            await asyncio.sleep_ms(1_000)
            #last_test = tmp
            if in_proximity():
                counter += 1
                print(f"Close timer: {counter}")
                if counter >= 7:
                    print("Ready to flush!")
                    led.on()
            else:
                print("state 2 not in proximity")
                if counter >= 7:
                    counter = 0
                    last_state = 2
                    print(f"State = {last_state}")
                else:
                    counter = 0
                    last_state = 0
                    print(f"Just passing thru .. state = {last_state}")
                    
                
        
        if last_state == 2: #and time.ticks_diff(tmp := time.ticks_ms(), last_test) >= 1000:
            print("state = 2")
            #last_test = tmp
            await asyncio.sleep_ms(1_000)
            if not in_proximity():
                counter += 1
            
            else:
                counter = 0
                last_state = 10
                print(f"State 2->10 not leaving")
            
            if counter >= 2:
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
            print("State 3, flush")
            await flush(on_demand=True)
            
            last_state = 0 #intermediate while flushing
            #print("should flush")
            await asyncio.sleep(120)
        
        await asyncio.sleep_ms(2000)

asyncio.create_task(flush())
asyncio.create_task(poll_button())
asyncio.create_task(timed_refresh())

asyncio.run(main())
