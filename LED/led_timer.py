import machine
import time
from machine import Timer

led = machine.Pin(2,machine.Pin.OUT)
led.on()

rpm_pin = machine.Pin(5, machine.Pin.IN)

pwm_pin = machine.Pin(4, machine.Pin.OUT)

my_pwm = machine.PWM(pwm_pin)
my_pwm.freq(50000)
timer1 = Timer()
timer1.init(period=100, mode=Timer.PERIODIC, callback= lambda t:led.toggle())
rpm = 0
i=0

import utime
from machine import Pin
#from rp2 import PIO, StateMachine, asm_pio
import rp2


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH)
def pulse_count():
    """PIO for counting incoming pulses during gate low."""
    mov(x, osr)                                            # load x scratch with max value (2^32-1)
    wait(1, pin, 0)                                        
    wait(0, pin, 0) .side(0)                               # detect falling edge of gate
    label("counter")
    wait(0, pin, 1)                                        # wait for rising edge of input signal
    wait(1, pin, 1)
    jmp(pin, "output")                                     # as long as gate is low //
    jmp(x_dec, "counter")                                  # decrement x reg - count incoming pulses
    label("output") 
    mov(isr, x) .side(1)                                   # move pulse count value to isr and set pin to high to tell clock counting sm to stop counting
    push()                                                 # send data to FIFO
    irq(block, 5)                                          # set irq and wait for gate PIO to acknowledge

  
@rp2.asm_pio() # No additional arguments required
def pulse_counter():
    
    label("loop")           # Start of the loop
    mov(x, null)            # Clear X
    mov(osr, null)          # Clear OSR
    pull(noblock)           # Pull from TX FIFO - if this is empty the OSR is filled from X
                            # OSR must be empty for either to work
    mov(x, osr)             # Load value from OSR into X
    
    jmp(not_x, "continue")  # If X is not empty, we're going to reset the counter and output the data
    mov(isr, y)             # Move Y (which is (2^32 - 1 - the number of edges)) into the ISR
    push()                  # Push that value into the RX FIFO
    mov(y, osr)             # Reset Y to 2^32 - 1 (which the value in the OSR right now)
       
    label("continue")       # If X is empty, we'll counting rising edges
    wait(1, pin, 0)         # wait for rising edge of input signal
    wait(0, pin, 0)
    jmp(y_dec, "loop")      # Jump back to the beginning and decrement Y.

# Create the state machine on the correct pin and start it, and initialise it.
pulse_counter_sm = rp2.StateMachine(0, pulse_counter, in_base=rpm_pin) #
pulse_counter_sm.active(1)
pulse_counter_sm.put(0xFFFFFFFF)

# Save the time in microseconds
ticks = utime.ticks_us()

while(True):
    utime.sleep(1)  # Wait for 1s
    last_ticks = ticks    
    pulse_counter_sm.put(0xFFFFFFFF) # This value both triggers the request for data and resets the counter
    ticks = utime.ticks_us() # Save the time the counter was restarted
                             # This is here so it can be right after the put() command for better accuracy
    
    if not pulse_counter_sm.rx_fifo(): # Check if there's any data to get
        print("No Data")
    else:
        pulses = 0xFFFFFFFF - pulse_counter_sm.get()            # Calculate the actual number of pulses
        period = utime.ticks_diff(utime.ticks_us(), last_ticks) # Calculate time difference
        # Display the data
        print(str(pulses) + " pulses, " + str(period/1000000) + " s, " + str(1000000 * pulses/period) + " Hz" )









def get_rpm(t):
    global rpm
    global i
    rpm = i*3
    i=0
    print("r:{}".format(rpm))


timer2 = Timer()
timer2.init(period=200, mode=Timer.PERIODIC, callback= get_rpm)

def increment_rpm(p):
   global i
   i+=1

#rpm_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler = increment_rpm)
#rpm_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler = lambda x: i+=1)


while True:
    #led.toggle()
    #my_pwm.duty_u16(40000)
    #time.sleep(5)
    #print(rpm)
    my_pwm.duty_u16(50000)
    time.sleep(5)
    #print(rpm)
    
