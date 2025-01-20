

import gc
#gc.enable()
from i2c_init import *
#oled.poweroff()

from my_remotes import *
import time
import asyncio
from WEATHER import *
from NTP import *
from dim import Dim
from brightness_map_1024 import brightness_map_1024
from machine import lightsleep
from MACHINES import *
from machine import Signal,PWM,Pin,sleep
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

debug = False 


my_machine = MACHINES()


def my_print(message):
    print(message)
    debug_oled(message)

def debug_oled(message):
    global debug
    if debug:
        print("oled msg")
        oled_write.set_textpos(oled,56,0)
        oled_write.printstring(f'{message}\n')
        oled.show()


from CONNECTWIFI_AS import *
wifi = CONNECTWIFI_AS(event_wifi_connected,my_machine.device)
ntp = NTP(wifi.wlan,event_wifi_connected,event_request_ready,event_ntp_updated)

#print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
weather = WEATHER(event_wifi_connected,event_weather_updated,event_request_ready,event_sleep_ready)

led_value = True
led = Signal(Pin(8,Pin.OUT,value = 1),invert=True)
#led.on()
#led = PWM(Pin(8,Pin.OUT,value=0))
dimmer = Dim(10,fade_time_ms = 60)

from MAP import *
map_ambient_light_oled = MAP(0,149,5,128)


def mqttClient(ssl_enabled = False,name="pico"):
    client = MQTTQueue(client_id=b"" + my_machine.name,
    server=b"fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud",
    port=8883,
    user=b"apanoiu_devices",
    password=b"Mqtt741852",
    keepalive=50000,
    ssl=ssl_enabled,
    ssl_params={'server_hostname':'fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud'}
    )

    #client.connect()
    return client

from machine import RTC
rtc = RTC()

dim_value = 0
def dim(strValue):
    global dim_value
    dim_value = int(float(strValue)*10.24)
    my_print(f"Dim to: {strValue} - {dim_value}")
    dimmer.setReqIndex1(dim_value)



#from CONNECTWIFI import *
#wifi = CONNECTWIFI()
#from MACHINES import *
#my_machine = MACHINES()

def mqtt_cb(topic,msg):
    global queue,client,event_wifi_connected,event_mq_connected
    my_print(f"cb: {msg}")
    _msg = msg.decode()
    queue._put(_msg)
        

#from umqtt.simple import MQTTClient
from mqtt_queue import MQTTQueue
client = mqttClient(True,my_machine.device)
client.set_callback(mqtt_cb)


#while True:
#    client.check_msg()
#oled.fill(0)
#oled_write = Writer(oled, consolas16)

#oled_write = writer.Writer(oled, myfont) #freesans20
#oled_write.set_textpos(oled,0,0)
#oled_write.printstring(f"Loading...")
#oled.show()
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



    

async def heartbeat_oled(wifi):
    global set_temp,weather,led,led_value,event_wifi_connected,event_mq_connected,debug
    my_print("heartbeat_oled")
    last_minute = -1 #rtc.datetime()[5]
    
    while True:
        if debug:
            await asyncio.sleep(60)
            continue
        
        if oled is None:
            await asyncio.sleep(60)
        oled_write.set_textpos(oled,40,114)
        oled_write.printstring(f'{"W" if event_wifi_connected.state else "-"}{"Q" if event_mq_connected.state else "-"}')

        if last_minute != rtc.datetime()[5]:
            my_print("diff")
            
            #oled.fill(0)
            oled_write.set_textpos(oled,20,0)
            if temp_sensor.temperature() == -100:
                oled_write.printstring(f'In: -')
            else:
                oled_write.printstring(f'In: {temp_sensor.temperature()}')
            oled_write.printdegrees()
            if temp_sensor.humidity() == -100:
                oled_write.printstring(f'  - % ')
            else:
                oled_write.printstring(f'  {temp_sensor.humidity()} %  ')
                #oled.drawCircle(50, 50, 10, WHITE)
            last_minute = rtc.datetime()[5]
        
        if event_weather_updated.state: # and weather.temperature() > -100:
            oled_write.set_textpos(oled,40,0)
            oled_write.printstring(f'Out: {weather.temperature()}/{weather.temperature_feel()}')
            oled_write.printdegrees()
            oled_write.printstring(f',R:{weather.precipitation() or "- "}')#9-10chars
            
        
        if event_ntp_updated.state:
            oled_write.set_textpos(oled,0,0)
            oled_write.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d} - {rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]}') #minut:{rtc.datetime()[6]:02d} {_ambient_light} L
        
        if light_sensor.enabled:
            oled.hline(0,62,128,0)
            oled.hline(0,62,int(map_ambient_light_oled.map_value(light_sensor.light())),1)
            
        oled.show()
        await asyncio.sleep(5)

t = None
tasks = []


def sayhello(strValue):
    my_print(f"Hello {strValue}")

async def check_queue(queue):
    while True:
        #my_print(queue.qsize())
        await asyncio.sleep(5)
    
async def process_queue(queue):
    global client,event_wifi_connected,event_mq_connected
    my_print("MQ process_queue initialised")
    while True:
        _msg = await queue.get()
        my_print(f"Queue msg: {_msg}")
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
        await asyncio.sleep(0.1)
        event_sleep_ready.set()

        

async def mq_check_messages(client,time=5):
    global event_sleep_ready,wifi,event_wifi_connected,event_mq_connected,event_request_ready,queue
    counter = 1
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
                await asyncio.sleep(0.2)
                #client.ping()
                #client.check_msg()
                await client.a_wait_msg(queue)
                await asyncio.sleep(0)
                counter += 1
                if counter%30 == 0:
                    print("send ping")
                    client.ping()
                    if counter>1000:
                        counter = 0
                my_print("client checked msg")
                
        except Exception as ex:
            my_print(f"MQ Error on ping, event_mq_connected.clear() Err:{ex}")
            event_mq_connected.clear()
            event_request_ready.set()
            await asyncio.sleep(2)

        event_request_ready.set()
        
        await asyncio.sleep(time)
        #await asyncio.sleep(1)
        event_sleep_ready.set()


