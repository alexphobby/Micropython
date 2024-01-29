import gc
#gc.enable()
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
from i2c_init import *
from machine import Pin
from my_remotes import *
import asyncio
from WEATHER import *
from NTP import *

from dim import Dim
from brightness_map_1024 import brightness_map_1024

from machine import lightsleep

from MACHINES import *
from machine import Signal,PWM,Pin
from asyncio import Event
event_wifi_connected = Event()
event_mq_connected = Event()
event_weather_updated = Event()

my_machine = MACHINES()
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
from CONNECTWIFI_AS import *
wifi = CONNECTWIFI_AS(event_wifi_connected,my_machine.device)
ntp = NTP(wifi.wlan,event_wifi_connected)

print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
weather = WEATHER(event_wifi_connected,event_weather_updated)
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
#led = Signal(Pin(8,Pin.OUT,value = 1),invert=True)
#led.on()
#led = PWM(Pin(8,Pin.OUT,value=0))
dimmer = Dim(10,fade_time_ms = 60)



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

from machine import RTC
rtc = RTC()

dim_value = 0
def dim(strValue):
    global dim_value
    dim_value = int(float(strValue)*10.24)
    print(f"Dim to: {strValue} - {dim_value}")
    dimmer.setReqIndex1(dim_value)


def mqtt_receive_cb(topic, msg):
    print(f'Received {(topic, msg)}')
    msg = msg.decode()
    if msg == "discovery":
        print("Send discovery result")
        task = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected,True))
        
    elif msg == "update" and topic == my_machine.topic_receive:
        print("Update from GitHub")
        
        #gc.collect
        import update
        update.update()
    else:
        try:
            command,strValue = msg.split(':')
            locals()[command](strValue)
                
        except Exception as ex:
            print(f"cannot unpack: {msg}, {ex}")


from umqtt.robust import MQTTClient
client = mqttClient(True,my_machine.device)
client.set_callback(mqtt_receive_cb)

#oled.fill(0)
#oled_write = Writer(oled, consolas16)

#oled_write = writer.Writer(oled, myfont) #freesans20
#oled_write.set_textpos(oled,0,0)
#oled_write.printstring(f"Loading...")
#oled.show()
sender_count = 0
async def mqtt_send_temp(client,event_wifi_connected,event_mq_connected,on_demand = False):
    global sender_count
    if on_demand:
        await event_wifi_connected.wait()
        await event_mq_connected.wait()
        sender_count +=1
        try:
            print(f"Send on demand message on {my_machine.topic_send}")
            _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":sender_count}
            client.publish(my_machine.topic_send, f'jsonDiscovery:{_output}', qos = 0)
            _output = None
            await asyncio.sleep(5)
            lightsleep(10000)
            return
        except Exception as ex:
            print(f"mqtt_send error: {ex}")
        return
        print("should not run")
    else:
        while False: #Do not run
            await event_wifi_connected.wait()
            await event_mq_connected.wait()

            try:
                sender_count +=1
                print(f"Send mqtt message on {my_machine.topic_send}")
                _output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(temp_sensor.temperature() or -100),"humidity":str(temp_sensor.humidity() or -100),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":sender_count}
                client.publish(my_machine.topic_send, f'jsonDiscovery:{_output}', qos = 0)
                _output = None
            except Exception as ex:
                print(f"mqtt_send error: {ex}")
            await asyncio.sleep(60)


        

async def heartbeat_oled(wifi):
    global set_temp,weather
    print("heartbeat_oled")
    last_minute = -1 #rtc.datetime()[5]
    
    while True:
        
        
        print("oled_update")
        _ambient_light = light_sensor.light()
        if _ambient_light <10:
            oled.contrast(2)
        elif _ambient_light <30:
            oled.contrast(10)
        elif _ambient_light <50:
            oled.contrast(30)
        else:
            oled.contrast(150)
        oled_write.set_textpos(oled,0,0)
        oled_write.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d} {_ambient_light} Lux    ')
        if event_weather_updated.state and weather.temperature() > -100:
            oled_write.set_textpos(oled,40,0)
            oled_write.printstring(f'Out: {weather.temperature()} C  ')
            
        oled.show()
        
        if last_minute != rtc.datetime()[5]:
            print(f"update temp: {last_minute} != {rtc.datetime()[5]}, light: {light_sensor.light()}, weather updated: {event_weather_updated.state}")
            #oled.fill(0)
            #oled_write.set_textpos(oled,0,0)
            #oled_write.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            #oled_write.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            oled_write.set_textpos(oled,20,0)
            oled_write.printstring(f'In: {temp_sensor.temperature()} C')
            
            #oled_write.set_textpos(oled,20,60)
            oled_write.printstring(f'  {temp_sensor.humidity()} %   ')
            
                #oled.drawCircle(50, 50, 10, WHITE)
            oled.show()
        last_minute = rtc.datetime()[5]
            #lightsleep(20000)
        #await asyncio.sleep(30)
        if event_weather_updated.state and event_mq_connected.state:
            #client.check_msg()
            #print("sleep")
            #await asyncio.sleep(0.2)
            #lightsleep(2000)
            await asyncio.sleep(5)
        else:
            await asyncio.sleep(5)
            


