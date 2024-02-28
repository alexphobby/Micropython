import urequests
import machine
from machine import Pin,PWM,Timer,ADC,time_pulse_us

import time
import utime
import ntptime
import json
import asyncio

import sys
import ubinascii
from MACHINES import MACHINES
my_machine = MACHINES()
#from CONNECTWIFI import CONNECTWIFI
#wifi = CONNECTWIFI()
from i2c_init import *

from WEATHER import *
from NTP import *

from neopixel_util import *

from asyncio import Event
from Queue import Queue
queue = Queue(5)
event_wifi_connected = Event()
event_mq_connected = Event()
event_weather_updated = Event()
event_sleep_ready = Event()
event_request_ready = Event()
event_request_ready.set()
event_ntp_updated = Event()

from CONNECTWIFI_AS import *
wifi = CONNECTWIFI_AS(event_wifi_connected,my_machine.device)
ntp = NTP(wifi.wlan,event_wifi_connected,event_request_ready,event_ntp_updated)

#print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
#weather = WEATHER(event_wifi_connected,event_weather_updated,event_request_ready,event_sleep_ready)

dim_value = 0
def dim(strValue):
    global dim_value
    #dim_value = int(float(strValue)*10.23)
    my_print(f"Dim to: {strValue}")
    dimmer.dimToPercent(int(strValue))


import random
#sys.exit()
#machines = {"e6614103e763b337":"a36_cam_mica","e6614103e7739437":"a36_cam_medie"}
from dim import Dim
from brightness_map_1024 import brightness_map_1024 as brightness_map
from pid import PID

led_pin = 20

motion_pin = 5
ir_pin = 16
ambient_light_pin = 26

fade_time_ms=2000
dimmer = Dim(led_pin,fade_time_ms = fade_time_ms)

#light = machine.Pin(led_pin,machine.Pin.OUT)
#light_pwm = PWM(light)

#light_pwm.freq(5000)
#light_pwm.duty_u16(0)

#time.sleep(2)



debug = False #False




print(f"This machine: {my_machine.guid}, {my_machine.device}")
topic_receive = my_machine.topic_receive
topic_send = my_machine.topic_send


lastMotion = 0

from machine import Pin
time.sleep(0.2)

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


from machine import WDT

#wdt_is_enabled = False
#if machine.reset_cause() != 3: 
#    wdt = WDT(timeout=8000)
    #wdt_is_enabled = True
    #wdt.feed()

time.sleep(0.2)


from my_remotes import remote_samsung
from my_remotes import remote_tiny

from ir_remote_read import ir_remote_read
print("IR sensor library init")
ir_pin = Pin(ir_pin,Pin.IN) #,Pin.PULL_UP

last_remote_button = ""
remote_button = ""
last_remote_button_time = time.ticks_ms()

async def mqtt_send_temp(client,event_wifi_connected,event_mq_connected,on_demand = False):
    global event_request_ready
    my_print(f"mqtt_send_temp, on demand= {on_demand}")
    if on_demand:
        if not event_mq_connected.state:
            my_print("Cannot send, not connected to mq")
            return
        try:
            
            my_print(f"Send on demand message on {my_machine.topic_send}")
            _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(light_sensor.light()),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0} #"lastmotion":f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}'
            event_request_ready.clear()
            #my_print("ping")
            #client.ping()
            await asyncio.sleep_ms(100)
            my_print(f"publish jsonDiscovery:{_output}")
            client.publish(my_machine.topic_send, f'jsonDiscovery:{_output}', qos = 0,retain=False)
            my_print(f"published jsonDiscovery:{_output}")
            await asyncio.sleep_ms(50)
            event_request_ready.set()
            _output = None
            event_request_ready.set()
            #await asyncio.sleep(5)
            #lightsleep(10000)
            return
        except Exception as ex:
            my_print(f"mqtt_send error: {ex}")
            event_mq_connected.clear()
        return
        my_print("should not run")
    else:
        while True: #Do not run
            await event_wifi_connected.wait()
            await event_mq_connected.wait()
            await event_request_ready.wait()
            try:
                my_print(f"Send mqtt message on {my_machine.topic_send}")
                _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0}
                #client.ping()
                await asyncio.sleep_ms(100)
                client.publish(my_machine.topic_send, f'jsonDiscovery:{_output}', qos = 0,retain=False)
                await asyncio.sleep_ms(50)
                _output = None
                event_request_ready.set()
            except Exception as ex:
                my_print(f"mqtt_send error: {ex}")
                event_mq_connected.clear()
            await asyncio.sleep(30)



