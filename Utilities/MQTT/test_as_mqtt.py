import secrets
from mqtt_as import MQTTClient, config

from machine import Pin
led = Pin("LED",Pin.OUT)

from MACHINES import MACHINES
machines = MACHINES()

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
import asyncio

# Subscription callback
def sub_cb(topic, msg, retained):
    print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')

# Demonstrate scheduler is operational.
async def heartbeat():
    s = True
    while True:
        await asyncio.sleep_ms(500)
        led(s)
        s = not s

async def wifi_han(state):
    led(not state)
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('foo_topic', 1)

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print(f'Received {(topic, msg, retained)}')

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('test', 1)  # renew subscriptions

async def main(client):
    await client.connect()
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))
    n = 0
    while True:
        await asyncio.sleep(5)
        print('publish', n)
        # If WiFi is down the following will pause for the duration.
        await client.publish('result', '{}'.format(n), qos = 1)
        n += 1

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
    