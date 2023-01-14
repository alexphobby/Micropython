import time
from machine import Timer
from machine import Pin, ADC
from machine import I2C
from machine import PWM
import math
#import picosleep
import os


#******ALX IR*****
from my_remotes import remote_samsung
from my_remotes import remote_tiny
#from my_remotes import brightness_map

from ir_remote_read import ir_remote_read
#time.sleep(2)
ir_pin = Pin(2,Pin.IN) #,Pin.PULL_UP

debugmessage = False
remote_button = ""

sensed = False
menu_page = 0
timeout_minutes = 1
blink_times = 0

my_brightness_1 = 5*26
my_brightness_2 = 5*26
new_brightness_1 = 0
new_brightness_2 = 0


wait_up = 0.02
wait_down = 0.08
wait = wait_up

brightness_1 = 0
brightness_2 = 0


state = 1 # 1 = lights off, 2= lights on


time.sleep(2)

try:
    config_file = 'config.ini'
    file = open(config_file)
    config_content = file.read().splitlines()
    file.close()
    for item in config_content :
        setting,value = item.split('=')
        if (setting == 'my_brightness_1') :
            my_brightness_1 = int(value)
            print("done loading saved brightness: {}".format(my_brightness_1))
        if (setting == 'my_brightness_2') :
            my_brightness_2 = int(value)
            print("done loading saved brightness: {}".format(my_brightness_2))
    
except:
    pass

def ir_demo(remote,command,combo):
    #global debugmessage
    debugmessage = False
    if debugmessage:
        print(combo)

def ir_callback(remote,command,combo):
    #print(combo)
    global remote_button
    global debugmessage
    
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
    
    #if debugmessage:
    #    print(debugmessage)
    #    print("Button: {}   Cod: {}".format(remote_button,combo))
        
    pressed_button(remote_button)



def pressed_button(button):
    global pressedbutton
    global menu_page
    global timeout_minutes
    global blink_times
    global my_brightness_1
    global my_brightness_2
    
    #pressedbutton = button
    #Brightness
    print("menu: {}; Button: {}".format(menu_page,button))
    if (menu_page == 1 ):
        try:
            button=int(button)
            #print("change brightness")
            my_brightness_1 = button * 26
            print("Setting brightness to: {}".format(my_brightness_1))
            blink_times = button
            
            #try:
            config_file = 'config.ini'
            os.remove(config_file)
            file = open(config_file,"w")
            file.write("my_brightness_1={}".format(my_brightness_1))
            file.write("my_brightness_2={}".format(my_brightness_2))
            time.sleep(0.2)
            file.close()
                
            print("Done saving brightness_1: {}".format(my_brightness_1))
            print("Done saving brightness_2: {}".format(my_brightness_2))
                
            #except:
            #    pass

            timer_blink.init(period=3000, mode=Timer.ONE_SHOT, callback=blink)    
        except:
            pass
    
    
    if (menu_page == 2 ):
        try:
            button=int(button)
            #print("change brightness")
            my_brightness_2 = button * 26
            print("Setting brightness to: {}".format(my_brightness_2))
            blink_times = button
            
            #try:
            config_file = 'config.ini'
            os.remove(config_file)
            file = open(config_file,"w")
            file.write("my_brightness_1={}\n".format(my_brightness_1))
            file.write("my_brightness_2={}".format(my_brightness_2))
            time.sleep(0.2)
            file.close()
                
            print("Done saving brightness_1: {}".format(my_brightness_1))
            print("Done saving brightness_2: {}".format(my_brightness_2))
                
            #except:
            #    pass

            timer_blink.init(period=3000, mode=Timer.ONE_SHOT, callback=blink)    
        except:
            pass
    
        
        
        
    if (button == '*' ):
        menu_page = menu_page +1
        if (menu_page == 3):
            
            menu_page = 0
        
        if menu_page == 1:
            print("Set light level")
            pass
        
        
        blink_times = menu_page
        timer_blink.init(period=3000, mode=Timer.ONE_SHOT, callback=blink)
        
        print("Menu page: {}".format(menu_page))
    
    
    #Timeout minutes
    if (button == '#' ):
        timeout_minutes = timeout_minutes + 1
        if (timeout_minutes > 10):
            
            timeout_minutes = 1
        
        print("Timeout: {} minutes".format(timeout_minutes))
        blink_times = timeout_minutes
        timer_blink.init(period=3000, mode=Timer.ONE_SHOT, callback=blink)
    print("Pressed_button: {}".format(button))
    
    
# ir_remote_read(ir_pin,ir_callback, False)


def blink(timer):
    global blink_times
    print("blink start times: {}".format(blink_times))
    pwm_1.duty_u16(0)
    time.sleep(0.5)
    for i in range(blink_times):
        pwm_1.duty_u16(100)
        time.sleep(0.1)
        pwm_1.duty_u16(0)
        time.sleep(0.2)
    
    blink_times = 0


from brightness_map import brightness_map


debugmessage = True

#i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

time.sleep(0.5)



timer=Timer()
timer_blink=Timer()


pwm_1_pin = Pin(20,Pin.OUT)
pwm_1_pin.low()

pwm_1 = PWM(pwm_1_pin)
pwm_1.freq(1000)
pwm_1.duty_u16(0)

pwm_2_pin = Pin(21,Pin.OUT)
pwm_2_pin.low()

pwm_2 = PWM(pwm_2_pin)
pwm_2.freq(1000)
pwm_2.duty_u16(0)



#sensor_ana_pin = Pin(26,Pin.IN)
#sensor_ana = ADC(sensor_ana_pin)

sensor_dig_pin = Pin(16,Pin.IN, Pin.PULL_DOWN)


