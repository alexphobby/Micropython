import gc
gc.enable()
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
from i2c_init import *
from machine import Pin
from ir_remote_read import ir_remote_read
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

ntp = NTP(event_wifi_connected)
my_machine = MACHINES()
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
from CONNECTWIFI_AS import *
wifi = CONNECTWIFI_AS(event_wifi_connected)
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
weather = WEATHER(event_wifi_connected,event_weather_updated)
print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)
#led = Signal(Pin(8,Pin.OUT,value = 1),invert=True)
#led.on()
#led = PWM(Pin(8,Pin.OUT,value=0))
dimmer = Dim(10,fade_time_ms = 60)
#from ir_remote_read_demo import *


#from aremote import NEC_IR, REPEAT
#from machine import Signal

#def cb(data, addr, led):
#    print(f"Addr: {addr} - Data: {data}")

#ir = NEC_IR(ir_pin, cb, True, Pin(8,Pin.OUT))

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

def ir_callback(remote,command,combo):
    #print((remote,command))
    button = ""
    try:
        button = remote_samsung[combo]
        return
    except:
        pass
    
    try:
        button = remote_tiny[combo]
    except:
        pass
    if len(button) > 0:
        print(f"Remote button : {button}")
    
    
    #print((remote,command))
    
print("init ir")    
ir = ir_remote_read(ir_pin,ir_callback)

#from ssd1306 import SSD1306_I2C

#Init Oled display i2c scan= [60]
#oled = SSD1306_I2C(128, 64, i2c)



#ir_remote_read(ir_pin,ir_callback)
from machine import RTC
rtc = RTC()

##init HDC temperature sensor, already we have i2c



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
        
        gc.collect
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
            output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(sensor_temp.temperature()),"humidity":str(sensor_temp.humidity()),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":sender_count}
            client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
            print("published")
            await asyncio.sleep(5)
            #lightsleep(20000)
            return
        except Exception as ex:
            print(f"mqtt_send error: {ex}")
        return
        print("should not run")
    else:
        while True:
            await event_wifi_connected.wait()
            await event_mq_connected.wait()

            try:
                sender_count +=1
                print(f"Send mqtt message on {my_machine.topic_send}")
                output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(sensor_temp.temperature()),"humidity":str(sensor_temp.humidity()),"ambient":str(0),"dim":str(dimmer.getPercent()),"lastmotion":0,"autobrightness":0,"count":sender_count}
                client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
                await asyncio.sleep(60)
            except Exception as ex:
                print(f"mqtt_send error: {ex}")
                await asyncio.sleep(60)


        

async def heartbeat_oled(wifi):
    global set_temp,ir,weather
    print("heartbeat_oled")
    print(ir)
    s = True
    last_minute = -1 #rtc.datetime()[5]
    
    while True:
        
        if last_minute == rtc.datetime()[5]:
            oled_write.set_textpos(oled,0,0)
            #oled_write.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            oled_write.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}     ')
            #oled_write.printstring(f'{wifi.wlan.status()}     ')
            oled.show()
            await asyncio.sleep_ms(100)
            #last_minute = rtc.datetime()[6]
        elif event_weather_updated.state:
            print(f"update temp: {last_minute} != {rtc.datetime()[5]}")
            oled.fill(0)
            oled_write.set_textpos(oled,0,0)
            #oled_write.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            oled_write.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            oled_write.set_textpos(oled,20,0)
            oled_write.printstring(f'In: {sensor_temp.temperature()} C')
            
            #oled_write.set_textpos(oled,20,60)
            oled_write.printstring(f'  {sensor_temp.humidity()} %   ')
            if weather.temperature() > -100:
                oled_write.set_textpos(oled,40,0)
                oled_write.printstring(f'Out: {weather.temperature()} C  ')
                #oled.drawCircle(50, 50, 10, WHITE)
            oled.show()
            last_minute = rtc.datetime()[5]
            #lightsleep(20000)
        await asyncio.sleep_ms(800)
            


t = None
tasks = []
sender_count = 0

async def heartbeat(client,event_wifi_connected,event_mq_connected,time=1):
    while True:
        await event_wifi_connected.wait()
        try:
            client.ping()
        except Exception as ex:
            print("MQ Error on ping, connecting..")
            event_mq_connected.set()
            asyncio.create_task(mq_connection(wifi,event_wifi_connected,event_mq_connected))
        await event_mq_connected.wait()
        client.check_msg()
        await asyncio.sleep(time)


async def wifi_connection(wifi,event_wifi_connected):
    while True:
        #print("called wifi connect")
        await wifi.check_and_connect()
        await asyncio.sleep(5)

async def mq_connection(wifi,event_wifi_connected,event_mq_connected):
    if True: #while True:
        await event_wifi_connected.wait()
        if wifi.is_connected():
            try:
                print("MQ connection - connect")
                gc.collect()
                print(f"mem free: {gc.mem_free()}; alloc: {gc.mem_alloc()}")
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
    t_mq_connection = asyncio.create_task(mq_connection(wifi,event_wifi_connected,event_mq_connected))
    t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client,event_wifi_connected,event_mq_connected)) #send discovery on interval#
    t_oled_update = asyncio.create_task(heartbeat_oled(wifi))
    t_ntp_update = asyncio.create_task(ntp.update_ntp())
    thb = asyncio.create_task(heartbeat(client,event_wifi_connected,event_mq_connected,0.2))
    while True:
        try:
            await asyncio.sleep(5)
            gc.collect()
            #await mqtt_send_temp(client,True)

            if t_ntp_update.done():
                print("t_wifi_connection is done")
                t_ntp_update=None
                gc.collect()
                t_ntp_update = asyncio.create_task(ttp.update_ntp())
                
            if t_wifi_connection.done():
                print("t_wifi_connection is done")
                t_wifi_connection=None
                gc.collect()
                t_wifi_connection = asyncio.create_task(t_wifi_connection(wifi,event_wifi_connected))
            
            
            if False: #t_mq_connection.done():
                print("t_mq_connection is done")
                t_mq_connection=None
                gc.collect()
                t_mq_connection = asyncio.create_task(t_mq_connection(wifi,event_wifi_connected,event_mq_connected))
            

            if thb.done():
                print("HB is done")
                thb=None
                gc.collect()
                thb = asyncio.create_task(heartbeat(client,event_wifi_connected,event_mq_connected,1))
            
            
            if t_mqtt_discovery.done(): #toled.done():
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
       
if True: #try:
    print("Async call main")
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
#except Exception as ex:
    print(f"Catch: {ex}")
#finally:
    print(f"finally: ")
    asyncio.new_event_loop()