t = None
tasks = []
sender_count = 0

async def heartbeat(client,event_wifi_connected,event_mq_connected,time=1):
    while True:
        await event_wifi_connected.wait()
        await event_mq_connected.wait()
        try:
            #print("MQ heartbeat try ping")
            #client.ping()
            client.check_msg()
            #client.publish(my_machine.topic_send, f'jsonDiscovery:test')
            #print("MQ ping ok")
        except Exception as ex:
            print("MQ Error on ping, connecting..")
            event_mq_connected.clear()
#            asyncio.create_task(mq_connection(wifi,event_wifi_connected,event_mq_connected))
#        await event_mq_connected.wait()
        
        await asyncio.sleep(time)


async def wifi_connection(wifi,event_wifi_connected):
    while True:
        await wifi.check_and_connect()
        await asyncio.sleep(30)

async def wifi_connection_check(wifi,client,event_wifi_connected):
    while True:
        print(f"called wifi connection check, wifi: {wifi.is_connected()}, MQ event:{event_mq_connected.state}  - mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
        #gc.collect()
        if not event_mq_connected.state:
            await mq_connection(wifi,client,event_wifi_connected,event_mq_connected)
        #print(wifi.is_connected())
        await asyncio.sleep(9)


async def mq_connection(wifi,client,event_wifi_connected,event_mq_connected):
    if True: #while True:
        #print("MQ connection - wait for wifi")
        await event_wifi_connected.wait()
        if wifi.is_connected():
            event_wifi_connected.set()
            try:
                print("MQ connection - connect")
                #gc.collect()
                print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
                #await asyncio.sleep(5)
                client.connect()
                client.subscribe(topic = my_machine.topic_receive)
                client.subscribe(topic = b"to/*")
                print("MQ connected and subscribed")
                event_mq_connected.set()
                await asyncio.sleep(60)
            except Exception as ex:
                print(f"Err connecting to MQ, {ex}")
                event_mq_connected.clear()
        else:
            print("Connect to MQ: no wifi available")
            event_mq_connected.clear()
        await asyncio.sleep(10)



async def main():
    t_wifi_connection = asyncio.create_task(wifi_connection(wifi,event_wifi_connected))
    await asyncio.sleep(15)
    t_oled_update = asyncio.create_task(heartbeat_oled(wifi))
    #t_mq_connection = asyncio.create_task(mq_connection(wifi,event_wifi_connected,event_mq_connected))
    t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected,on_demand = True)) #send discovery on interval#
    
    t_ntp_update = asyncio.create_task(ntp.update_ntp())
    thb = asyncio.create_task(heartbeat(client,event_wifi_connected,event_mq_connected,2))
    
    t_check_wifi = asyncio.create_task(wifi_connection_check(wifi,client,event_wifi_connected))
    
    while True:
        try:
            await asyncio.sleep(5)
            #gc.collect()
            #await mqtt_send_temp(client,True)

            if t_ntp_update.done():
                print("t_wifi_connection is done")
                t_ntp_update=None
                #gc.collect()
                t_ntp_update = asyncio.create_task(ntp.update_ntp())
                
            if t_wifi_connection.done():
                print("t_wifi_connection is done")
                t_wifi_connection=None
                #gc.collect()
                t_wifi_connection = asyncio.create_task(wifi_connection(wifi,client,event_wifi_connected))
            
            
            if False: #t_mq_connection.done():
                print("t_mq_connection is done")
                t_mq_connection=None
                #gc.collect()
                t_mq_connection = asyncio.create_task(mq_connection(wifi,client,event_wifi_connected,event_mq_connected))
            

            if thb.done():
                print("HB is done")
                thb=None
                gc.collect()
                thb = asyncio.create_task(heartbeat(client,event_wifi_connected,event_mq_connected,1))
            
            
            if False: #t_mqtt_discovery.done(): #toled.done():
                print("t_mqtt_discovery is done")
                t_mqtt_discovery=None
                gc.collect()
                t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected))
            
            if t_oled_update.done():
                print("HB is done")
                t_oled_update=None
                gc.collect()
                t_oled_update = asyncio.create_task(heartbeat_oled(wifi,1))
             
                
        except Exception as ex:
            print(f"Catch from main loop: {ex}")
            await asyncio.sleep(5)
            print(f"Catch from main loop after wait: {ex}")
        await asyncio.sleep(5)
        #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
       
try:
    print("Async call main")
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
except Exception as ex:
    print(f"Catch: {ex}")
finally:
    print(f"finally: ")
    asyncio.new_event_loop()



