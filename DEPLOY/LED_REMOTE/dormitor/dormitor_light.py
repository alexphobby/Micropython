import time
time.sleep(3)
import machine
from machine import Pin,PWM,Timer,ADC,time_pulse_us,freq,TouchPad,sleep
#freq(160000000)

import utime
import ntptime
import json
import asyncio

import sys
import ubinascii
from MACHINES import MACHINES
my_machine = MACHINES()

from BUZZER import BUZZER

led = ""
led_2 = Pin(6,mode = Pin.OUT, value = 0)

led_wifi = Pin(9,mode = Pin.OUT, value = 0)
led_mq = Pin(10,mode = Pin.OUT, value = 0)
led_ir = Pin(11,mode = Pin.OUT, value = 0)

if "ESP32S3" in sys.implementation._machine:
    from neopixel_util import *
    led = NEOPIXEL_UTIL()
elif "ESP32C3" in sys.implementation._machine:
    led = Pin(25,Pin.OUT)
else:
    led = Pin('LED',Pin.OUT)
#from CONNECTWIFI import CONNECTWIFI
#wifi = CONNECTWIFI()
from i2c_init import *

print(oled_enabled)

from WEATHER import *
from NTP import *

from asyncio import Event
from Queue import Queue
queue = Queue(5)
ir_queue = Queue()
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
def getSeconds():
    return time.localtime()[1]*30*24*3600 + time.localtime()[2]*24*3600 + time.localtime()[3]*3600 + time.localtime()[4]*60 + time.localtime()[5]
def setSeconds():
    global last_motion
    last_motion = time.localtime()[1]*30*24*3600 + time.localtime()[2]*24*3600 + time.localtime()[3]*3600 + time.localtime()[4]*60 + time.localtime()[5]

async def blink(led,times = 1):
    for i in range(times - 1):
        led.on()
        await asyncio.sleep(0.05)
        led.off()
        await asyncio.sleep(0.05)
        
dim_value = 0
async def dim(strValue):
    global dim_value,event_request_ready,auto_start_percent
    #dim_value = int(float(strValue)*10.23)

    event_request_ready.clear()
    my_print(f"Dim to: {strValue}")
    await dimmer.dimToPercent(int(strValue))
    if auto_start:
        auto_start_percent = int(strValue)
    
    event_request_ready.set()


import random
#sys.exit()
#machines = {"e6614103e763b337":"a36_cam_mica","e6614103e7739437":"a36_cam_medie"}
from dim_as import Dim
from brightness_map_1024 import brightness_map_1024 as brightness_map
from pid import PID

led_pin = 38
ir_pin = 1
ambient_light_pin = 2
buzzer_pin = 17
buzzer = BUZZER(buzzer_pin,max_duty=20)
buzzer.buzz()

motion_pin = 5
motion = Pin(motion_pin, Pin.IN,Pin.PULL_DOWN)
touch_pin = 12
t = TouchPad(Pin(touch_pin))
sleep(1)
previous=t.read()

for i in range(10):
    current=t.read()
    if current-previous< 100:
        previous = int((previous + current)/2)

base = round(previous)
print(f'Base value: {base}')
t.config(base + 500)
def check_touch():
    if t.read() > base + 500:
        return True
    else:
        return False

def touch_sensed(pin):
    print("sensed")
    print(pin)

lastMotion = 0
last_motion = 0
motionOccurances = 0
_MOTIONTHRESHOLDSECONDS = const(2)
event_motion = Event()

def motion_sensed(pin):
    global lastMotion,motionOccurances
    #pin.irq(trigger=0)
    if event_motion.is_set():
        return
    
    event_motion.set()
    #if time.time() - lastMotion < _MOTIONTHRESHOLDSECONDS:
        
    #    timer.init(period=10*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)
    print("motion")
    
    #time.sleep(5)
    #lastMotion = time.time()
    #pin.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)

motion.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)


auto_start = False
auto_start_percent = 0

fade_time_ms=2000
dimmer = Dim(led_pin,fade_time_ms = fade_time_ms)

debug = False #False
debug_ir = False
print(f"This machine: {my_machine.guid}, {my_machine.device}")
topic_receive = my_machine.topic_receive
topic_send = my_machine.topic_send




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
ir_pin = Pin(ir_pin,Pin.IN,Pin.PULL_UP)
def ir_cb(button):
    my_print(f'button is {button}')
    if button == "up":
        #brightness += 5
        print("dim up")
        await dimmer.dimToPercent(99)

