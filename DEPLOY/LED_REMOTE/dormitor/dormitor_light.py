import urequests

import machine
from machine import Pin,PWM
from machine import Timer
from machine import PWM
from machine import ADC

import time
import utime
import ntptime
import json

import sys
import ubinascii

import random

time.sleep(4)

machine_id = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
#sys.exit()
#machines = {"e6614103e763b337":"a36_cam_mica","e6614103e7739437":"a36_cam_medie"}
from dim import Dim
from brightness_map import brightness_map
from pid import PID






led_pin = 21
motion_pin = 5
ir_pin = 6
ambient_light_pin = 26

fade_time_ms=2000
dim = Dim(led_pin,16,0,236,0,230,fade_time_ms)

#light = machine.Pin(led_pin,machine.Pin.OUT)
#light_pwm = PWM(light)

#light_pwm.freq(5000)
#light_pwm.duty_u16(0)

#time.sleep(2)

from CONNECTWIFI import CONNECTWIFI
wifi = CONNECTWIFI()

debug = False #False


from MACHINES import MACHINES
machines = MACHINES()

print(f"This machine: {machines.guid}, {machines.device}")
topic_receive = machines.topic_receive
topic_send = machines.topic_send


lastMotion = 0

#NRF
from machine import SPI
from machine import Pin
time.sleep(0.2)

try: 
    from nrf24l01 import NRF24L01
    import ustruct as struct

    spi = SPI(1)
    csn = Pin(13)
    ce=Pin(12)
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    _RX_POLL_DELAY = const(15)
    _SLAVE_SEND_DELAY = const(10)
    pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

except:
    print("no nrf")
#led = Pin('LED',Pin.OUT)


#DS
try:
    import onewire,ds18x20
    ds_data = Pin(14)
    # create the onewire object
    ds = ds18x20.DS18X20(onewire.OneWire(ds_data))
    ds_id = ds.scan()[0]
    # print('found devices:', roms)

    # loop 10 times and print all temperatures
    ds.convert_temp()
    time.sleep_ms(750)
    ds.read_temp(ds_id)
except:
    print("no ds")

from HDC1080 import HDC1080

from machine import WDT

wdt_is_enabled = False
if machine.reset_cause() != 3: 
    wdt = WDT(timeout=8000)
    wdt_is_enabled = True
    wdt.feed()

time.sleep(0.2)


from my_remotes import remote_samsung
from my_remotes import remote_tiny
from my_remotes import brightness_map

from ir_remote_read import ir_remote_read
print("IR sensor library init")
ir_pin = Pin(ir_pin,Pin.IN) #,Pin.PULL_UP

last_remote_button = ""
last_remote_button_time = time.ticks_ms()

def pressed_button(button):
    global brightness
    global auto_brightness
    global desired
    global remote_button
    global last_remote_button
    global last_remote_button_time
    global dim
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
                brightness = 35
            elif directbutton == 2:
                brightness = 50
            elif directbutton == 3:
                brightness = 65
            elif directbutton == 4:
                brightness = 80
            elif directbutton == 5:
                brightness = 95
            elif directbutton == 6:
                brightness = 100
            elif directbutton == 7:
                brightness = 108
            elif directbutton == 8:
                brightness = 112
            elif directbutton == 9:
                brightness = 115
                   
        except:
            pass
    #desired = read_adc()
    last_remote_button = _button
    last_remote_button_time = time.ticks_ms()
    #enable_auto_brightness(False)
    #light_pwm.duty_u16(brightness_map[brightness])
    setAutoBrightness("false")
    time.sleep(0.1)
    dim.setReqIndex1(brightness)
    
    #change_duty(brightness,"remote")



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
    print("Button: {}   Cod: {}".format(remote_button,combo))
    
    if debug:
        print("Button: {}   Cod: {}".format(remote_button,combo))
        
    pressed_button(remote_button)

    
ir_remote_read(ir_pin,ir_callback, debug = debug)
print("IR sensor listening")

try:
    i2c = machine.I2C(0,scl=Pin(1),sda=Pin(0))
except:
    print("no i2c")


try:
    hdc1080 = HDC1080(i2c)
    print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
    print(f"Humidity: {int(hdc1080.read_humidity())}")
    #print(f"Humidity: {int(hdc1080.read_humidity())}")


except:
    print("no humidity")
    
#print("ok")
#sys.exit()

try:
    from BH1750 import BH1750
    bh1750 = BH1750(i2c)

except:
    print("no light sensor")




def read_light():
    try:
        read_1 = round(bh1750.luminance_fast(bh1750.CONT_HIRES_2),1)
        #print(read_1)
        #time.sleep_ms(10)
        #read_2 = round(bh1750.luminance(bh1750.CONT_HIRES_2),1)
        #time.sleep_ms(50)
        #read_3 = round(bh1750.luminance(bh1750.CONT_HIRES_2),1)
        return read_1
        #return int((read_1+read_2+read_3)*10/3)
    
    except:
        return -1

