from i2c_init import *
from machine import Pin
from ir_remote_read import ir_remote_read
from my_remotes import *
import asyncio
from WEATHER import *
from NTP import *

oled = False

from machine import lightsleep

from MACHINES import *
from machine import Signal

my_machine = MACHINES()

from CONNECTWIFI_AS import *
wifi = CONNECTWIFI_AS()
weather = WEATHER(wifi.wlan)
ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)
led = Signal(Pin(8,Pin.OUT,value = 1),invert=True)
led.on()
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
    
    
ir = ir_remote_read(ir_pin,ir_callback)

#from ssd1306 import SSD1306_I2C
#from writer import Writer
#import consolas16

#Init Oled display i2c scan= [60]
#oled = SSD1306_I2C(128, 64, i2c)

#ir_remote_read(ir_pin,ir_callback)
from machine import RTC
rtc = RTC()

##init HDC temperature sensor, already we have i2c
from hdc1080_util import hdc1080_util
hdc1080 = hdc1080_util(i2c)

from umqtt.robust import MQTTClient
client = mqttClient(True,my_machine.device)




def mqtt_receive_cb(topic, msg):
    print(f'Received {(topic, msg)}')
    if str(msg,"UTF-8") == "discovery":
        print("Send discovery result")
        task = asyncio.create_task(mqtt_send_temp(client,True))
        
    elif msg == "update" and topic == my_machine.topic_receive:
        print("Update from GitHub")
        import gc
        gc.collect
        import update
        update.update()


client.set_callback(mqtt_receive_cb)


#oled.fill(0)
#write_custom_font = Writer(oled, consolas16)

#write_custom_font = writer.Writer(oled, myfont) #freesans20
#write_custom_font.set_textpos(oled,0,0)
#write_custom_font.printstring(f"Loading...")
#oled.show()

async def mqtt_send_temp(client,on_demand = False):
    global sender_count
    print("mqtt_send_temp")
    if not wifi.is_connected():
        print("mqtt_send_temp no wifi yet")
        return
    if on_demand:
        sender_count +=1
        try:
            print(f"Send on demand message on {my_machine.topic_send}")
            output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(0),"lastmotion":0,"autobrightness":0,"count":sender_count}
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
            
            try:
                sender_count +=1
                print(f"Send mqtt message on {my_machine.topic_send}")
                output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(0),"lastmotion":0,"autobrightness":0,"count":sender_count}
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

    if not wifi.is_connected():
        write_custom_font.set_textpos(oled,0,0)
        write_custom_font.printstring(f'{wifi.wlan.status()}     ')
        write_custom_font.set_textpos(oled,20,0)
        write_custom_font.printstring(f'Wait for wifi')
        
        oled.show()
        await asyncio.sleep(2)
        
        
    while True:
        
        if last_minute == rtc.datetime()[5]:
            write_custom_font.set_textpos(oled,0,0)
            #write_custom_font.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            #write_custom_font.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}     ')
            write_custom_font.printstring(f'{wifi.wlan.status()}     ')
            oled.show()
            await asyncio.sleep_ms(100)
            #last_minute = rtc.datetime()[6]
        else:
            print(f"update temp: {last_minute} != {rtc.datetime()[5]}")
            oled.fill(0)
            write_custom_font.set_textpos(oled,0,0)
            #write_custom_font.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.set_textpos(oled,20,0)
            write_custom_font.printstring(f'{hdc1080.temperature()} C')
            
            write_custom_font.set_textpos(oled,20,60)
            write_custom_font.printstring(f' {hdc1080.humidity()} %   ')
            
            if weather.temperature() > -100:
                write_custom_font.set_textpos(oled,40,0)
                write_custom_font.printstring(f'Out: {weather.temperature()} C  ')
                #oled.drawCircle(50, 50, 10, WHITE)
            oled.show()
            last_minute = rtc.datetime()[5]
            lightsleep(20000)
            await asyncio.sleep_ms(800)
            

from asyncio import Event
event = Event()

t = None
tasks = []
sender_count = 0

async def heartbeat(client,time=1):
    while True:
        if wifi.is_connected():
            if True: #try:
                #await asyncio.sleep(30)
                #client.ping()
                client.check_msg()
            #except Exception as ex:
            #    print(f"heartbeat error {ex}")
        await asyncio.sleep(time)

def wifi_connect_done():
    print("wifi connect done")
    led.off()
    if wifi.is_connected():
        print("Init NTP Time, obj: ntp")
        ntp = NTP(wifi.wlan)

        print("client connect, wifi up")
        client.connect()
        print("subscribe")
        client.subscribe(topic = my_machine.topic_receive)
        client.subscribe(topic = b"to/*")
        gc.collect()
    
async def wifi_connection(wifi):
    while True:
        await wifi.check_and_connect(wifi_connect_done)
        await asyncio.sleep(60)

async def mq_connection(wifi):
    while True:
        if wifi.is_connected():
            try:
                print("MQ connection - connect")
                gc.collect()
                client.connect()
                print("subscribe")
                client.subscribe(topic = my_machine.topic_receive)
                client.subscribe(topic = b"to/*")
                await asyncio.sleep(60)
            except Exception as ex:
                print(f"Err connecting to MQ, {ex}")
        else:
            print("Connect to MQ: no wifi available")
        
        await asyncio.sleep(10)


async def main():
    t_wifi_connection = asyncio.create_task(wifi_connection(wifi))
    
    #t_mq_connection = asyncio.create_task(mq_connection(wifi))
       #loop = asyncio.get_event_loop()
    #terr =  asyncio.create_task(err())
        
            
            
    t_mqtt_discovery = asyncio.create_task(mqtt_send_temp(client)) #send discovery on interval#
    #toled = asyncio.create_task(heartbeat_oled(wifi))
    
    thb = asyncio.create_task(heartbeat(client,0.1))
    while True:
        try:
            await asyncio.sleep(5)
            #await mqtt_send_temp(client,True)


            if t_wifi_connection.done():
                print("t_wifi_connection is done")
                t_wifi_connection=None
                gc.collect()
                t_wifi_connection = asyncio.create_task(t_wifi_connection(wifi))
            
            
            if False: #t_mq_connection.done():
                print("t_mq_connection is done")
                t_mq_connection=None
                gc.collect()
                t_mq_connection = asyncio.create_task(t_mq_connection(wifi))
            

            if thb.done():
                print("HB is done")
                thb=None
                gc.collect()
                thb = asyncio.create_task(heartbeat(client,1))
            
            if False: #toled.done():
                print("ERR is done")
                toled=None
                gc.collect()
                toled = asyncio.create_task(heartbeat_oled(client))
             
                
        except Exception as ex:
            print(f"Catch from main loop: {ex}")
            await asyncio.sleep(5)
            print(f"Catch from main loop after wait: {ex}")
        await asyncio.sleep(5)
        #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
       
try:
    asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
except Exception as ex:
    print(f"Catch: {ex}")
finally:
    print(f"finally: ")
    asyncio.new_event_loop()