last_remote_button = ""
remote_button = ""
last_remote_button_time = time.ticks_ms()

async def mqtt_send_temp(client,event_wifi_connected,event_mq_connected,on_demand = False):
    global event_request_ready,dimmer,auto_start
    my_print(f"mqtt_send_temp, on demand= {on_demand}")
    if on_demand:
        if not event_mq_connected.state:
            my_print("Cannot send, not connected to mq")
            return
        try:
            
            #my_print(f"Send on demand message on {my_machine.topic_send}")
            _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(light_sensor.light()),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0,"motion": auto_start} #"lastmotion":f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}'
            event_request_ready.clear()
            #my_print("ping")
            #client.ping()
            await asyncio.sleep_ms(100)
            #my_print(f"publish jsonDiscovery:{_output}")
            #client.
            publish(my_machine.topic_send, f'jsonDiscovery:{_output}')
            #my_print(f"published jsonDiscovery:{_output}")
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
                _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0,"motion": auto_start}
                #client.ping()
                await asyncio.sleep_ms(100)
                #client.publish(my_machine.topic_send, f'jsonDiscovery:{_output}', qos = 0,retain=False)
                publish(my_machine.topic_send, f'jsonDiscovery:{_output}')
                await asyncio.sleep_ms(50)
                _output = None
                event_request_ready.set()
            except Exception as ex:
                my_print(f"mqtt_send error: {ex}")
                event_mq_connected.clear()
            await asyncio.sleep(30)


async def process_ir_queue(queue):
    global auto_start,auto_start_percent
    my_print("IR process_queue initialised")
    setSeconds()
    while True:
        _button = await queue.get()
        my_print(f"IR Queue msg: {_button}")
        await buzzer.buzz_as()
        await blink(led_ir,2)
        if _button == "up":
            await dimmer.dimToPercent(dimmer.getPercent() + 5)
        elif _button == "down" :
            await dimmer.dimToPercent(dimmer.getPercent() - 5)
        elif _button in ("*","menu"):
            auto_start = not auto_start
            my_print(f'pressed: {_button} - auto_start: {auto_start}')
        elif _button in ("#","exit"):
            print(f'pressed: {_button} - x')
        
        else:
            try:
                directbutton = int(_button)
                my_print(f"DirectButton= {directbutton}")
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
                    
                await dimmer.dimToPercent(directbutton*11)
            except Exception as ex:
                my_print(ex)

        if auto_start:
            auto_start_percent = dimmer.getPercent()
            my_print(f'auto_start: {auto_start} - Auto_start_percent: {auto_start_percent}')

            #await dimmer.dimToPercent(99)
            #await mqtt_send_temp(client,event_wifi_connected,event_mq_connected,True)


async def process_motion(event):
    global auto_start_percent
    motion_threshold = 15
    while True:
        await event.wait()
        setSeconds()
        #_current_motion = time.localtime()[1]*30*24*3600 + time.localtime()[2]*24*3600 + time.localtime()[3]*3600 + time.localtime()[4]*60 + time.localtime()[5]
        #print(f'process motion: {time.localtime()} -> {_current_motion} - last_motion: {last_motion}')
        if auto_start and dimmer.getPercent() == 0: #_current_motion - last_motion > motion_threshold:
            print(f"autostart, motion threshold passed set to {auto_start_percent}")
            await dimmer.dimToPercent(auto_start_percent)
        #last_motion = _current_motion
        await asyncio.sleep(10)
        event.clear()
    
async def process_queue(queue):
    global client,event_wifi_connected,event_mq_connected
    my_print("MQ process_queue initialised")
    while True:
        _msg = await queue.get()
        my_print(f"Queue msg: {_msg}")
        await blink(led_mq,3)
        if _msg == "discovery":
            my_print("Send discovery result")
            await mqtt_send_temp(client,event_wifi_connected,event_mq_connected,True)
        
        elif _msg == "update": # and topic == my_machine.topic_receive:
            my_print("Update from GitHub")
            
            #gc.collect
            import update
            try:
                update.update()
            except Exception as ex:
                print(f"Err updating: {ex}")
        elif ":" in _msg:
            try:
                _command,_strValue = _msg.split(':')
                my_print(f"MQ Command Run if available: {_command}, param: {_strValue}")
                if _command in locals():
                    asyncio.create_task(eval(f'{_command}')(_strValue)) #locals()[_command](_strValue)
                    discovery(_command)
                    #time.sleep(10)
            except Exception as ex:
                my_print(f"Error unpacking or running: {_msg}, {ex}")

        else:
            my_print(f"Unknown command: {_msg}")
        
        #await asyncio.sleep(0.1)
        
        event_sleep_ready.set()