async def process_queue(queue):
    global client,event_wifi_connected,event_mq_connected
    my_print("MQ process_queue initialised")
    while True:
        _msg = await queue.get()
        event_sleep_ready.clear()
        my_print(f"Queue msg: {_msg}")
        led("blue")
        await asyncio.sleep_ms(100)
        led("off")

        if _msg == "discovery":
            my_print("Send discovery result")
            await mqtt_send_temp(client,event_wifi_connected,event_mq_connected,True)
        
        elif _msg == "update" and topic == my_machine.topic_receive:
            my_print("Update from GitHub")
            
            #gc.collect
            import update
            update.update()
        elif ":" in _msg:
            try:
                _command,_strValue = _msg.split(':')
                my_print(f"MQ Command Run if available: {_command}, param: {_strValue}")
                if _command in locals():
                    locals()[_command](_strValue)
            except Exception as ex:
                my_print(f"Error unpacking or running: {_msg}, {ex}")

        else:
            my_print(f"Unknown command: {_msg}")
        await asyncio.sleep(0)
        event_sleep_ready.set()

        



def setAutoBrightness(strValue):
    global autoBrightness, topic_send, pid, timer_pid
    
    
    
    print(f"setAutoBrightness = {strValue}")
    if strValue == "true":
        autoBrightness = True
        _setpoint = read_light()
        pid.set_point = _setpoint
        print(f"Dim setpoint = {_setpoint}")
        #timer_pid.init(period=100, mode=Timer.PERIODIC, callback = update_pid)
        #pid.update()
    else:
        autoBrightness = False
        #timer_pid.deinit()
    #time.sleep(2)
    #discovery("setAutobrightness")



brightness = 0
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
            print(f"DirectButton= {directbutton}")
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
                
            dimmer.dimToPercent(directbutton*11)   
            
        except:
            pass
    #desired = read_adc()
    last_remote_button = _button
    last_remote_button_time = time.ticks_ms()
    #enable_auto_brightness(False)
    #light_pwm.duty_u16(brightness_map[brightness])
    setAutoBrightness("false")
    time.sleep(0.1)
    #dim.setReqIndex1(brightness)
    
    
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
    if _requestedIndex < dim.max1 and _requestedIndex > dim.min1 : #in range
        dim.setReqIndex1(dim.index1 + message)
        #print(f"Dimming message:{message}, setReqIndex1 = {dim.index1}")
    elif _requestedIndex > dim.max1:
        dim.setReqIndex1(dim.max1)
    elif _requestedIndex < dim.min1:
        dim.setReqIndex1(dim.min1)
    
        #print("Out of range, new setpoint")
        #pid.set_point = read_light()
    
    
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

timer_pid = Timer(0)
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

def pi_pico_ntp():
    result = False
    while result == False:
        try:
            res = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest")
            result = True
        except:
            print("err requests")
            
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


def my_print(message):
    print(message)


def mqttClient(ssl_enabled = False,name="pico"):
    client = MQTTQueue(client_id=b"" + my_machine.name,
    server=b"fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud",
    port=8883,
    user=b"apanoiu_devices",
    password=b"Mqtt741852",
    keepalive=50000,
    ssl=ssl_enabled #,
    #ssl_params={'server_hostname':'fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud'}
    )

    #client.connect()
    return client

def mqtt_cb(topic,msg):
    global queue,client,event_wifi_connected,event_mq_connected
    my_print(f"cb: {msg}")
    _msg = msg.decode()
    queue._put(_msg)
        

#from umqtt.simple import MQTTClient
from mqtt_queue import MQTTQueue
client = mqttClient(True,my_machine.device)
client.set_callback(mqtt_cb)



def publish(topic_send, value):
    global client
    #print(topic)
    #print(f"Sending to {topic_send} Message: {value}")
    client.publish(topic_send, value)
    #print("publish Done")

def sendTemperature(sender):
    global topic_send,my_machine
    
    print(f"sendTemperature function called by {sender}")
    #publish(topic_send, f"name:{my_machine.name}")
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
    #time.sleep(2)
    #discovery("setAutobrightness")

def discovery(sender):
    global topic_send,my_machine,lastMotion,autoBrightness
    print(f"Discovery function called by {sender}")
    temperature = read_temperature()
    humidity = read_humidity()
    ambient = read_light()
    dim = read_dim()
    output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(ambient),"dim":str(dim),"lastmotion":lastMotion,"autobrightness":autoBrightness}
    #_output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(light_sensor.light()),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0} #"lastmotion":f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}'
    
    #output = json.loads()
    #publish(topic_send, f"device:{my_machine.device}")
    #publish(topic_send, f"name:{my_machine.name}")
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
                    discovery("setAutobrightness")
                if command == "dim":
                    intValue = int(strValue)
                    timer_pid.deinit()
                    setAutoBrightness("false")
                    dim.setReqIndex1(round(intValue*200/100))
                    
                
                
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
 