#set1_pin = Pin(14,Pin.IN, Pin.PULL_UP)
#set2_pin = Pin(15,Pin.IN, Pin.PULL_UP)
#self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._aquire) #Pin.IRQ_RISING|Pin.IRQ_FALLING



old_pwm = 0

on_threshold = 100

    

def led_off(*args):
    global state
    
    global my_brightness_1
    global my_brightness_2
    global new_brightness_1
    global new_brightness_2
    
    state = 1
    new_brightness_1 = 0
    new_brightness_2 = 0
    print("led_off")
    #set_brightness(0,0,0.02)

def led_on(*args):
    global my_brightness_1
    global my_brightness_2
    global new_brightness_1
    global new_brightness_2
    
    print("led on")
    
    new_brightness_1 = my_brightness_1
    new_brightness_2 = my_brightness_2
    #print("int, brightness_1: {}, brightness_2: {}".format(brightness_1,brightness_2))
    #set_brightness(my_brightness_1,my_brightness_2,0.02)
    


set=False
def disable_set(timer):
    global set
    set = False
    
    
#timer.init(period=3000, mode=Timer.ONE_TIME, callback=set_brightness)
# def set1(pin):
#     global set
#     pin.irq(trigger=0)
#     set = True
#     print("SET1: ".format(pin))
#     #time.sleep(0.1)
#     timer.init(period=3000, mode=Timer.ONE_SHOT, callback=lambda t:print("Welcome to Microcontrollerslab"))
#     
#     timer.init(period=3000, mode=Timer.ONE_SHOT, callback=disable_set)
#     pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING
# 
# 
# def set2(pin):
#     pin.irq(trigger=0)
#     print("SET2: ".format(pin))
#     #time.sleep(0.1)
#     pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING

#p2.irq(lambda pin: print("IRQ with flags:", pin.irq().flags()), Pin.IRQ_FALLING)


    
#set1_pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING
#set2_pin.irq(trigger=Pin.IRQ_FALLING, handler=set2) #Pin.IRQ_RISING|Pin.IRQ_FALLING

#sensor_dig_pin.irq(trigger=Pin.IRQ_RISING, handler=led_on)

def onSensed(timer):
    global sensed
    #global sensed_on
    #print("sensed irq")
    sensed = True
    
    
    
    #sensed_on= time.ticks_ms()

sensor_dig_pin.irq(trigger=Pin.IRQ_RISING, handler=onSensed)

last_run_time_states = 0
last_run_time_dim = 0
while True:

    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_states) >= int(100):
        last_run_time_states = tmp

        if (menu_page !=0 ):
            continue
        
        
        if state == 1:
            if not sensed:
                pass
                #print("state 1 and not sensed")
            else:
                #print("state 1 and sensed --> state2")
                state = 2
                sensed = False
            
            
        
        if state == 2:
            #print("state 2 --> state2 + led on + off timer")
            led_on()
            timer.init(period=timeout_minutes*10*1000, mode=Timer.ONE_SHOT, callback=led_off)
            state = 3
            
            
        if state == 3:
            if not sensed:
                #print("state 3 not sensed, skip")
                pass
            else:
                #print("state 3 sensed, new off timer")
                timer.init(period=timeout_minutes*10*1000, mode=Timer.ONE_SHOT, callback=led_off)
                sensed = False
        
        if state == 4:
            #print("state 4, dim to 0")
            led_off()
            state = 1



#    if (new_brightness_1 == brightness_1 or new_brightness_2 == brightness_2):
#        continue


    if new_brightness_1 != brightness_1 and time.ticks_diff(tmp := time.ticks_ms(), last_run_time_dim) >= int(wait*1000):
        last_run_time_dim = tmp
        #print(f"Dimming, new_brightness_1= {new_brightness_1} - brightness_1 = {brightness_1}")
        
        try:
            
            step_1 = int((new_brightness_1 - brightness_1)/abs(new_brightness_1 - brightness_1))
            wait = wait_up if step_1 > 0 else wait_down
        except:
            step_1 = 0
        
        try:
            step_2 = int((new_brightness_2 - brightness_2)/abs(new_brightness_2 - brightness_2))
            #step = step_up if step_1 > 0 else step_down
        except:
            step_2 = 0
            
        if new_brightness_1 == 0 and brightness_1 <= on_threshold:
            brightness_1 = 0
            brightness_2 = 0
            
        if new_brightness_1 >= on_threshold and brightness_1 < on_threshold:
            brightness_1 = on_threshold
            brightness_2 = on_threshold
        
        
        if (new_brightness_1 != brightness_1 and step_1 != 0):
            brightness_1 += step_1
            if brightness_1 <= on_threshold:
                pwm_1.duty_u16(0)
                #new_brightness_1 = 0
            else:
                pwm_1.duty_u16(brightness_map[brightness_1])
               
        if (new_brightness_2 != brightness_2 and step_2 != 0):
            brightness_2 += step_2
                
            if brightness_2 <= on_threshold:
                pwm_2.duty_u16(0)
                #new_brightness_2 = 0
            else:
                pwm_2.duty_u16(brightness_map[brightness_2])                        

        
        
    

        #else:
            #led_off()
        #print(brightness_1)
    
    #Analogic sensor
    #sensor_ana_value = sensor_ana.read_u16()
    #print("{} {}".format(sensor_ana_value,18000-sensor_dig_pin.value()*18000))
    #if (sensor_ana_value < 18000):
    
    #Digital sensor
        
    
        #print("Motion: {}".format(sensor_ana_value))
        #led_on()
        #timer.init(period=5*60*1000, mode=Timer.ONE_SHOT, callback=led_off)
        