async def setMotion(strValue):
    global auto_start,auto_start_percent,dimmer
    
    if strValue == "true":
        auto_start = True
        auto_start_percent = dimmer.getPercent()
        print(f"setMotion(auto_start) = {strValue} - light:{dimmer.getPercent()}")
        #_setpoint = read_light()
        #pid.set_point = _setpoint
        #print(f"Dim setpoint = {_setpoint}")
        #timer_pid.init(period=100, mode=Timer.PERIODIC, callback = update_pid)
        #pid.update()
    else:
        auto_start = False
        
    
async def setAutoBrightness(strValue):
    print(f"setAutoBrightness(auto_start) = {strValue} - neimplementat")
    return
    if strValue == "true":
        auto_start = True
        auto_start_percent = dimmer.getPercent()
        #_setpoint = read_light()
        #pid.set_point = _setpoint
        #print(f"Dim setpoint = {_setpoint}")
        #timer_pid.init(period=100, mode=Timer.PERIODIC, callback = update_pid)
        #pid.update()
    else:
        auto_start = False
        
    #time.sleep(2)
    #discovery("setAutobrightness")

brightness = 0
ir = ir_remote_read(ir_pin,ir_cb, debug = debug_ir)
print("IR sensor listening")
    
#print("ok")
#sys.exit()


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

#pid = PID(read_light,pid_output,_P=const(2.0), _I=const(0.01), _D=const(0.0),debug = False)

timer_pid = Timer(0)
timer = Timer(2)


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


last_run_time_send = 0
last_run_time_receive = 0

last_print = 0
def my_print(message):
    global last_print
    print(message)
    if oled_enabled:
        last_print = time.ticks_ms()

        oled_write.set_textpos(oled,56,0)
        oled_write.printstring(f'{message}\n')
        oled.show()
        

import ssl
def mqttClient(ssl_enabled = False,name="pico"):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.verify_mode = ssl.CERT_NONE
    client = MQTTQueue(client_id=b"" + my_machine.name,
    server=b"fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud",
    port=8883,
    user=b"apanoiu_devices",
    password=b"Mqtt741852",
    keepalive=50000,
    ssl=ssl_context #,
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
    client.publish(topic=topic_send, msg= value, retain=False, qos=0)
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




def discovery(sender):
    global topic_send,my_machine,lastMotion,autoBrightness
    print(f"Discovery function called by {sender}")
    #temperature = read_temperature()
    #humidity = read_humidity()
    #ambient = read_light()
    #dim = read_dim()
    #output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(ambient),"dim":str(dim),"lastmotion":lastMotion,"autobrightness":autoBrightness,"motion": auto_start}
    _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0,"motion": auto_start}
                
    #_output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(light_sensor.light()),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":0} #"lastmotion":f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}'
    
    #output = json.loads()
    #publish(topic_send, f"device:{my_machine.device}")
    #publish(topic_send, f"name:{my_machine.name}")
    #if (time.time() - lastMotion ) / 60 < 5:
    #publish(topic_send, f"lastmotion:{lastMotion}")
    #sendTemperature("Discovery")
    publish(topic_send, f"jsonDiscovery:{_output}")
    my_print(f"jsonDiscovery:{_output}")

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
                    #dim.setReqIndex1(round(intValue*200/100))
                    await dim.dimToPercent(intValue)
                    
                    #print(f"Command: {command}, Value: {strValue}, index: {round(value*200/100)}")                
                if command == "setAutoBrightness":
                    print("setAutoBrightness")
                    locals()[command](strValue)
                    discovery("setAutobrightness")
                if command == "dim":
                    intValue = int(strValue)
                    timer_pid.deinit()
                    setAutoBrightness("false")
                    #dim.setReqIndex1(round(intValue*200/100))
                    await dim.dimToPercent(intValue)
                    
                
                
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





