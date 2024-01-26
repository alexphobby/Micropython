

#test()

#print(weather.temperature())
from i2c_init import *
#from mqtt_as_init import *
from machine import Pin
from ir_remote_read import ir_remote_read
from my_remotes import *
from MACHINES import *
import asyncio
ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)
#from ir_remote_read_demo import *


#from aremote import NEC_IR, REPEAT
#from machine import Signal

#def cb(data, addr, led):
#    print(f"Addr: {addr} - Data: {data}")

#ir = NEC_IR(ir_pin, cb, True, Pin(8,Pin.OUT))

def ir_callback(remote,command,combo):
    print((remote,command))
    try:
        print(remote_samsung[combo])
        return
    except:
        pass
    
    try:
        print(remote_tiny[combo])
    except:
        pass
    #print((remote,command))
    
    
ir = ir_remote_read(ir_pin,ir_callback)

from ssd1306 import SSD1306_I2C
from writer import Writer
import consolas16

#Init Oled display i2c scan= [60]
oled = SSD1306_I2C(128, 64, i2c)

#ir_remote_read(ir_pin,ir_callback)
from machine import RTC
rtc = RTC()

##init HDC temperature sensor, already we have i2c
from hdc1080_util import hdc1080_util
hdc1080 = hdc1080_util(i2c)

oled.fill(0)
write_custom_font = Writer(oled, consolas16)

#write_custom_font = writer.Writer(oled, myfont) #freesans20
write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring(f"Loading...")
oled.show()

async def mqtt_send_temp(client,on_demand = False):
    global sender_count
    if on_demand:
        sender_count +=1
        try:
            print(f"Send on demand message on {my_machine.topic_send}")
            output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(0),"lastmotion":0,"autobrightness":0,"count":sender_count}
            await client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
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
                await client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
                await asyncio.sleep(60)
            except Exception as ex:
                print(f"mqtt_send error: {ex}")
                await asyncio.sleep(60)


async def messages(client):  # Respond to incoming messages
    global dim
    while True:
        if client.broker_up():
            print(f"MQTT connected: {client.broker_up()}")
        else:
            print("MQTT not connected")
            client.connect(True)
            
        
        async for topic, msg, retained in client.queue:
            print(f'Received {(topic, msg, retained)}')
            #print(f'Message: {msg.}')
            if msg == "discovery":
                print("Send discovery result")
                await (mqtt_send_temp(client,True))
            elif msg == "update" and topic == my_machine.topic_receive:
                print("Update from GitHub")
                import gc
                gc.collect
                import update
                update.update()
        await asyncio.sleep(0.5)


async def heartbeat_oled(client):
    global set_temp,ir,weather
    print("heartbeat_oled")
    print(ir)
    s = True
    last_minute = -1 #rtc.datetime()[5]
    
    oled.fill(0)
    oled.show()
    if not client.isconnected():
        write_custom_font.set_textpos(oled,20,0)
        write_custom_font.printstring(f'Wait for wifi')
        oled.show()
        await client.connect()
    else:
        write_custom_font.set_textpos(oled,20,0)
        write_custom_font.printstring(f'Heartbeat connected')
        oled.show()
        
        
    while True:
        
        if last_minute == rtc.datetime()[5]:
            write_custom_font.set_textpos(oled,0,0)
            #write_custom_font.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}     ')
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
            await asyncio.sleep_ms(800)
            
async def err():
    while True:
        print("err")
        await asyncio.sleep_ms(20000)
        raise Exception("raise ex")
    
from asyncio import Event
event = Event()

t = None
tasks = []
sender_count = 0





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



from CONNECTWIFI import *
wifi = CONNECTWIFI()


def messages(topic, msg):  # Respond to incoming messages
    global dim
    print(f'Received {(topic, msg)}')
        #print(f'Message: {msg.}')
    if str(msg) == "discovery":
        print("Send discovery result")
        #await (mqtt_send_temp(client,True))
    elif str(msg) == "update" and topic == my_machine.topic_receive:
        print("Update from GitHub")
        import gc
        gc.collect
        import update
        update.update()
    time.sleep(0.5)


from MACHINES import *
my_machine = MACHINES()

time.sleep(1)
client = mqttClient(True,my_machine.device)
client.set_callback(messages)
client.connect()

client.subscribe(topic = my_machine.topic_receive)

while True:
    client.ping()
    client.check_msg()

    print("ping")
    time.sleep(2)

async def main():
    
    #thb = asyncio.create_task(heartbeat(60))
    #tup = asyncio.create_task(up(client))

       #loop = asyncio.get_event_loop()
    #tmsg = asyncio.create_task(messages(client))
    #terr =  asyncio.create_task(err())
       
            
            
        #asyncio.create_task(mqtt_send_temp(client)) #send discovery on interval#
    #toled = asyncio.create_task(heartbeat_oled(client))
    while True:
        try:
            await asyncio.sleep(5)
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring(f"loop     ")
            oled.show()

            #await mqtt_send_temp(client,True)
            #if thb.done():
             #   print("HB is done")
              #  thb=None
               # gc.collect()
                #thb = asyncio.create_task(heartbeat(60))
             
            #if tup.done():
             #   print("UP is done")
              #  tup=None
               # gc.collect()
                #tup = asyncio.create_task(up(client))
                
            #if tmsg.done():
             #   print("MSG is done")
              #  tmsg=None
               # gc.collect()
                #tmsg = asyncio.create_task(messages(client))
            
            
            #if toled.done():
             #   print("ERR is done")
              #  toled=None
               # gc.collect()
                #toled = asyncio.create_task(heartbeat_oled(client))
             
                
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
    #client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()