ambient_light = read_light()
print(f"Lux: {ambient_light}")

def pid_output(message):
    global timer_pid,pid,dim
    if abs(message) == 0:
        return
    print(message)
    _requestedIndex = dim.index1 + message
    if _requestedIndex < dim.max1 and _requestedIndex > dim.min1 :
        dim.setReqIndex1(dim.index1 + message)
        print(f"Dimming message:{message}, setReqIndex1 = {dim.index1}")
    else:
        print("Out of range, new setpoint")
        pid.set_point = read_light()
    
    
    return
        
def update_pid(timer):
    global pid
    timer.deinit()
    #print("start")
    pid.update()
    timer.init(period=100, mode=Timer.PERIODIC, callback = update_pid)
    #print("end")


from micropython import const  
pid = PID(read_light,pid_output,_P=const(2.0), _I=const(0.01), _D=const(0.0),debug = False)

timer_pid = Timer()
#timer_pid.init(period=50, mode=Timer.PERIODIC, callback = update_pid)



def read_temperature():
    try:
        return round(hdc1080.read_temperature(celsius=True),1)
    except:
        return -1

def read_humidity():
    try:
        return round(hdc1080.read_humidity())
    except:
        return -1

def read_dim():
    global dim
    #print(f"read_dim: pwm {dim.pwm_1.duty_u16()}")
    #print(f"read_dim: index {dim.reqIndex1 * 100 / 200}")
    return round(dim.reqIndex1 * 100 / 200)

#ds_pwr = Pin(15,Pin.OUT)
#ds_pwr.on()
time.sleep(0.1)


#for rom in roms:

#for i in range(10):
#    print(ds.read_temp(ds_id), end=' ')
#    time.sleep(1)


#res = urequests.get("https://google.com")
result = False
while result == False:
    try:
        res = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest")
        result = True
    except:
        print("err")
        
print("-----------")
#print(res.json()["unixtime"])

import ujson
unixtime = int(res.json()["unixtime"])
UTC_OFFSET = int(res.json()["utc_offset"][2:3])

adjustedunixtime = int(unixtime + UTC_OFFSET*60*60)
#print(f"Got time: {res.json()["unixtime"]}")
tm = time.localtime(adjustedunixtime)
machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
print(unixtime)
print(adjustedunixtime)
print(time.localtime())
print(f"Time is: {time.localtime()[3]}:{time.localtime()[4]}")
print("-----------")

last_run_time_send = 0
last_run_time_receive = 0


from mqtt import MQTTClient

def mqttClient(ssl_enabled = False,name="pico"):
    client = MQTTClient(client_id=b"" + name,
    server=b"fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud",
    port=8883,
    user=b"apanoiu",
    password=b"Mqtt741852",
    keepalive=3600,
    ssl=ssl_enabled,
    ssl_params={'server_hostname':'fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud'}
    )

    #client.connect()
    return client

def publish(topic_send, value):
    global client
    #print(topic)
    #print(f"Sending to {topic_send} Message: {value}")
    client.publish(topic_send, value)
    #print("publish Done")

def sendTemperature(sender):
    global topic_send,machines
    
    print(f"sendTemperature function called by {sender}")
    #publish(topic_send, f"name:{machines.name}")
    publish(topic_send, f"temperature:{read_temperature()}")
    publish(topic_send, f"humidity:{read_humidity()}")
    publish(topic_send, f"ambient:{read_light()}")
    publish(topic_send, f"dim:{read_dim()}")

autoBrightness = False



def setAutoBrightness(strValue):
    global autoBrightness, topic_send, pid, timer_pid
    
    
    
    print(f"setAutoBrightness = {strValue}")
    if strValue == "true":
        autoBrightness = True
        _setpoint = read_light()
        pid.set_point = _setpoint
        print(f"Dim setpoint = {_setpoint}")
        timer_pid.init(period=100, mode=Timer.PERIODIC, callback = update_pid)
        #pid.update()
    else:
        autoBrightness = False
        timer_pid.deinit()
    
    discovery("setAutobrightness")

def discovery(sender):
    global topic_send,machines,lastMotion,autoBrightness
    print(f"Discovery function called by {sender}")
    temperature = read_temperature()
    humidity = read_humidity()
    ambient = read_light()
    dim = read_dim()
    output = {"devicename":str(machines.device),"roomname":str(machines.name),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(ambient),"dim":str(dim),"lastmotion":lastMotion,"autobrightness":autoBrightness}
    
    #output = json.loads()
    #publish(topic_send, f"device:{machines.device}")
    #publish(topic_send, f"name:{machines.name}")
    #if (time.time() - lastMotion ) / 60 < 5:
    #publish(topic_send, f"lastmotion:{lastMotion}")
    #sendTemperature("Discovery")
    publish(topic_send, f"jsonDiscovery:{output}")
    print(f"jsonDiscovery:{output}")