adc = ADC(ambient_light_pin)



#saved settings:
#file = open("config.py", "r")
#settings = file.read()
#settings_dict = json.loads(settings)
#humidity_setpoint = int(settings_dict["humidity_setpoint"])

#dimSetPoint = int(adc.read_u16()* 233 / 65534)



async def wifi_connection_check(wifi):
    global event_mq_connected,event_wifi_connected
    await event_wifi_connected.wait()
    while True:
        #my_print(f"called wifi connection check, wifi: {wifi.is_connected()}, MQ event:{event_mq_connected.state}  - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
        #print(f"wifi_connection_check event_wifi_connected.state: {event_wifi_connected.state}")
        if wifi.is_connected():
            led_wifi.on()
            if not event_wifi_connected.state:
                event_wifi_connected.set()
                
        else:
            my_print("Wifi not connected, clear wifi and mq events")
            led_wifi.off()
            event_mq_connected.clear()
            event_wifi_connected.clear()
                
        await asyncio.sleep(10)


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
        await asyncio.sleep(30)

async def connect_mq(event_request_ready): 
    if True: #while True:
        my_print(f"MQ connection - wait for wifi: {event_wifi_connected.state} and request: {event_request_ready.state}")
        await event_wifi_connected.wait()
        if not event_mq_connected.is_set():
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
        if True:
        #try:
            #client.ping()
            #print("MQ Check msg")
            if wifi.is_connected():
                #await asyncio.sleep(0.2)
                #client.check_msg()
                
                await client.a_wait_msg(queue)
                event_request_ready.set()
                await asyncio.sleep(1)
                counter += 1
                #print("MQ Check msg")
                if counter%30 == 0:
                    #print("send ping")
                    client.ping()
                    counter = 0
                    #led.set_value("green")
                    #await asyncio.sleep(0.1)
                    #led.off()
                    await blink(led_mq,1)
            else:
                led.set_value("red")
                event_request_ready.set()
                #print(counter)
                #my_print("client checked msg")
                
        #except Exception as ex:
        #    my_print(f"MQ Error on ping, event_mq_connected.clear() Err:{ex}")
        #    event_mq_connected.clear()
        #    event_request_ready.set()
        #    await asyncio.sleep(2)

        
        
        await asyncio.sleep(time)
        #await asyncio.sleep(1)
        #event_sleep_ready.set()

read_pulses = []
pulse_in = 0
old_pulse_in = 0
event_matter = Event()
pwm_in = Pin(7,Pin.IN)

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
async def read_touch():
    await asyncio.sleep(5)
    my_print("touch init")
    while True:
        if check_touch():
            print("touch")
        await asyncio.sleep(0.3)
        
async def print_pulse_in():
    await asyncio.sleep(5)
    while True:
        await event_matter.wait()
        event_matter.clear()
        print(f"async def read_pulse_in()={pulse_in}") # , pulses: {read_pulses[0]},{read_pulses[1]},{read_pulses[2]},{read_pulses[3]},{read_pulses[4]},{read_pulses[5]}")
        dimmer.dimToPercent(pulse_in)
        #await asyncio.sleep(1)

async def inactivity():
    global last_motion,auto_start,auto_start_percent

    print("Init inactivity loop")
    await asyncio.sleep(30)
    motion_threshold = 60
    _sleep_time=20
    while True:
        if not auto_start:
            await asyncio.sleep(_sleep_time)
            continue
        
        _now = time.localtime()[1]*30*24*3600 + time.localtime()[2]*24*3600 + time.localtime()[3]*3600 + time.localtime()[4]*60 + time.localtime()[5]
        #print(f'process inactivity: {time.localtime()} -> {_now} - last_motion: {last_motion}')
        if _now - last_motion > motion_threshold and dimmer.getPercent() != 0:
            my_print(f'inact auto_start: {auto_start}')
            my_print(f'auto_start_percent: {auto_start_percent}')
            await dimmer.dimToPercent(0)
        
        await asyncio.sleep(_sleep_time)

async def clear_oled():
    my_print("Init clear_oled")
    while True:
        await asyncio.sleep(5)
        if oled_enabled and time.ticks_ms() - last_print > 30000:
            oled.fill(0)
            oled.show()

