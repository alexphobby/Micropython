
import secrets
import asyncio
from mqtt_as import MQTTClient, config

from machine import Pin
led = Pin(8,Pin.OUT)
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

# Subscription callback
def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    
# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(5000)
        oled.fill(0)
        write_custom_font.set_textpos(oled,10,0)
        write_custom_font.printstring(f'{hdc1080.temperature()} C   ')
        write_custom_font.set_textpos(oled,40,0)
        write_custom_font.printstring(f'{hdc1080.humidity()} %   ')
        #oled.drawCircle(50, 50, 10, WHITE)
        oled.show()

        #led(s)
        #s = not s
        #blink

async def wifi_han(state):
    #led(not state)
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('foo_topic', 1)

async def messages(client):  # Respond to incoming messages
    global dim
    async for topic, msg, retained in client.queue:
        #print(f'Received {(topic, msg, retained)}')
        #print(f'Message: {msg.}')
        print(client.ip)
        if (msg == 'discovery'):
            
            output = {"devicename":str(machines.device),"roomname":str(machines.name),"ip": str(client.ip), "temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(dim),"lastmotion":0,"autobrightness":0}
            await client.publish(machines.topic_send, f'jsonDiscovery:{output}', qos = 0)
            print(f'Topic: {machines.topic_send}; Sent: {output}')
        else:
            print(f'Topic: {topic}; Received: {msg}')
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
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe("to/#", 1)
        await client.subscribe(machines.topic_receive, 1)  # renew subscriptions
        

async def main(client):
    global dim
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))
    n = 0
    while True:
        await asyncio.sleep(60)
        #print('publish', n)
        # If WiFi is down the following will pause for the duration.
#        print(hdc1080.temperature())
#        print(hdc1080.humidity())
        output = {"devicename":str(machines.device),"roomname":str(machines.name),"ip": str(client.ip), "temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(dim),"lastmotion":0,"autobrightness":0}
        await client.publish(machines.topic_send, f'jsonDiscovery:{output}', qos = 0)
        #await client.publish(machines.topic_send, f'{hdc1080.temperature()}', qos = 1)
        #n += 1

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True
#import time
#wlanPower = Pin(23,Pin.OUT)
#wlanPower.off()
#time.sleep(1)
#wlanPower.on()
#time.sleep(1)

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)
asyncio.create_task(heartbeat())

try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
    asyncio.new_event_loop()
    