def sub_cb(topic, msg):
    global light,last_run_time_send,light_pwm,timer_pid #,topic
    
    
    print(f"Topic: {topic}; Mesaj: {msg}")
    
    
    
    if topic_receive == bytearray(topic,'UTF-8'):
        print("Matched topic")
        #print("Lights")
        if msg == b'true':
            light.on()
            print("Lights ON")
        elif msg == b'false':
            light.off()
            print("Lights OFF")
            #publish('picow/frompico', f"Received:{msg}")
        elif msg == b'discovery':
            print("discovery")
            locals()[msg.decode()]("mqtt")
        elif msg == b'sendTemperature':
            #last_run_time_send = 0
            locals()[msg.decode()]("mqtt")
            
        #elif: msg.contains
        else:
            #try:
            if True:
                command,strValue = msg.decode().split(':')
                print(f"Command: {command}, Value: {strValue}")
                if command == "lights":
                    intValue = int(strValue)
                    timer_pid.deinit()
                    setAutoBrightness("false")
                    dim.setReqIndex1(round(intValue*200/100))
                    #print(f"Command: {command}, Value: {strValue}, index: {round(value*200/100)}")                
                if command == "setAutoBrightness":
                    print("setAutoBrightness")
                    locals()[command](strValue)
                    
                
                
                #light_pwm.duty_u16(round(value*65534/100))
                
                #val = int(msg)
            try:
                pass
            except:# ex as Exception:
                #pass
                #print("Error parsing, {ex}")
                print("Err")

    elif str(topic)[str(topic).find('/')+1:str(topic).find('/')+2] == '*' and str(topic)[2:str(topic).find('/')] == str(topic_receive)[0:str(topic_receive).find('/')]:
        print("broadcast")
        try:
            locals()[msg.decode()]("mqtt")
        except:
            print(f"Cannot decode function name: {msg}")
    else:
        print(f"Other {topic}: {str(topic)[str(topic).find('/')+1:str(topic).find('/')+2]}")
 
print("Init MQTT")
try:
    client = mqttClient(True,machines.device)
    client.set_callback(sub_cb)
    client.connect()

    client.subscribe(topic = topic_receive)
    client.subscribe(topic = "to/#")
    print(f"Subscribed to: {topic_receive}")

except:
    print("err mqtt")
#client.subscribe(topic = "picow/lights")

import struct
import random


#Update time from NTP
if wdt_is_enabled:
    wdt.feed()

#import NTP
#from NTP import ro_time_epoch

try:
            
    client.ping()
    #sendTemperature("Init")
    discovery("Init")
except Exception as ex:
    print(f"Error sending to MQ: {ex}")
    client.connect()





adc = ADC(ambient_light_pin)



#saved settings:
file = open("config.py", "r")
settings = file.read()
settings_dict = json.loads(settings)
humidity_setpoint = int(settings_dict["humidity_setpoint"])

dimSetPoint = int(adc.read_u16()* 233 / 65534)

#analogReadings = []
analogReading = 0

def analogReadings(self):
    global analogReading,motion
    average = 0
    analogReadings = []
    if motion.value() == 1:
        return

    for i in range(20):
        analogReadings.append(int(adc.read_u16()* 233 / 65534))
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


#led = Pin(25,Pin.OUT)
led = Pin('LED',Pin.OUT)
#led12 = Pin(15,Pin.OUT)
#led12.on()

motion = Pin(motion_pin, Pin.IN,Pin.PULL_DOWN)

timer = Timer()
timer_blink = Timer()
timer_check_messages = Timer()




#timer_test.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:timerTest)   # Timer.ONE_SHOT . Period in m

def blinkOnboardLed(timer):
    global led
    led.toggle()
    #if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:

timer_blink.init(period=1000, mode=Timer.PERIODIC, callback = blinkOnboardLed)

time.sleep(0.2)

def dimToOff(timer):
    global dim
    dim.dimToOff()

   

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
timer.init(period=1000, mode=Timer.ONE_SHOT, callback=analogReadings)   # Timer.ONE_SHOT . Period in m

timer_check_messages.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:client.check_msg())   # Timer.ONE_SHOT . Period in m

def motion_sensed(pin):
    global lastMotion
    pin.irq(trigger=0)
    lastMotion = time.time()
    timer.init(period=10*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)
    print("motion")
    #time.sleep(5)
    pin.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)

motion.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)


while True:
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_receive) >= 1000:
        last_run_time_receive = tmp
        if wdt_is_enabled:
            wdt.feed()
        #received = client.check_msg()

    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 300000:
        last_run_time_send = tmp
        try:
            
            client.ping()
            #publish('fromCMica', f"dt:{str(round(ds.read_temp(ds_id),1 ) )}")
            #publish('fromCMica', f"t:{read_temperature()}")
            #publish('fromCMica', f"h:{read_humidity()}")
            #publish('fromCMica', f"l:{read_light()}")
            #sendTemperature("300s loop")
            
        except Exception as ex:
            print(f"Error sending to MQ: {ex}")
            client.connect()