async def wifi_connection_check(wifi):
    global event_mq_connected,event_wifi_connected
    while True:
        #my_print(f"called wifi connection check, wifi: {wifi.is_connected()}, MQ event:{event_mq_connected.state}  - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
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
        await asyncio.sleep(0)
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
            gc.collect()
            #client.subscribe(topic = my_machine.topic_receive)
            my_print("MQ connected and subscribed")
            event_mq_connected.set()
            #event_sleep_ready.set()
            
        except Exception as ex:
            my_print(f"Err connecting to MQ, {ex}")
            event_mq_connected.clear()
        event_request_ready.set()
        await asyncio.sleep(2) 
        

async def program_sleep(event_wifi_connected,event_mq_connected,event_sleep_ready):
    global led,led_value,event_weather_updated
    while True:
        await event_wifi_connected.wait()
        await event_mq_connected.wait()
        await event_sleep_ready.wait()
        if not event_weather_updated.state:
            await asyncio.sleep(3)
        #my_print("sleep")
        #time.sleep_ms(50)
        #await asyncio.sleep(3)
        #lightsleep(2000)
        await asyncio.sleep(0)
        event_sleep_ready.clear()
        #await asyncio.sleep(5)
        
async def update_contrast():
    while True:
        if light_sensor.enabled:
            _ambient_light = light_sensor.light()
            if _ambient_light <10:
                oled.contrast(0)
            elif _ambient_light <30:
                oled.contrast(5)
            elif _ambient_light <50:
                oled.contrast(10)
            else:
                oled.contrast(150)
        await asyncio.sleep(60)

async def mq_ping(client):
    while True:
        await event_mq_connected.wait()
        await event_request_ready.wait()
        try:
            
            event_request_ready.clear()
            client.ping()
            event_request_ready.set()
        except:
            my_print("MQ ping exception")
            event_request_ready.set()
            event_mq_connected.clear()
        await asyncio.sleep(30)
        
async def main():
    await wifi.check_and_connect()
    asyncio.create_task(check_queue(queue))
    t_wifi_connection_check = asyncio.create_task(wifi_connection_check(wifi)) #not handled
    t_ntp_update = asyncio.create_task(ntp.update_ntp())

    t_mq_connection_check = asyncio.create_task(mq_connection_check(event_wifi_connected,event_mq_connected))
    t_process_queue = asyncio.create_task(process_queue(queue))
    t_program_sleep = asyncio.create_task(program_sleep(event_wifi_connected,event_mq_connected,event_sleep_ready))
    
    t_oled_update = asyncio.create_task(heartbeat_oled(wifi))
    t_update_contrast = asyncio.create_task(update_contrast())
    t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected,on_demand = False)) #send discovery on interval#
    t_mq_check_messages = asyncio.create_task(mq_check_messages(client,1))
    t_mq_ping = asyncio.create_task(mq_ping(client))
    
    
    while True:
        try:
            await asyncio.sleep(5)
            #gc.collect()
            #await mqtt_send_temp(client,True)
            
            #continue
            if t_program_sleep.done():
                my_print("t_mq_ping is done")
                t_mq_ping=None
                #gc.collect()
                t_mq_ping = asyncio.create_task(mq_ping(client))
        
            if t_program_sleep.done():
                my_print("t_sleep_connection is done")
                t_sleep=None
                #gc.collect()
                t_sleep = asyncio.create_task(program_sleep(event_wifi_connected,event_mq_connected,event_sleep_ready))

            if t_ntp_update.done():
                my_print("t_wifi_connection is done")
                t_ntp_update=None
                #gc.collect()
                t_ntp_update = asyncio.create_task(ntp.update_ntp())
                
            if t_process_queue.done():
                my_print("process_queue is done")
                t_process_queue=None
                #gc.collect()
                t_process_queue = asyncio.create_task(process_queue(queue))
            
            
            if False: #t_mq_connection.done():
                my_print("t_mq_connection is done")
                t_mq_connection=None
                #gc.collect()
                t_mq_connection = asyncio.create_task(mq_connection(wifi,client,event_wifi_connected,event_mq_connected))
            

            if t_mq_check_messages.done():
                my_print("HB is done")
                t_mq_check_messages=None
                gc.collect()
                t_mq_check_messages = asyncio.create_task(mq_check_messages(client,10))
            
            
            if t_mqtt_discovery.done(): #toled.done():
                my_print("t_mqtt_discovery is done")
                t_mqtt_discovery=None
                gc.collect()
                t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected,False))
            
            if t_oled_update.done():
                my_print("oled refresh is done")
                t_oled_update=None
                gc.collect()
                t_oled_update = asyncio.create_task(heartbeat_oled(wifi,1))
             
                
        except Exception as ex:
            my_print(f"Catch from main loop: {ex}")
            oled_write.set_textpos(oled,55,0)
            oled_write.printstring(f'E_lp:{ex}\n')
            oled.show()

            await asyncio.sleep(5)
            my_print(f"Catch from main loop after wait: {ex}")
        await asyncio.sleep(10)
        #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
       
try:
    my_print("Async call main")
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
except Exception as ex:
    my_print(f"Catch: {ex}")
    oled_write.set_textpos(oled,55,0)
    oled_write.printstring(f'E:{ex} \n ')
    oled.show()

finally:
    my_print(f"finally: ")
    oled.fill(0)
    asyncio.new_event_loop()



