#import machine
import time
from machine import Timer
from machine import Pin
from machine import I2C
from machine import PWM
import math


#******PID********
from pid import PID
#*****/PID********

#******BUTTONS****
bt_touch1 = Pin(17,Pin.IN, Pin.PULL_DOWN)
bt_1 = Pin(18,Pin.IN, Pin.PULL_UP)
bt_2 = Pin(19,Pin.IN, Pin.PULL_UP)
bt_3 = Pin(20,Pin.IN, Pin.PULL_UP)
bt_4 = Pin(21,Pin.IN, Pin.PULL_UP)

#******/BUTTONS***

#*******OLED******
import writer
import freesans20
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI
import struct
#i2c = I2C(0)   # default assignment: scl=Pin(9), sda=Pin(8)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

time.sleep(0.5)

oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

write_custom_font = writer.Writer(oled, freesans20)

#write_custom_font.set_textpos(oled,0,0)
#write_custom_font.printstring("Welcome! ")


oled.show()
def oled_print(text,line = 1, col=1, clear = False):
    if clear:
        oled.fill(0)

    write_custom_font.set_textpos(oled,line*21 -21,0)
    write_custom_font.printstring(text + "    ")
    oled.show()

oled_print("Welcome new")
#*******/OLED*****

#******SET-DATE***

date_menu = ["year","month","day"]
hour_menu = ["hour","minute"]
#menu_levels = [l1,l2,l3]
menu_level = 0
l1=0
l2=0
l3=0

i=0
year = 2021
month = 1
day = 1
hour= 8
minute=0

show_menu = True

def set_date(pin):
    global year
    global month
    global day
    global i
    i=0
    print("menu level: {}".format(menu_level))
    while menu_level == 0:
        print("set date, menu = {}, i= {}".format(show_menu,i))
        oled_print(date_menu[i],line=1,clear=True)
        oled_print(str(year+i),line=2,clear=False)
        
        time.sleep(0.5)
        

def menu_set(pin):
    global show_menu
    global i
    global j
    global menu_level
    
    pin.irq(trigger=0) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    print("menu")
    
    
    if show_menu:
        show_menu = not show_menu
        print("set date, menu = {}".format(show_menu))
        oled_print(date_menu[i],clear=True)
        pin.irq(trigger=Pin.IRQ_FALLING, handler=set_date) #Pin.IRQ_RISING|Pin.IRQ_FALLING
        return
    else:
        pass
        #menu_level +=1 
    print("menu2")
    if menu_level > 3:
        menu_level = 0
    if menu_level==1:
        #set_date()
        pass
        
    if menu_level ==2:
        pass
    if menu_level == 3:
        pass
    time.sleep(0.2)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=set_date) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    
    
def menu_plus(pin):
    global i
    pin.irq(trigger=0)
    print("++")
    
    i+=1
    time.sleep(0.2)
    oled_print(date_menu[i],clear=True)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=menu_plus)

def menu_minus(pin):
    global i
    pin.irq(trigger=0)
    print("--")
    i-=1
    time.sleep(0.2)
    oled_print(date_menu[i],clear=True)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=menu_minus)

bt_4.irq(trigger=Pin.IRQ_FALLING, handler=menu_set) #Pin.IRQ_RISING|Pin.IRQ_FALLING
#bt_3.irq(trigger=Pin.IRQ_FALLING, handler=menu_enter) #Pin.IRQ_RISING|Pin.IRQ_FALLING
bt_1.irq(trigger=Pin.IRQ_FALLING, handler=menu_plus) #Pin.IRQ_RISING|Pin.IRQ_FALLING
bt_2.irq(trigger=Pin.IRQ_FALLING, handler=menu_minus) #Pin.IRQ_RISING|Pin.IRQ_FALLING

while True:
    time.sleep(5)
    
#******/SET-DATE**

#******ALX IR*****
from my_remotes import remote_samsung
from my_remotes import remote_tiny

from ir_remote_read import ir_remote_read

ir_pin = Pin(16)

remote_button = ""
def ir_demo(remote,command,combo):
    print(combo)

def ir_callback(remote,command,combo):
    #print(combo)
    global remote_button
    try:
        remote_button = remote_samsung[combo]
    except:
    
        pass
    try:
        remote_button = remote_tiny[combo]
    except:
        pass
    #print("Button: {}   Cod: {}".format(remote_button,combo))
    pressed_button(remote_button)

    
ir_remote_read(ir_pin,ir_callback)
#ir_remote_read(ir_pin,ir_demo)

#*****************

led = Pin(10, Pin.OUT)                # LED

from rotary_irq import RotaryIRQ

