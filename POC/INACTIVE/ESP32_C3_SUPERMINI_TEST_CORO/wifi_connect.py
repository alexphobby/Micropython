import secrets
from machine import Pin
import time,asyncio
from pushbutton import Pushbutton

blink_time = 100
set_temp = 21.0

async def wifi_connect(ssid=secrets.SSID, pwd=secrets.PASSWORDS[0]):
    global blink_time
    import network
    sta_if = network.WLAN(network.STA_IF)
    time.sleep(1)
    while not sta_if.isconnected():
        #blink_time = 100
        try:
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(ssid, pwd)
            await asyncio.sleep_ms(10000)
            #time.sleep(10)
        except:
            print("err")
            #pass
    blink_time = 1000
    print('network config:', sta_if.ifconfig())

led = Pin(8,Pin.OUT,value = 1)

s = True


async def blink():
    global s,blink_time
    while True:
        s = not s
        led.value(s)
        await asyncio.sleep_ms(blink_time)





from mqtt_as import MQTTClient, config

dim = 0
from MACHINES import MACHINES
machines = MACHINES()



from hdc1080_util import hdc1080_util
hdc1080 = hdc1080_util()


from ssd1306 import SSD1306_I2C
#from machine import Pin, I2C, SPI

#import struct
import writer
import freesans20

#display i2c scan= [60]
oled = SSD1306_I2C(128, 64, hdc1080.i2c)
oled.fill(0)

write_custom_font = writer.Writer(oled, freesans20)

write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring("Welcome! ")
oled.show()


config['server'] = secrets.MQTT_SERVER  # Change to suit
config['ssid'] = 'AlxPHome'
config['wifi_pw'] = '741852963'

config['user'] = secrets.MQTT_USERNAME
config['password'] = secrets.MQTT_PASSWORD

config['client_id'] = machines.device
config["port"]= secrets.MQTT_PORT
config["ssl"]= secrets.MQTT_SSL
config["ssl_params"] = secrets.MQTT_SSL_PARAMS
config["queue_len"] = secrets.MQTT_QUEUE_LENGTH
config['keepalive'] = secrets.MQTT_KEEP_ALIVE


async def heartbeat():
    global set_temp
    s = True
    while True:
        
        oled.fill(0)
        write_custom_font.set_textpos(oled,10,0)
        write_custom_font.printstring(f'{hdc1080.temperature()} C')
        
        write_custom_font.set_textpos(oled,10,60)
        write_custom_font.printstring(f'  {hdc1080.humidity()} %   ')
        
        
        write_custom_font.set_textpos(oled,40,0)
        write_custom_font.printstring(f'Set: {set_temp} C  ')
        #oled.drawCircle(50, 50, 10, WHITE)
        oled.show()
        await asyncio.sleep_ms(50000)

def update_temp(new_val):
    global set_temp
    
    print(f"Set: {set_temp}; New: {new_val:.1f}")
    
    while set_temp > new_val + 0.1 or set_temp < new_val - 0.1 :
        
        if set_temp > new_val:
            set_temp -= 0.2
        else:
            set_temp += 0.2
        
        
        print(f"Print: {set_temp:.1f}")
        write_custom_font.set_textpos(oled,40,0)
        write_custom_font.printstring(f'Set: {set_temp:.1f} C  ')
        oled.show()
        



async def messages(client):  # Respond to incoming messages
    global dim
    async for topic, msg, retained in client.queue:
        #print(f'Received {(topic, msg, retained)}')
        #print(f'Message: {msg.}')
        #print(client.ip)
        if (msg == 'discovery'):
            
            output = {"devicename":str(machines.device),"roomname":str(machines.name),"ip": str(client.ip), "temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(dim),"lastmotion":0,"autobrightness":0}
            await client.publish(machines.topic_send, f'jsonDiscovery:{output}', qos = 0)
            print(f'Discovery, topic: {machines.topic_send}; Sent: {output}')
        elif topic == machines.topic_receive:
            print(f'Matched topic: {topic}; Received: {msg}')
            command,strValue = msg.decode().split(':')
            print(f"Command: {command}, Value: {strValue}")
            if command == "lights":
                intValue = int(strValue)
                dim = intValue
                if intValue > 50:
                    print("off")
                    led.off()
                else:
                    print("on")
                    led.on()
                    
        #except ex as Exception:
        #    print(f"err: {ex}")


async def up(client):  # Respond to connectivity being (re)established
    while True:
        print("client up function")
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe("to/#", 1)
        await client.subscribe(machines.topic_receive, 1)  # renew subscriptions
        print(f"Subscribed to topic: {machines.topic_receive}")




async def main(client):
    global dim
    await client.connect()
    #for coroutine in (up, messages):
    #    asyncio.create_task(coroutine(client))
    asyncio.create_task(up(client))
    asyncio.create_task(messages(client))


    n = 0
    while True:
        
        #print('publish', n)
        # If WiFi is down the following will pause for the duration.
#        print(hdc1080.temperature())
#        print(hdc1080.humidity())
        output = {"devicename":str(machines.device),"roomname":str(machines.name),"ip": str(client.ip), "temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(dim),"lastmotion":0,"autobrightness":0}
        
        await client.publish(machines.topic_send, f'jsonDiscovery:{output}', qos = 0)
        await asyncio.sleep(60)
        

MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

pin1 = Pin(5, Pin.IN, Pin.PULL_DOWN)  # Pushbutton to gnd
pin2 = Pin(10, Pin.IN, Pin.PULL_DOWN)  # Pushbutton to gnd
pb1 = Pushbutton(pin1,suppress=True)
pb2 = Pushbutton(pin2,suppress=True)
pb1.release_func(print, ("SHORT",))
pb1.double_func(print, ("DOUBLE",))
pb1.long_func(print, ("LONG",))
    
async def increase(val):
    #global set_temp
    #set_temp += val
    print(f"Set temp: {set_temp+ val}")
    update_temp(set_temp + val )
    
    
    
    
pb1.press_func(increase, (0.2,))  # Note how function and args are passed
#pb2.press_func(toggle, (led,))  # Note how function and args are passed

#asyncio.create_task(wifi_connect())
asyncio.create_task(heartbeat())

asyncio.create_task(main(client))


asyncio.run(blink())

#do_connect(secrets.SSID,secrets.PASSWORDS[0])