import struct
import random


#Update time from NTP
#if wdt_is_enabled:
#    wdt.feed()

#import NTP
#from NTP import ro_time_epoch





#adc = ADC(ambient_light_pin)



#saved settings:
#file = open("config.py", "r")
#settings = file.read()
#settings_dict = json.loads(settings)
#humidity_setpoint = int(settings_dict["humidity_setpoint"])

#dimSetPoint = int(adc.read_u16()* 233 / 65534)


#pwm_pin = Pin(15,Pin.OUT)
#pwm_pin.low()

#pwm = PWM(pwm_pin)
#pwm.freq(30000)
#pwm.duty_u16(0)


#led = Pin(25,Pin.OUT)
#led = Pin('LED',Pin.OUT)
#led12 = Pin(15,Pin.OUT)
#led12.on()

motion = Pin(motion_pin, Pin.IN,Pin.PULL_DOWN)

#timer = Timer()
#timer_blink = Timer()
#timer_check_messages = Timer()

#timer_test.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:timerTest)   # Timer.ONE_SHOT . Period in m

def blinkOnboardLed(timer):
    #global led
    #led.toggle()
    #if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:
    pass



#timer_blink.init(period=1000, mode=Timer.PERIODIC, callback = blinkOnboardLed)

time.sleep(0.2)

def dimToOff(timer):
    global dim
    dim.dimToOff()

   


motionOccurances = 0
_MOTIONTHRESHOLDSECONDS = const(2)

def motion_sensed(pin):
    global lastMotion,motionOccurances
    pin.irq(trigger=0)
    
    if time.time() - lastMotion < _MOTIONTHRESHOLDSECONDS:
        
        #timer.init(period=10*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)
        print("motion")
    
    #time.sleep(5)
    lastMotion = time.time()
    pin.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)

motion.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)