r = RotaryIRQ(pin_num_clk=12, 
              pin_num_dt=13, 
              min_val=0, 
              max_val=139, 
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_BOUNDED,
              half_step = True)
              
rotary_old = r.value()




time.sleep(1)



def mymap(x,in_min=0,in_max=65535,out_min=0,out_max=100):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

auto_pin = Pin(9)
auto_pin.init(auto_pin.OUT,value = 0)

pwm_pin = Pin(8)
pwm_duty = 3000
old_brightness = 0
brightness = 0
desired = 200

auto_brightness = False
old_pwm = 0

pwm = PWM(pwm_pin)
pwm.freq(10000)
pwm.duty_u16(0)

ir_pin = Pin(16, Pin.IN)
ir_code = ""

last_remote_button = ""
last_remote_button_time = time.ticks_ms()


# 119 values
brightness_map = [0,461,
    481,
    502,
    524,
    546,
    570,
    595,
    620,
    647,
    675,
    705,
    735,
    767,
    800,
    835,
    871,
    909,
    948,
    989,
    1032,
    1077,
    1123,
    1172,
    1223,
    1276,
    1331,
    1388,
    1449,
    1511,
    1577,
    1645,
    1716,
    1790,
    1868,
    1948,
    2033,
    2121,
    2212,
    2308,
    2408,
    2512,
    2621,
    2734,
    2852,
    2976,
    3105,
    3239,
    3379,
    3525,
    3677,
    3837,
    4002,
    4176,
    4356,
    4545,
    4741,
    4946,
    5160,
    5383,
    5616,
    5859,
    6112,
    6376,
    6652,
    6940,
    7240,
    7553,
    7879,
    8220,
    8575,
    8946,
    9333,
    9737,
    10157,
    10597,
    11055,
    11533,
    12031,
    12552,
    13094,
    13660,
    14251,
    14867,
    15510,
    16180,
    16880,
    17610,
    18371,
    19165,
    19994,
    20858,
    21760,
    22701,
    23682,
    24706,
    25774,
    26889,
    28051,
    29264,
    30529,
    31849,
    33226,
    34662,
    36160,
    37724,
    39355,
    41056,
    42831,
    44683,
    46614,
    48629,
    50732,
    52925,
    55213,
    57600,
    60090,
    62688,
    65398,
    65535]
#print(str(brightness_map[1]))
#R = (65535 * math.log(1.2,10))/(math.log(65535,10))
#print(R)
machine.freq(250000000)
#machine.freq(12000000)

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
    global r
    if source != "rotary":
        r.reset(brightness)
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
        print("anti repeat")
        last_remote_button_time = time.ticks_ms()
        print("break")
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
        if auto_brightness:
            enable_auto_brightness(False)
            
        else:
            enable_auto_brightness(True)
        return
    else:
        try:
            directbutton = int(_button)
            if directbutton == 5:
                brightness = 50
            if directbutton == 0:
                brightness = 0
            if directbutton == 9:
                brightness = 119
                   
        except:
            pass
    desired = read_adc()
    last_remote_button = _button
    last_remote_button_time = time.ticks_ms()
    enable_auto_brightness(False)
    change_duty(brightness,"remote")


from machine import ADC

adc = ADC(26)     # create ADC object on ADC pin
adc1 = ADC(27)     # create ADC object on ADC pin
adjusted_reading = 0

old_adc = 0
def read_adc(min_adc=0,max_adc=1000):
    global old_adc
    new_adc = int(adc.read_u16()/10)
    if abs(new_adc - old_adc) > 5:
        time.sleep(0.1)
        new_adc = int(((adc.read_u16()/10) + new_adc) / 2)
        #old_adc = new_adc
    elif abs(new_adc - old_adc) >20:
        new_adc = int(((adc.read_u16()/10) + new_adc) / 2)
    if new_adc < min_adc:
        new_adc = min_adc
    if new_adc > max_adc:
        new_adc = max_adc
    
    #new_adc = mymap(new_adc,in_min=0,in_max=65535,out_min=0,out_max=100):
    
    #old_adc = mymap(new_adc,in_min=min_adc,in_max=max_adc
    old_adc = new_adc
    
    return old_adc

def read_adc1():
    return adc1.read_u16()
new_pwm = 0



def print_output(message):
    global brightness
    global new_pwm
    global old_pwm
    global old_adc
    global desired
    #print("adjx100:{};PWM:{};ADCx10:{};Desired:{}".format(int(message*100),old_pwm/100,old_adc,desired))
    print("ADC: {}; Desired: {};Old_brightness: {}; Adjustment: {}".format(old_adc,desired,brightness,message))
    brightness = brightness + int(message)
    if brightness > 118:
        brightness = 118
    if brightness < 0:
        brightness = 0
    
    change_duty(brightness,"pid")
    time.sleep(0.05)
    
