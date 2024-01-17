import secrets
from MACHINES import MACHINES

import asyncio
from ubinascii import hexlify
from mqtt_as_slim import MQTTClient
from NTP import *
from WEATHER import *
from machine import Pin

machines = MACHINES()

config = {
    "client_id": "",
    "server": None,
    "port": 0,
    "user": "",
    "password": "",
    "keepalive": 60,
    "ping_interval": 0,
    "ssl": False,
    "ssl_params": {},
    "response_time": 10,
    "clean_init": True,
    "clean": True,
    "max_repubs": 4,
    "will": None,
    "subs_cb": lambda *_: None,
    "wifi_coro": "",
    "connect_coro": "",
    "ssid": None,
    "wifi_pw": None,
    "queue_len": 0,
    "gateway" : False,
}

# Subscription callback
def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
    
# Demonstrate scheduler is operational.
async def heartbeat():
    print("heartbeat")
    s = True
    while True:
        await asyncio.sleep_ms(60000)
        print("heartbeat")
        #led(s)
        #s = not s
        #blink

async def wifi_han(state):
    #led(not state)
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    print("Subscribe to foo")
    await client.subscribe('foo_topic', 1)

async def messages(client):  # Respond to incoming messages
    global dim
    async for topic, msg, retained in client.queue:
        print(f'Received {(topic, msg, retained)}')
        #print(f'Message: {msg.}')
        

async def up(client):  # Respond to connectivity being (re)established
    while True:
        print("Up")
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe("to/#", 1)
        await client.subscribe(machines.topic_receive, 1)  # renew subscriptions
        
        

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

config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True

print("Init WIFI and MQTT Client obj:client")
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)
print("Init NTP Time, obj: ntp")
ntp = NTP(client._sta_if)
print("Init weather, obj: weather")
weather = WEATHER(client._sta_if)




async def main(client):
    print("wait for connect")
    await client.connect()
    #for coroutine in (up, messages):
    asyncio.create_task(up(client))
    asyncio.create_task(messages(client))
    n = 0
    
    while len(weather.weather) == 0:
        await asyncio.sleep(0.2)
        #print('publish', n)
        # If WiFi is down the following will pause for the duration.
#        print(hdc1080.temperature())
#        print(hdc1080.humidity())
    output = {"test"} #{"devicename":str(machines.device),"roomname":str(machines.name),"ip": str(client.ip), "temperature":str(hdc1080.temperature()),"humidity":str(hdc1080.humidity()),"ambient":str(0),"dim":str(dim),"lastmotion":0,"autobrightness":0}
    await client.publish(machines.topic_send, f'jsonDiscovery:{output}', qos = 0)

print("to test, run test()")
asyncio.create_task(heartbeat())
asyncio.create_task(up(client))
asyncio.create_task(messages(client))


def test():
    try:
        asyncio.run(main(client))
    finally:
        pass
        #client.close()  # Prevent LmacRxBlk:1 errors
        #asyncio.new_event_loop()