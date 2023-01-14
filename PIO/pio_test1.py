import time
from machine import PWM


import time
from machine import Pin
import rp2

pwm_pin = Pin(7)
pwm = PWM(pwm_pin)
pwm.freq(50)
pwm.duty_u16(33000)


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
#,out_shiftdir=rp2.PIO.SHIFT_RIGHT,
#             autopull=True,pull_thresh=3)
def wait_pin_low():
    wait(0, pin, 0)
    wait(1, pin, 0)
    
    wrap_target()
    
    #jmp(not_osre,)
    pull(noblock) # read data if available
    mov(x,osr) # after pull, if no data, x is pushed into osr
    mov(y,x)

    #wait(1, pin, 0)
    wait(0, pin, 0)
    
    label("delay_on")
    jmp(y_dec, "delay_on") [31]
    set(pins, 1)    [31]
    nop()           [31]
    nop()           [31]
    mov(y,x)
    set(pins, 0)
    wait(1, pin, 0)
    
    label("second_delay_on")
    jmp(y_dec, "second_delay_on") [31]
    set(pins, 1)    [31]
    nop()           [31]
    nop()           [31]
    mov(y,x)
    set(pins, 0)
    #label("delay_on")
    #jmp(y_dec, "delay_on")   
    
    #wait(1, pin, 0)
    #wait(0, pin, 0)
    
    #set(pins, 1)    [10]
    #label("delay")
    #jmp(y_dec,"delay") [31] # delay until x is 0
    
    #mov(x,y)

    #set(pins, 0)   

    wrap()


def handler(sm):
    # Print a (wrapping) timestamp, and the state machine object.
    print(time.ticks_ms(), sm)


# Instantiate StateMachine(0) with wait_pin_low program on Pin(16).
rpm = Pin(5, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)

#led.high()
#time.sleep(0.2)
#led.low()
#time.sleep(1)

sm0 = rp2.StateMachine(0, wait_pin_low,freq = 500000, set_base = led,in_base= rpm) #in_base= rpm,
sm0.put(140)
sm0.exec("pull()")
sm0.exec("mov(isr, osr)")
sm0.active(1)
#sm0.irq(handler)


#sm0.active(1)




while True:
    input1 = int(input("delay"))
    sm0.put(input1)
    print(input1)
        #sm0.exec("set(0, 1)")
    time.sleep(0.2)
        #sm0.put(0)
        #time.sleep(1)
        #sm0.exec("set(0, 0)")
        #time.sleep(0.1)



# Example of using PIO for PWM, and fading the brightness of an LED

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep


@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)
    mov(x, osr) # Keep most recent pull data stashed in X, for recycling by noblock
    mov(y, isr) # ISR must be preloaded with PWM count max
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop()         .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")


class PIOPWM:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, pwm_prog, freq=2 * count_freq, sideset_base=Pin(pin))
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count

    def set(self, value):
        # Minimum value is -1 (completely turn off), 0 actually still produces narrow pulse
        value = max(value, -1)
        value = min(value, self._max_count)
        self._sm.put(value)


# Pin 25 is LED on Pico boards
led = 2
pwm = PIOPWM(0, led, max_count=(1 << 16) - 1, count_freq=10_000_000)

while True:
    for i in range(256):
        pwm.set(i ** 2)
        sleep(0.01)
        
        
        
        





while True:
    time.sleep(1)
import time
import rp2
from machine import Pin

# Define the blink program.  It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blinking visible by eye.
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1)   [1]
#    nop()          [31]
#    nop()          [31]
#    nop()          [31]
#    nop()          [31]
    set(pins, 0)   [1]
#    nop()          [31]
#    nop()          [31]
#    nop()          [31]
#    nop()          [31]
    wrap()

# Instantiate a state machine with the blink program, at 2000Hz, with set bound to Pin(25) (LED on the rp2 board)
sm = rp2.StateMachine(0, blink, freq=5000, set_base=Pin(2))

# Run the state machine for 3 seconds.  The LED should blink.
sm.active(1)
time.sleep(30)
sm.active(0)