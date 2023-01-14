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

menu_page = 0
blink_times = 0

retries = 0
max_retries = 2
#Saved settings
timeout_minutes = 5
my_brightness_1 = 5*26
my_brightness_2 = 5*26
motion_threshold = 18000
config_file = 'config.ini'

state = 0

brightness_1 = 0
brightness_2 = 0


time.sleep(2)


def load_settings():
    global my_brightness_1
    global my_brightness_2
    global timeput_minutes
    global motion_threshold
    global retries
    global max_retries
    
    settings_to_load = 4
    print("Loading settings..")
    try:
        file = open(config_file)
    except Exception as err:
        print("Saved first settings")
        save_settings()
        
        return
    
    
    try:
        file = open(config_file)
        config_content = file.read().splitlines()
        file.close()
        for item in config_content :
            setting,value = item.split('=')
            if (setting == 'my_brightness_1') :
                my_brightness_1 = int(value)
                print("done loading saved brightness: {}".format(my_brightness_1))
                settings_to_load = settings_to_load - 1
            if (setting == 'my_brightness_2') :
                my_brightness_2 = int(value)
                print("done loading saved brightness: {}".format(my_brightness_2))
                settings_to_load = settings_to_load - 1
            if (setting == 'timeout_minutes') :
                timeout_minutes = int(value)
                print("done loading timeout: {}".format(timeout_minutes))
                settings_to_load = settings_to_load - 1
            if (setting == 'motion_threshold') :
                motion_threshold = int(value)
                print("done loading threshold: {}".format(motion_threshold))
                settings_to_load = settings_to_load - 1

        if (settings_to_load > 0):
            raise Exception("not all settings loades")
    except Exception as err:
        print(err)
        if (retries < max_retries):
            retries = retries + 1
            save_settings()
            load_settings()
        else:
            print("Max retries reached")
            
    print("Load complete")

def save_settings():
    global config_file
    global brightness_1
    global brightness_2
    global timeout_minutes
    global motion_threshold
    
    config_file = 'config.ini'
    print("Saving settings")
    try:
        os.remove(config_file)
    except Exception as err:
        print("eroare stergere fis: {}".format(err))
    file = open(config_file,"w")
    file.write("my_brightness_1={}\n".format(my_brightness_1))
    file.write("my_brightness_2={}\n".format(my_brightness_2))
    file.write("timeout_minutes={}\n".format(timeout_minutes))
    file.write("motion_threshold={}".format(motion_threshold))
    time.sleep(0.001)
    file.close()
                
    print("Done saving brightness_1: {}".format(my_brightness_1))
    print("Done saving brightness_2: {}".format(my_brightness_2))


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

print("start")
load_settings()

            
            
def pressed_button(button):
    global pressedbutton
    global menu_page
    global timeout_minutes
    global blink_times
    global my_brightness_1
    global my_brightness_2
    global changed_settings
    
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
            save_settings()
            
            
                
            #except:
            #    pass

            timer_blink.init(period=500, mode=Timer.ONE_SHOT, callback=blink)    
        except:
            pass
    
    
    if (menu_page == 2 ):
        try:
            button=int(button)
            #print("change brightness")
            my_brightness_2 = button * 26
            print("Setting brightness to: {}".format(my_brightness_2))
            blink_times = button
            save_settings()
            
            timer_blink.init(period=500, mode=Timer.ONE_SHOT, callback=blink)    
        except:
            pass
    
    
    if (menu_page == 3 ):
        try:
            button=int(button)
            #print("change threshold")
            threshold = 9000 + button * 1000
            print("Setting threshold to: {}".format(threshold))
            blink_times = button
            save_settings()
            timer_blink.init(period=500, mode=Timer.ONE_SHOT, callback=blink)    
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
        timer_blink.init(period=500, mode=Timer.ONE_SHOT, callback=blink)
        
        print("Menu page: {}".format(menu_page))
    
    
    #Timeout minutes
    if (button == '#' ):
        timeout_minutes = timeout_minutes + 1
        if (timeout_minutes > 10):
            
            timeout_minutes = 1
        
        print("Timeout: {} minutes".format(timeout_minutes))
        blink_times = timeout_minutes
        timer_blink.init(period=500, mode=Timer.ONE_SHOT, callback=blink)
    print("Pressed_button: {}".format(button))
    
    
ir_remote_read(ir_pin,ir_callback, False)


def blink(timer):
    global blink_times
    global my_brightness_1
    global my_brightness_2
    global state
    
    print("blink start times: {}".format(blink_times))
    pwm_1.duty_u16(0)
    time.sleep(0.5)
    for i in range(blink_times):
        pwm_1.duty_u16(100)
        time.sleep(0.1)
        pwm_1.duty_u16(0)
        time.sleep(0.2)
    
    blink_times = 0
    
    if (state == 1):
        led_on()


