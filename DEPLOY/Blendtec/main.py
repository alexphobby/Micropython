from machine import Pin
from machine import Timer

from time import ticks_ms, ticks_diff
import time

import rp2

from pid import PID

motor_in_pin = Pin(21,Pin.IN) #, Pin.PULL_DOWN
motor_out_pin = Pin(16,Pin.OUT,Pin.PULL_DOWN)
motor_out_pin.off()
                                                                                                                                                            
sin_pin = Pin(18,Pin.IN, Pin.PULL_DOWN)

led_pin = Pin(16,Pin.OUT,Pin.PULL_DOWN)
time.sleep(4)
#machine.freq(250000000)

i=0


ramping=False
running=False
start_time = 0

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
#,out_shiftdir=rp2.PIO.SHIFT_RIGHT,
#             autopull=True,pull_thresh=3)
def control_triac():
    wait(0, pin, 0)
    wait(1, pin, 0) [31]
    
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

    wrap()

sm_triac = rp2.StateMachine(0, control_triac,freq = 500000, set_base = motor_out_pin,in_base= sin_pin) #in_base= rpm,

#sm_triac.put(115)
#sm_triac.exec("pull()")
#sm_triac.exec("mov(isr, osr)")

sm_triac.active(0)

@rp2.asm_pio()    
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
    
sm_rpm = rp2.StateMachine(2, get_rpm,freq = 10_000, in_base= motor_in_pin) #in_base= rpm,
sm_rpm.active(1)

#motor_in_pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda x: print("irq")) #Pin.IRQ_RISING|Pin.IRQ_FALLING


rps = 0

triac_timing = 120
#sm_triac.put(triac_timing)

def read_rps():
    global rps,factor
    return rps * factor

def print_output(message):
    global rps,pid
    global triac_timing,ramping,running
    if not ramping and not running:
        print("PID OFF")
        sm_triac.active(0)
        motor_out_pin.off()
        return
    
    #print("adjx100:{};PWM:{};ADCx10:{};Desired:{}".format(int(message*100),old_pwm/100,old_adc,desired))
    print("Triac: {};PID_Adj: {}; RPS_Adj: {};Factor: {};DesiredRPS: {}".format(triac_timing,message,rps*factor,factor,pid.set_point))
    triac_timing += message
    if triac_timing > 125:
        triac_timing = 125
    if triac_timing < 10:
        triac_timing = 10
    sm_triac.active(1)
    sm_triac.put(triac_timing)
    #time.sleep(0.05)


pid = PID(read_rps,print_output,P=-3.0, I=-0.01, D=0.0,debug = False)

#button_1 = Pin(28,Pin.IN, Pin.PULL_UP)
#button_2 = Pin(2,Pin.IN, Pin.PULL_UP)
#button_3 = Pin(3,Pin.IN, Pin.PULL_UP)
#button_4 = Pin(4,Pin.IN, Pin.PULL_UP)
#button_5 = Pin(5,Pin.IN, Pin.PULL_UP)
button_pulse = Pin(0,Pin.IN, Pin.PULL_UP)

program_1 = [(3000,50000),(110,5000)]
current_program = ""
def speed_1_program(pin):
    global ramping,running, program_1,current_program
    
    #pin.irq(trigger=0) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    current_program = program_1
    time.sleep(0.2)
    if pin.value():
        print("speed_1_program")
        if not ramping:
            ramping = True
            print("Ramping")
        time.sleep(0.2)
    #pin.irq(trigger=Pin.IRQ_FALLING, handler=speed_1_program) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    
    #running=False
    
print("Ready")
#button_pulse.irq(trigger=Pin.IRQ_FALLING, handler=speed_1_program) #Pin.IRQ_RISING|Pin.IRQ_FALLING

sampling_time = 500
ramping_time = 50
last_check = ticks_ms()
current_delay = 0

speed_1_program(button_pulse)
while True:
    time.sleep(0.1)
    led_pin.toggle()
    if ticks_diff(tmp := ticks_ms(), last_check) >= sampling_time:
        #print("ticks")
        if ramping: 
            print("spool tune")
            factor =int(sampling_time/ramping_time)
            pid.tune(P=-15.0, I=-0.01, D=0.0)
            for i in range(20,current_program[0][0],50):
                sm_rpm.exec('mov(isr,x)')
                sm_rpm.exec('push()')
                rps = (0x100000000 - sm_rpm.get()) & 0xffffffff
                #print(rps)
                sm_rpm.put(0) #reset counter
                
                pid.set_point = i
                pid.update()
                pid.update()
                time.sleep_ms(ramping_time)
                start_time = tmp
            ramping = False
            running=True
            print("Constant tune")
            factor = 1
            pid.tune(P=-3.0, I=-0.01, D=0.0)
            pid.update()
        #if running and ticks_diff(tmp := ticks_ms(), start_time) < current_program[0][1] :
        #    print("Run")
        #else:
        #    print("Stop")
        #    pid.set_point = 0
        #    pid.update()
        
        if running:
            if ticks_ms() - start_time < current_program[0][1]:
                factor = 1
                sm_rpm.exec('mov(isr,x)')
                sm_rpm.exec('push()')
                rps = (0x100000000 - sm_rpm.get()) & 0xffffffff
                #print(rps)
                sm_rpm.put(0) #reset counter
                
                pid.set_point =current_program[0][0]                
                pid.update()
                
            else :
                
                sm_triac.active(0)
                motor_out_pin.low()
            #button_pulse.irq(trigger=Pin.IRQ_FALLING, handler=lambda x:print("Stop!")) #Pin.IRQ_RISING|Pin.IRQ_FALLING
            
                
        
        
        last_check = tmp
    
    
    #print(sm_rpm.get())
    #counter = sm_rpm.get()
    #print(counter)
 

#from PWMCounter import PWMCounter

# Set PWM to output test signal
#pwm = PWM(Pin(0))
#pwm.duty_u16(1 << 15)
#pwm.freq(1000)

# Configure counter to count rising edges on GP15
#counter = PWMCounter(5, PWMCounter.EDGE_RISING)
# Set divisor to 1 (just in case)
#counter.set_div()
# Start counter
#counter.start()

# Set sampling time in ms
#sampling_time = 1000
#last_check = ticks_ms()

        

#    if ticks_diff(tmp := ticks_ms(), last_check) >= sampling_time:
        # Print calculated frequency in Hz - should show 1000 with default setup
        #print(counter.read_and_reset() / (sampling_time / 1000))
#        print(counter.read_and_reset())
#        last_check = tmp
    