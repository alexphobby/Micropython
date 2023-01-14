from micropython import const
import rp2
from rp2 import PIO, asm_pio
import time
from machine import PWM


import time
from machine import Pin
import rp2

#pwm_pin = Pin(7)
#pwm = PWM(pwm_pin)
#pwm.freq(50)
#pwm.duty_u16(33000)

from machine import Pin,Timer, PWM
from rp2 import PIO, asm_pio, StateMachine
    
@asm_pio()    
def get_rpm():
    set(x,0)
    wrap_target()
    label('loop')
    wait(0,pin,0)
    pull(noblock) # read data if available
    mov(x,osr) # after pull, if no data, x is pushed into osr
    #mov(y,x)

    wait(1,pin,0)
    jmp(x_dec,'loop')
    wrap()
    
class SMCounter:
    
    def __init__(self, smID, InputPin):
        self.counter = 0x0
        self.sm = StateMachine(smID)
        self.pin = InputPin
        self.sm.init(PIO_COUNTER,freq=125_000_000,in_base=self.pin)
        self.sm.active(1)
    
    def value(self):
        self.sm.exec('mov(isr,x)')
        self.sm.exec('push()')
        self.counter = self.sm.get()
        print(self.counter)
        return  (0x100000000 - self.counter) #& 0xffffffff
    
    def reset(self):
        #self.sm.active(0)
        self.sm.put(0)
        #self.sm.init(PIO_COUNTER,freq=125_000_000,in_base=self.pin)
        #self.sm.active(1)
        

    def __del__(self):
        self.sm.active(0)
        
        
#from SMCounter import SMCounter
#from machine import Pin
#import utime

#counter = SMCounter(smID=0,InputPin=Pin(5,Pin.IN,Pin.PULL_UP))
motor_in_pin=Pin(4,Pin.IN,Pin.PULL_UP)

sm_rpm = rp2.StateMachine(1, get_rpm,freq = 125_000_000, in_base= motor_in_pin) #in_base= rpm,
sm_rpm.active(1)

while True:
    
#    print(counter.value())
#    counter.reset()
    
    sm_rpm.exec('mov(isr,x)')
    sm_rpm.exec('push()')
    counter = sm_rpm.get()
    #    print(self.counter)
    print(int((0x100000000 - counter) & 0xffffffff))
    sm_rpm.put(0) #reset counter
    
    time.sleep(1)
