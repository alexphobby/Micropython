

#test()

#print(weather.temperature())
from i2c_init import *
from mqtt_as_init import *
from machine import Pin,ADC
from ir_remote_read import ir_remote_read
from my_remotes import *

ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)
#from ir_remote_read_demo import *


#from aremote import NEC_IR, REPEAT
#from machine import Signal

#def cb(data, addr, led):
#    print(f"Addr: {addr} - Data: {data}")

#ir = NEC_IR(ir_pin, cb, True, Pin(8,Pin.OUT))
auto_dim = False
required_lumens = 0

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

from dim import *

dimmer = Dim(pin1=8,fade_time_ms=50)
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
    global lightReading
    if on_demand:
        try:
            print(f"Send on demand message on {my_machine.topic_send}")
            output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(lightReading),"dim":str(0),"lastmotion":0,"autobrightness":0}
            await client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
            return
        except Exception as ex:
            print(f"mqtt_send error: {ex}")
        return
        print("should not run")
    else:
        while True:
            try:
                print(f"Send mqtt message on {my_machine.topic_send}")
                output = {"devicename":str(my_machine.device),"roomname":str(my_machine.name),"devicetype": str(my_machine.devicetype),"features": str(my_machine.features),"temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(0),"lastmotion":0,"autobrightness":0}
                await client.publish(my_machine.topic_send, f'jsonDiscovery:{output}', qos = 0)
                await asyncio.sleep(60)
            except Exception as ex:
                print(f"mqtt_send error: {ex}")
                await asyncio.sleep(60)


async def messages(client):  # Respond to incoming messages
    global dim,auto_dim,lightReading,required_lumens
    while True:
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
            else:
                try:
                    command,strValue = msg.decode().split(':')
                    print(f"Command: {command}, Value: {strValue}, command: {command}")
                    if command == "setAutoBrightness" and strValue == "true":
                        await asyncio.sleep(2)
                        auto_dim = True
                        required_lumens = lightReading
                        print(f"Required: {lightReading}")
                    elif command == "setAutoBrightness" and strValue == "false":
                        auto_dim = False
                        #required_lumens = lightReading
                    #print(locals())
                    else:
                        await locals()[command](strValue)
                except Exception as ex:
                    print(ex)
                    
                    
        await asyncio.sleep(0.5)

from BH1750 import BH1750
bh1750 = BH1750(i2c)

print(f"Lux: {round(bh1750.luminance(bh1750.CONT_HIRES_2)),1}")

lightReadings=[]
lightReading = 0
light = ADC(Pin(0,Pin.IN))
light.atten(ADC.ATTN_11DB)

def get_lightReading():
    global lightReading
    return lightReading

def get_required_lumens():
    global required_lumens
    return required_lumens

async def read_adc():
    global lightReadings, lightReading
    for i in range(0,3):
        lightReadings.append(int(light.read_u16()))
        await asyncio.sleep(0.1)
        
    while True:
        lightReadings.append(int(light.read_u16()))
        lightReadings.pop(0)
        lightReading = round((sum(lightReadings)/len(lightReadings))*0.0252)
        #print(f"TEMT6000: {lightReading}; BH1750:{round(bh1750.luminance(bh1750.CONT_HIRES_2))}")
        #print(f"Lux: {round(bh1750.luminance(bh1750.CONT_HIRES_2),1)}")
        await asyncio.sleep(0.2)
        
        
async def dim_auto():
    global auto_dim
    #brightness_values = len(brightness_map)
    while True:
        print(f"Auto: {auto_dim}; Required_lm: {get_required_lumens()} - lightReading: {lightReading} Dimmer index: {dimmer.index1}")
        if auto_dim and get_lightReading() < get_required_lumens() - 10 and dimmer.index1 < dimmer.max1 - 10:
            print(f"Dim up to: {dimmer.index1 + 10}")
            
            dimmer.setReqIndex1(dimmer.index1 + 10)
            
        elif auto_dim and get_lightReading() > get_required_lumens() + 10 and dimmer.index1 > dimmer.min1+10:
            print(f"Dim down to: {dimmer.index1 - 10}")
            dimmer.setReqIndex1(dimmer.index1 - 10)
        await asyncio.sleep_ms(1000)
            
        
        
async def dim(new_value):
    if "dim" in my_machine.features:
        #print(f"can dim to: {new_value} - {(float(new_value)*242)/100}")
        dimmer.setReqIndex1(int((float(new_value)*dimmer.max_index)/100))
        

async def heartbeat_oled(client):
    global set_temp,ir,weather
    print("heartbeat_oled")
    print(ir)
    s = True
    last_minute = -1 #rtc.datetime()[5]
    
    await client.connect()
    
    if not client.isconnected():
        write_custom_font.set_textpos(oled,20,0)
        write_custom_font.printstring(f'Wait for wifi')
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
            

from asyncio import Event
event = Event()

try:
    asyncio.create_task(messages(client))
    asyncio.create_task(read_adc())
    asyncio.create_task(dim_auto())
    #asyncio.create_task(mqtt_send_temp(client)) #send discovery on interval#
    #asyncio.create_task(heartbeat_oled())
    asyncio.run(heartbeat_oled(client))
    
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()


