import time
from machine import Timer
from machine import Pin
#from machine import I2C
from machine import PWM
import math
#import picosleep

from utility import brightness_map
debug = True

time.sleep(5)

pwm_pin = Pin(20,Pin.OUT)
pwm_pin.low()

pwm = PWM(pwm_pin)
pwm.freq(1000)
pwm.duty_u16(0)

old_pwm = 0


def set_brightness(brightness):
    global old_brightness
    global old_pwm
    new_pwm = brightness_map[brightness]
    step = int((new_pwm - old_pwm)/10)
    
    if abs(step) > 10:
        for i in range(10):
            old_pwm += step
            pwm.duty_u16(old_pwm)
            #print("old bright: {}; new bright: {}; PWM: {} Step: {}".format(old_brightness,brightness,old_pwm,step))
            time.sleep(0.02)
    #else:
    pwm.duty_u16(new_pwm)
    old_pwm=new_pwm
    


while True: 
    #adc.read_u16()         # read value, 0-65535 across voltage range 0.0v - 3.3v
    #conversion_factor = 3.3 * 6 / (65535) 

    #for i in range(100):
    #reading = adc.read_u16() #* conversion_factor
    #reading1 = adc1.read_u16() #* conversion_factor
    set_brightness(3000)
    #picosleep.seconds(1)
    time.sleep(5)
    set_brightness(30)
    time.sleep(5)