async def receive_espnow():
    #global e
    import aioespnow
    e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
    e.active(True)
    async for mac, msg in e:
        print(f'Echo: {msg} - {str(msg,"UTF-8")}')
        if str(msg,"UTF-8") == "ON":
            setSeconds()
            print("on")
        else:
            print("off")



async def main():
    t_connect = asyncio.create_task(wifi.check_and_connect())
    t_process_ir_queue = None #asyncio.create_task(process_ir_queue(ir_queue))
    t_ir = None #asyncio.create_task(ir.process(ir_queue)) #not handled
    #t_connect = None #asyncio.create_task(wifi.check_and_connect())
    t_mq_connection_check = None #asyncio.create_task(mq_connection_check(event_wifi_connected,event_mq_connected))
    t_mq_check_messages = None #asyncio.create_task(mq_check_messages(client,0.5))
    t_process_queue = None #asyncio.create_task(process_queue(queue))
#    await asyncio.sleep(5)
    t_wifi_connection_check = None #asyncio.create_task(wifi_connection_check(wifi)) #not handled
    
    t_motion = None 
    t_inactivity = None

    t_update_ntp = None #asyncio.create_task(ntp.update_ntp())
    t_touch = None
    t_touch = asyncio.create_task(read_touch())
    #t_read_pulse_in = asyncio.create_task(read_pulse_in())
    #t_print_pulse_in = asyncio.create_task(print_pulse_in())
    t_clear_oled = None
    t_receive_espnow = None
    while True:
        await asyncio.sleep(1)
        #gc.collect()
        
        
        if t_process_ir_queue is None or t_process_ir_queue.done():
            t_process_ir_queue = None
            print("restart task t_process_ir_queue")
            t_process_ir_queue = asyncio.create_task(process_ir_queue(ir_queue))
        
        if t_ir is None or t_ir.done():
            t_ir = None
            print("restart task t_ir")
            t_ir = asyncio.create_task(ir.process(ir_queue))
            
        if t_motion is None or t_motion.done():
            t_motion = None
            print("restart task t_motion")
            t_motion = asyncio.create_task(process_motion(event_motion)) #not handled
        
        if t_inactivity is None or t_inactivity.done():
            t_inactivity = None
            print("restart task t_inactivity")
            t_inactivity = asyncio.create_task(inactivity()) #not handled
        
        
        if t_update_ntp is None or t_update_ntp.done():
            t_update_ntp = None
            print("restart task t_update_ntp")
            t_update_ntp = asyncio.create_task(ntp.update_ntp())
    
        if t_process_ir_queue is None or t_process_ir_queue.done():
            t_process_ir_queue = None
            print("restart task t_process_ir_queue")
            t_process_ir_queue = asyncio.create_task(process_ir_queue(ir_queue))

        
        if t_wifi_connection_check is None or t_wifi_connection_check.done():
            t_wifi_connection_check = None
            print("restart task t_wifi_connection_check")
            t_wifi_connection_check = asyncio.create_task(wifi_connection_check(wifi))
        
        if t_process_queue is None or t_process_queue.done():
            my_print("process_queue is done")
            t_process_queue = None
            t_process_queue = asyncio.create_task(process_queue(queue))
        
        if  t_mq_connection_check is None or t_mq_connection_check.done():
            print("restart task t_mq_connection_check")
            t_mq_connection_check = None
            t_mq_connection_check = asyncio.create_task(mq_connection_check(event_wifi_connected,event_mq_connected))

        if t_mq_check_messages is None or t_mq_check_messages.done():
            print("restart task t_mq_check_messages")
            t_mq_check_messages = asyncio.create_task(mq_check_messages(client,0.5))
    
        #if t_process_queue.done():
        #    print("restart task t_process_queue")
        #    t_process_queue = asyncio.create_task(process_queue(queue))
        if t_clear_oled is None or t_clear_oled.done():
            t_clear_oled = None
            print("restart task t_clear_oled")
            t_clear_oled = asyncio.create_task(clear_oled())

        if t_receive_espnow is None or t_receive_espnow.done():
            t_receive_espnow = None
            print("restart task t_receive_espnow")
            t_receive_espnow = asyncio.create_task(receive_espnow())

        await asyncio.sleep(30)

try:
    my_print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
#except Exception as ex:
#    my_print(f"Catch: {ex}")

