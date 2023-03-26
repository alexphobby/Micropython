from machine import Pin
import time
from machine import Timer
from machine import PWM
from machine import ADC

from dim import Dim
from brightness_map import brightness_map
adc = ADC(26)

dimSetPoint = int(adc.read_u16()* 233 / 65000)
#pwm_pin = Pin(15,Pin.OUT)
#pwm_pin.low()

#pwm = PWM(pwm_pin)
#pwm.freq(30000)
#pwm.duty_u16(0)
fade_time_ms=1000
dim = Dim(15,16,0,236,0,230,fade_time_ms)


led = Pin(25,Pin.OUT)
#led12 = Pin(15,Pin.OUT)
#led12.on()

motion = Pin(22, Pin.IN,Pin.PULL_DOWN)

timer = Timer()
timer_blink = Timer()

def blinkOnboardLed(timer):
    global led,adc,dimSetPoint
    led.toggle()
    dimSetPoint = int(adc.read_u16()* 233 / 65000)

    
timer_blink.init(period=1000, mode=Timer.PERIODIC, callback = blinkOnboardLed)

time.sleep(2)

def dimToOff(timer):
    global dim
    dim.dimToOff()

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)

while True:
    if motion.value() == 1:
        #led12.on()
        #dimSetPoint = int(adc.read_u16()* 233 / 65000)
        
        #while not dim.atSetpoint1():
        #    dim.dimStep()
        #dim.dimToSetpoint()
        dim.setReqIndex1(dimSetPoint)
        #print(brightness_map[dimSetPoint])
        #pwm.duty_u16(brightness_map[dim])
        timer.init(period=4*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in ms
        
    #led.toggle()
#    led12.toggle()
    time.sleep(0.2)
    #print(motion.value())
    #time.sleep(0.1)