#pid = PID(read_adc,print_output,P=-3., I=-0.01, D=0.0)
pid = PID(read_adc,print_output,P=-3.0, I=-0.01, D=0.0,debug = True)

#3800 med intensity
#3000 high intensity
#import micropython
def update_display(test):
    global brightness
    global old_adc
    read_adc()
    
    if True:
    #try:
        #timer3.deinit()
        write_custom_font.set_textpos(oled,0,0)
        
        write_custom_font.printstring("Set: {}        ".format(brightness))
        
        write_custom_font.set_textpos(oled,22,0)
        
        write_custom_font.printstring("Read: {}        ".format(1000 - old_adc))
        
        #micropython.mem_info
        #write_custom_font.set_textpos(oled,42,0)
        
        #write_custom_font.printstring("{}        ".format(micropython.mem_info()))
        
        oled.show()
    #except:
    #    print("ERR")
    #timer3.init(period=500, mode=Timer.PERIODIC, callback=update_display)
#    led.toggle()

#timer3 = Timer()
#timer3.init(period=1000, mode=Timer.PERIODIC, callback=update_display)
import gc

#timer2 = Timer()
#timer2.init(period=100000, mode=Timer.PERIODIC, callback=lambda t:gc.collect())

#timer3 = Timer()
#timer3.init(period=2000, mode=Timer.PERIODIC, callback=lambda t:test(1))




while True:
    #adc.read_u16()         # read value, 0-65535 across voltage range 0.0v - 3.3v
    #conversion_factor = 3.3 * 6 / (65535) 

    #for i in range(100):
    #reading = adc.read_u16() #* conversion_factor
    #reading1 = adc1.read_u16() #* conversion_factor
    
    
    rotary_new = r.value()
    
    update_display("test")
    #print("1:{};2:{}".format(adc.read_u16(),adc1.read_u16()))
    
    if rotary_new != brightness:
        print("Rotary " + str(rotary_new))
        enable_auto_brightness(False)
        time.sleep_ms(20)
        brightness = r.value()
        change_duty(brightness,"rotary")
        rotary_old = rotary_new
        
    if auto_brightness:
        pid.set_point = desired
        pid.update()
        time.sleep(0.5)
    else:
        #time.sleep(1)
        pass
    #print("s1: {};  s2: {}".format(reading,reading))    
    #print("Reading: {} - Adjusted: {}".format(reading,pid.output))
    time.sleep(0.3)
    

#***************
    
from nrf24l01 import NRF24L01
import nrf24l01

csn = Pin(9, mode=Pin.OUT, value=1)  # chip select not
ce  = Pin(8, mode=Pin.OUT, value=0)  # chip enable
btn = Pin(20, Pin.IN, Pin.PULL_DOWN)  # button press


led = Pin(10, Pin.OUT)                # LED
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

def setup():
    nrf = 0
    #nrf = NRF24L01(SPI(0), csn, ce, payload_size=4)
    #print("NRF OK")
    #time.sleep(2)
    while nrf == 0:
        try:
            nrf = NRF24L01(SPI(0), csn, ce, payload_size=4)
            print("NRF OK!!")
        except:
            print("No NRF ")
            time.sleep(0.8)
        
    #nrf.set_channel(1)
    nrf.set_power_speed(nrf24l01.POWER_1,nrf24l01.SPEED_250K)
    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    #led.value(0)
    return nrf

def nrf_action(button):
    global nrf
    global btn
    btn.irq(trigger=0)
    state = btn.value()
    time.sleep_ms(200)
    if state == btn.value():
        print("tx", state)
        nrf.stop_listening()
        try:
            nrf.send(struct.pack("i", state))
        except OSError:
            print('message lost')
            nrf.start_listening()
    #time.sleep_ms(100)
    btn.irq(trigger=Pin.IRQ_RISING, handler=nrf_action)

            
def demo(nrf):
    state = 0 
    while True:
        
        #print("loop")
        time.sleep(1)
        print("tx1", state)
        nrf.stop_listening()
        try:
            nrf.send(struct.pack("i", state))
        except OSError:
            print('message lost')
        nrf.start_listening()

        if state != btn.value():
            state = btn.value()
            led.value(state)
            
            print("tx", state)
            nrf.stop_listening()
            try:
                nrf.send(struct.pack("i", state))
            except OSError:
                print('message lost')
            nrf.start_listening()
            
        if nrf.any():
            buf = nrf.recv()
            got = struct.unpack("i", buf)[0]
            print("rx", got)
            led.value(got)