from brightness_map import brightness_map


debugmessage = True

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

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



sensor_ana_pin = Pin(26,Pin.IN)
sensor_ana = ADC(sensor_ana_pin)

sensor_dig_pin = Pin(16,Pin.IN, Pin.PULL_DOWN)


set1_pin = Pin(14,Pin.IN, Pin.PULL_UP)
set2_pin = Pin(15,Pin.IN, Pin.PULL_UP)
#self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._aquire) #Pin.IRQ_RISING|Pin.IRQ_FALLING



old_pwm = 0


def set_brightness(new_brightness_1,new_brightness_2,wait): #0:235
    
    global brightness_1
    global brightness_2
    global timeout_minutes
    #print("set_brightness")
    
    if (new_brightness_1 == brightness_1 and new_brightness_2 == brightness_2):
        print("Extend!")
        timer.init(period=timeout_minutes*60*1000, mode=Timer.ONE_SHOT, callback=led_off)
        return
    step_1 = int((new_brightness_1 - brightness_1)/abs(new_brightness_1 - brightness_1))
    step_2 = int((new_brightness_2 - brightness_2)/abs(new_brightness_2 - brightness_2))
    #print(step)
    
    
    while new_brightness_1 != brightness_1 or new_brightness_2 != brightness_2:
        if (new_brightness_1 != brightness_1):
            brightness_1 += step_1
            pwm_1.duty_u16(brightness_map[brightness_1])
        
        if (new_brightness_2 != brightness_2):
            brightness_2 += step_2
            pwm_2.duty_u16(brightness_map[brightness_2])
                
        time.sleep(wait/2)
        
        #if (step <= 0):
            #print(step)
            #sensor_ana_value = sensor_ana.read_u16()
            #if (sensor_ana_value < 18000):
            #    print("Led ON - Motion!")
            #    led_on()
            #    timer.init(period=timeout_minutes*60*1000, mode=Timer.ONE_SHOT, callback=led_off)
            #    break
        #print("old bright: {}; new bright: {}; Step: ; PWM: {}".format(brightness,new_brightness,brightness_map[brightness]))
        
        time.sleep(wait/2)
    
    
    print("Done!")
            
            
    
    #pwm.duty_u16(brightness)
    
    #old_pwm=brightness


def led_off(*args):
    global state
    state = 0
    set_brightness(0,0,0.2)

def led_on(*args):
    global my_brightness_1
    global my_brightness_2
    global state
    
    state = 1
    print("int, brightness_1: {}, brightness_2: {}".format(brightness_1,brightness_2))
    set_brightness(my_brightness_1,my_brightness_2,0.02)


set=False
def disable_set(timer):
    global set
    set = False
    
    
#timer.init(period=3000, mode=Timer.ONE_TIME, callback=set_brightness)
def set1(pin):
    global set
    pin.irq(trigger=0)
    set = True
    print("SET1: ".format(pin))
    #time.sleep(0.1)
    timer.init(period=3000, mode=Timer.ONE_SHOT, callback=lambda t:print("Welcome to Microcontrollerslab"))
    
    timer.init(period=3000, mode=Timer.ONE_SHOT, callback=disable_set)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING


def set2(pin):
    pin.irq(trigger=0)
    print("SET2: ".format(pin))
    #time.sleep(0.1)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING

#p2.irq(lambda pin: print("IRQ with flags:", pin.irq().flags()), Pin.IRQ_FALLING)


    
set1_pin.irq(trigger=Pin.IRQ_FALLING, handler=set1) #Pin.IRQ_RISING|Pin.IRQ_FALLING
set2_pin.irq(trigger=Pin.IRQ_FALLING, handler=set2) #Pin.IRQ_RISING|Pin.IRQ_FALLING

sensor_dig_pin.irq(trigger=Pin.IRQ_RISING, handler=led_on)


while True:
    time.sleep(0.1)

    #print(sensor_dig_pin.value())
    if (menu_page !=0 ):
        continue
    #print("no good")
    
    #Analogic sensor
    #sensor_ana_value = sensor_ana.read_u16()
    #print("{} {}".format(sensor_ana_value,18000-sensor_dig_pin.value()*18000))
    #if (sensor_ana_value < 18000):
    
    #Digital sensor
        
    
        #print("Motion: {}".format(sensor_ana_value))
        #led_on()
        #timer.init(period=5*60*1000, mode=Timer.ONE_SHOT, callback=led_off)
        