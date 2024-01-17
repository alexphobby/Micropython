import time
from machine import Pin, I2C, Timer, Signal
from vl53l0x import VL53L0X
import asyncio

print("setting up i2c")
i2c = I2C(0,scl=Pin(3),sda=Pin(4))

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
    global last_state
    print("Flush!")
    
    flush_pin.on()
    await asyncio.sleep_ms(5_000)
    flush_pin.off()
    led.off()
    #timer1.init(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:flush_pin.off())   # Timer.ONE_SHOT
    last_state=0
    
        

def in_proximity():
    global threshold
    range = int(tof.ping()/10) - 5
    #print(range)
    if range < threshold:
        return True
    else:
        return False


while True:
    print(in_proximity())
    time.sleep(2)