def auto_ack(nrf):
    nrf.reg_write(0x01, 0b11111000)  # enable auto-ack on all pipes

#nrf_int = Pin(20, machine.Pin.IN) #,machine.Pin.PULL_DOWN
btn.irq(trigger=Pin.IRQ_RISING, handler=nrf_action)



nrf = setup()
auto_ack(nrf)
#demo(nrf)
state = 11
while True:
    #print("loop")
    time.sleep(1)
    #print("txbreadboard", state)
    nrf.stop_listening()
    try:
        led.toggle()
        sent = nrf.send(struct.pack("i", state))
        state += 1
        
        write_custom_font.set_textpos(oled,0,0)
        write_custom_font.printstring("{} - {}    ".format(state,sent))
        oled.show()

        print("Sent {}".format(sent))
    except OSError:
        write_custom_font.set_textpos(oled,0,0)
        write_custom_font.printstring("Err    ")
        oled.show()

        print('message lost')
    nrf.start_listening()


#time.sleep(1)           # sleep for 1 second
#time.sleep_ms(500)      # sleep for 500 milliseconds
#time.sleep_us(10)       # sleep for 10 microseconds
#start = time.ticks_ms() # get millisecond counter
#delta = time.ticks_diff(time.ticks_ms(), start) # compute time difference

led = Pin(25, Pin.OUT)



import time
import radiofast
from config import master_config, slave_config, FromMaster, ToMaster

def test_master():
    m = radiofast.Master(master_config)
    send_msg = FromMaster()
    while True:
        rx_msg = m.exchange(send_msg)
        if rx_msg is not None:
            print(rx_msg.i0)
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring(str(rx_msg.i0)+ "        ")
        else:
            write_custom_font.printstring("Timeout     ")
            print('Timeout')
        send_msg.i0 += 1
        oled.show()
        time.sleep_ms(1000)

def test_slave():
    print("Slave")
    s = radiofast.Slave(slave_config)
    send_msg = ToMaster()
    while True:
        print("True")
        result = s.exchange(send_msg)       # Wait for master
        print("Wait")
        if result is not None:
            print('Message')
            print(result.i0)
            write_custom_font.set_textpos(oled,0,22)
            write_custom_font.printstring(str(result.i0)+ "        ")
            
        else:
            write_custom_font.set_textpos(oled,0,22)
            print('Timeout')
            write_custom_font.printstring("Timeout     ")
            
        send_msg.i0 += 1
        oled.show()


s = radiofast.Slave(slave_config)
send_msg = ToMaster()

def nrf_action(pin):
    global s
    
    nrf_int.irq(trigger=0)
    time.sleep_ms(100)
    result = s.exchange(send_msg)       # Wait for master
    if result is not None:
        print('Message')
        print(result.i0)
        write_custom_font.set_textpos(oled,0,22)
        write_custom_font.printstring(str(result.i0)+ "        ")
            
    else:
        write_custom_font.set_textpos(oled,0,22)
        print('Timeout')
        write_custom_font.printstring("Timeout     ")
        
    print("int")
    nrf_int.irq(trigger=Pin.IRQ_FALLING, handler=nrf_action)



nrf_int = Pin(16, machine.Pin.IN) #,machine.Pin.PULL_DOWN
nrf_int.irq(trigger=Pin.IRQ_FALLING, handler=nrf_action)

    #global led_dir
    #led_dir = led_dir * -1
    

print("Start slave")
#test_slave()
while True:
    time.sleep(1)
#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
timer.init(period=3000, mode=Timer.PERIODIC, callback=blink)


#import ssd1306

# using default address 0x3C
#i2c = I2C(sda=Pin(4), scl=Pin(5))
#lcd.init_i2c(scl=15,sda= 14, width = 128,height = 64, i2c = 1)
#display = ssd1306.SSD1306_I2C(128, 64, i2c)
#ssd1306.write

#display.text('Hello, World!', 0, 0, 8)

#write_custom_font = ssd1306.Write(display, arial)
#write_custom_font.text("Espresso IDE", 0, 0)

#display.show()





from machine import ADC

adc = ADC(26)     # create ADC object on ADC pin
#adc.read_u16()         # read value, 0-65535 across voltage range 0.0v - 3.3v
conversion_factor = 3.3 / (65535)
#for i in range(100):
reading = adc.read_u16() * conversion_factor
temp = int((27 - (reading - 0.706)/0.001721)*10) / 10
write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring("T= " + str(temp)+ "    ")
oled.show()
time.sleep(0.5)
    
#display.contrast(0)

        