async def wifi_connection_check(wifi):
    global event_mq_connected,event_wifi_connected
    while True:
        my_print(f"called wifi connection check, wifi: {wifi.is_connected()}, MQ event:{event_mq_connected.state}  - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
        if wifi.is_connected():
            if event_wifi_connected.state:
                pass
            else:
                event_wifi_connected.set()
        else:
            my_print("Wifi not connected, clear wifi and mq events")
            event_mq_connected.clear()
            event_wifi_connected.clear()
                
        await asyncio.sleep(30)


async def mq_connection_check(event_wifi_connected,event_mq_connected):
    while True:
        #my_print(f"mq_connection_check, event_mq_connected.status={event_mq_connected.state} ")
        await event_wifi_connected.wait()
        await event_request_ready.wait()
        gc.collect()
        if not event_mq_connected.state:
            my_print("mq_connection_check call connect")
            await asyncio.sleep(1)
            
            await connect_mq(event_request_ready)
            
        #my_print(f"called mq connection check, wifi: {wifi.is_connected()}, MQ event:{event_mq_connected.state}  - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
        await asyncio.sleep(5)

async def connect_mq(event_request_ready): 
    if True: #while True:
        my_print(f"MQ connection - wait for wifi: {event_wifi_connected.state} and request: {event_request_ready.state}")
        await event_wifi_connected.wait()
        event_sleep_ready.clear()
        await asyncio.sleep(2)
        #my_print("MQ connection - wifi ok")
        try:
            #await event_request_ready.wait()
            my_print("MQ connection - connect")
            gc.collect()
            await asyncio.sleep(0)
            my_print(f"connect_mq - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
            event_request_ready.clear()
            client.connect()
            gc.collect()
            client.subscribe(topic = b"to/*")
            await asyncio.sleep(1)
            #gc.collect()
            #client.check_msg()
            await client.a_wait_msg(queue)
            client.subscribe(topic = my_machine.topic_receive)
            my_print("MQ connected and subscribed")
            event_mq_connected.set()
            event_sleep_ready.set()
            
        except Exception as ex:
            my_print(f"Err connecting to MQ, {ex}")
            event_mq_connected.clear()
        event_request_ready.set()
        await asyncio.sleep(2) 


async def mq_check_messages(client,time=5):
    global event_sleep_ready,wifi,event_wifi_connected,event_mq_connected,event_request_ready,queue
    counter = 0
    while True:
        #my_print(f"MQ Check msg wifi:{event_wifi_connected.state} mq:{event_mq_connected.state} req:{event_request_ready.state} ")
        await event_wifi_connected.wait()
        await event_mq_connected.wait()
        await event_request_ready.wait()
        event_sleep_ready.clear()

        #led.value(True)
        #await asyncio.sleep_ms(1)
        #led.value(False)

        try:
            #client.ping()
            #my_print("MQ Check msg")
            if wifi.is_connected():
                #await asyncio.sleep(0.2)
                #client.check_msg()
                if await client.a_wait_msg(queue):
                    await asyncio.sleep_ms(100)
                counter += 1
                if counter%30 == 0:
                    print("send ping")
                    client.ping()
                
                print(counter)
                #lightsleep(1000)
                #my_print("client checked msg")
                
        except Exception as ex:
            my_print(f"MQ Error on ping, event_mq_connected.clear() Err:{ex}")
            event_mq_connected.clear()
            event_request_ready.set()
            await asyncio.sleep(2)

        event_request_ready.set()
        
        await asyncio.sleep(time)
        #await asyncio.sleep(1)
        event_sleep_ready.set()

read_pulses = []
pulse_in = 0
old_pulse_in = 0
event_matter = Event()
pwm_in = Pin(4,Pin.IN)

async def read_pulse_in():
    global read_pulses,pulse_in,old_pulse_in
    while True:
        await asyncio.sleep_ms(1000)
        #machine.time_pulse_us(pwm_in,1,10000)
        #read_pulses.append(round(machine.time_pulse_us(pwm_in,1,10000)/10))
        _first_pulse_in = machine.time_pulse_us(pwm_in,1,10000)
        _second_pulse_in = machine.time_pulse_us(pwm_in,1,10000)
        if _first_pulse_in != _second_pulse_in:
            continue
        if _second_pulse_in == -2:
            pulse_in = 0
        elif _second_pulse_in == -1:
            pulse_in = 100
        else:
            pulse_in = round(_second_pulse_in/10)
            
        if abs(pulse_in - old_pulse_in) > 2:
            print("Matter change")
            old_pulse_in = pulse_in
            event_matter.set()
        #if len(read_pulses) >5:
        #    read_pulses.pop(0) 
        #pulse_in = round(sum(read_pulses) / len(read_pulses))

async def print_pulse_in():
    await asyncio.sleep(5)
    while True:
        await event_matter.wait()
        event_matter.clear()
        print(f"async def read_pulse_in()={pulse_in}") # , pulses: {read_pulses[0]},{read_pulses[1]},{read_pulses[2]},{read_pulses[3]},{read_pulses[4]},{read_pulses[5]}")
        dimmer.dimToPercent(pulse_in)
        #await asyncio.sleep(1)
  
async def program_sleep(event_wifi_connected,event_mq_connected,event_sleep_ready):
    global led,led_value
    while True:
        await event_wifi_connected.wait()
        await event_mq_connected.wait()
        await event_sleep_ready.wait()
        
        machine.lightsleep(10000)
        event_sleep_ready.clear()
        led("red")
        await asyncio.sleep_ms(0)
        led("off")
        await asyncio.sleep_ms(100)
        
        



async def main():
    await wifi.check_and_connect()
    t_wifi_connection_check = asyncio.create_task(wifi_connection_check(wifi)) #not handled
    t_mq_connection_check = asyncio.create_task(mq_connection_check(event_wifi_connected,event_mq_connected))
    t_mq_check_messages = asyncio.create_task(mq_check_messages(client,2))
    t_program_sleep = asyncio.create_task(program_sleep(event_wifi_connected,event_mq_connected,event_sleep_ready))
    t_process_queue = asyncio.create_task(process_queue(queue))
    #t_read_pulse_in = asyncio.create_task(read_pulse_in())
    
    #t_print_pulse_in = asyncio.create_task(print_pulse_in())

    while True:
        await asyncio.sleep(10)
        gc.collect()
        
        if t_wifi_connection_check.done():
            t_wifi_connection_check = None
            t_wifi_connection_check = asyncio.create_task(wifi_connection_check(wifi))
        
        if t_process_queue.done():
            my_print("process_queue is done")
            t_process_queue = None
            t_process_queue = asyncio.create_task(process_queue(queue))
        
        if t_mq_connection_check.done():
            t_mq_connection_check = None
            t_mq_connection_check = asyncio.create_task(mq_connection_check(event_wifi_connected,event_mq_connected))

        if t_mq_check_messages.done():
            t_mq_check_messages = asyncio.create_task(mq_check_messages(client,2))
    
        if t_process_queue.done():
            t_process_queue = asyncio.create_task(process_queue(queue))

if True: #try:
    my_print("Async call main")
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
#except Exception as ex:
#    my_print(f"Catch: {ex}")

while True:
    time.sleep(1)
#finally:
#    my_print(f"finally: ")
#    asyncio.new_event_loop()




