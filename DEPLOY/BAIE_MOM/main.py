from machine import Pin
import time
from machine import Timer
from machine import PWM
from machine import ADC

from dim import Dim
from brightness_map import brightness_map
adc = ADC(26)

dimSetPoint = int(adc.read_u16()* 233 / 65000)

#analogReadings = []
analogReading = 0
def analogReadings(self):
    global analogReadings,analogReading,motion
    if motion.value() == 1:
        return

    for i in range(20):
        analogReadings.append(int(adc.read_u16()* 233 / 65000))
        analogReadings.pop(0)
        
        #print(f"Instant: {lightReadings[-1]};average: {old_average}")
    #average = 0
    
    for value in analogReadings:
        average = average + value/20
        
    if int(abs(average - analogReading)) > 3:
            #print(f"Update: {int(average)}")
        analogReading = int(average)
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
    if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:

timer_blink.init(period=1000, mode=Timer.PERIODIC, callback = blinkOnboardLed)

time.sleep(2)

def dimToOff(timer):
    global dim
    dim.dimToOff()

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
timer.init(period=1000, mode=Timer.ONE_SHOT, callback=analogReadings)   # Timer.ONE_SHOT . Period in m
while True:
    if motion.value() == 1:
        dim.setReqIndex1(dimSetPoint)
        timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in m
        
        
    #led.toggle()
#    led12.toggle()
    time.sleep(0.2)
    #print(motion.value())
    #time.sleep(0.1)