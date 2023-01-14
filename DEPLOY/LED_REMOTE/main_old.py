#import machine
import time
from machine import Timer
from machine import Pin
#from machine import I2C
from machine import PWM
import math
#import picosleep

debug = True
#******PID********
#from pid import PID
#*****/PID********

#******BUTTONS****
# bt_touch1 = Pin(19,Pin.IN, Pin.PULL_DOWN)

#******/BUTTONS***


#******ALX IR*****
from my_remotes import remote_samsung
from my_remotes import remote_tiny
from my_remotes import brightness_map

from ir_remote_read import ir_remote_read
time.sleep(2)

#machine.freq(240000000)
#machine.freq(120000000)
machine.freq(20000000)


ir_pin = Pin(4,Pin.IN) #,Pin.PULL_UP
pwm_pin = Pin(5,Pin.OUT)
pwm_pin.low()

remote_button = ""
def ir_demo(remote,command,combo):
    global debug
    if debug:
        print(combo)

def ir_callback(remote,command,combo):
    #print(combo)
    global remote_button,debug
    print("try combo: {}".format(combo))
    
    if combo == "R":
        print("Repeat {}".format(remote_button))
    else:
        remote_button = ""
    try:
        remote_button = remote_samsung[combo]
        
    except:
        pass
        
    try:
        remote_button = remote_tiny[combo]
        
    except:
        pass
    
    if debug:
        print("Button: {}   Cod: {}".format(remote_button,combo))
        
    pressed_button(remote_button)

    
ir_remote_read(ir_pin,ir_callback, debug = debug)
#ir_remote_read(ir_pin,ir_demo)

#*****************

#def mymap(x,in_min=0,in_max=65535,out_min=0,out_max=100):
#    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#auto_pin = Pin(9)
#auto_pin.init(auto_pin.OUT,value = 0)


pwm_duty = 3000
old_brightness = 0
brightness = 0
desired = 200

auto_brightness = False
old_pwm = 0

pwm = PWM(pwm_pin)
pwm.freq(30000)
pwm.duty_u16(0)


ir_code = ""

last_remote_button = ""
last_remote_button_time = time.ticks_ms()


#print(str(brightness_map[1]))
#R = (65535 * math.log(1.2,10))/(math.log(65535,10))
#print(R)

def enable_auto_brightness(setting = True):
    global auto_brightness
    auto_brightness = setting
    if setting:
        desired = read_adc()
        auto_pin.high()
    else:
        auto_pin.low()
    

def change_duty(brightness,source):
    global old_brightness
    global old_pwm
    #global r
    #if source != "rotary":
    #    r.reset(brightness)
    #475 + int(pow (1.2, int(new_duty / R)) - 1)
    #print(brightness_map[old_brightness])
    #old_pwm = brightness_map[old_brightness]
    #print(brightness)
    if brightness > 119:
        brightness = 119
    if brightness < 0:
        brightness = 0

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

def pressed_button(button):
    global brightness
    global auto_brightness
    global desired
    global remote_button
    global last_remote_button
    global last_remote_button_time
    _button = button
    threshold_repeat = 300
    reject_repeat = ["*","#","ok"]
    #print(_button == last_remote_button)
    #print(_button in reject_repeat)
    
    
    if _button == last_remote_button and _button in reject_repeat and (time.ticks_ms() - last_remote_button_time) < threshold_repeat:
        #print("anti repeat")
        last_remote_button_time = time.ticks_ms()
        #print("break")
        return
    #print(_button,last_remote_button, (time.ticks_ms() - last_remote_button_time))
    if _button == "up":
        brightness += 5
                
    elif _button == "down" :
        brightness -= 5
    elif _button == "*":
        print("toggle brightness, initial status: {}".format(auto_brightness))
        last_remote_button_time = time.ticks_ms()
        last_remote_button = _button
        #if auto_brightness:
            #enable_auto_brightness(False)
            
        #else:
            #enable_auto_brightness(True)
        return
    else:
        try:
            directbutton = int(_button)
            if directbutton == 0:
                brightness = 0
            elif directbutton == 1:
                brightness = 10
            elif directbutton == 2:
                brightness = 20
            elif directbutton == 3:
                brightness = 30
            elif directbutton == 4:
                brightness = 40
            elif directbutton == 5:
                brightness = 50
            elif directbutton == 6:
                brightness = 70
            elif directbutton == 7:
                brightness = 90
            elif directbutton == 8:
                brightness = 100
            elif directbutton == 9:
                brightness = 119
                   
        except:
            pass
    #desired = read_adc()
    last_remote_button = _button
    last_remote_button_time = time.ticks_ms()
    #enable_auto_brightness(False)
    change_duty(brightness,"remote")




def print_output(message):
    global brightness
    global new_pwm
    global old_pwm
    global desired
    #print("adjx100:{};PWM:{};ADCx10:{};Desired:{}".format(int(message*100),old_pwm/100,old_adc,desired))
    #print("ADC: {}; Desired: {};Old_brightness: {}; Adjustment: {}".format(old_adc,desired,brightness,message))
    brightness = brightness + int(message)
    if brightness > 118:
        brightness = 118
    if brightness < 0:
        brightness = 0
    
    change_duty(brightness,"pid")
    time.sleep(0.05)
    
#pid = PID(read_adc,print_output,P=-3., I=-0.01, D=0.0)
#pid = PID(read_adc,print_output,P=-3.0, I=-0.01, D=0.0,debug = True)

#3800 med intensity
#3000 high intensity
#import micropython

#timer2 = Timer()
#timer2.init(period=100000, mode=Timer.PERIODIC, callback=lambda t:gc.collect())

#timer3 = Timer()
#timer3.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:test(1))

#time.sleep(2)

test = Pin(19,Pin.OUT)
test.on()
#test.value() = 0
while True:
    #adc.read_u16()         # read value, 0-65535 across voltage range 0.0v - 3.3v
    #conversion_factor = 3.3 * 6 / (65535) 

    #for i in range(100):
    #reading = adc.read_u16() #* conversion_factor
    #reading1 = adc1.read_u16() #* conversion_factor
    test.toggle()
    #picosleep.seconds(1)
    time.sleep(0.3)
    
    
