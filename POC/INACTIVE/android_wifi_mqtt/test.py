import network
import urequests

import secrets
import time
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print(wlan.scan())


wlan.connect(secrets.SSID, secrets.PASSWORD)
print(wlan.isconnected())


#astronauts = urequests.get("http://api.open-notify.org/astros.json").json()
#number = astronauts['number']

#for i in range(number):
#    print(astronauts['people'][i]['name'])

#res = urequests.get("https://google.com")

from mqtt import MQTTClient

def connectMQTT(ssl_enabled = False):
    client = MQTTClient(client_id=b"kudzai_raspberrypi_picow",
    server=b"fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud",
    port=8883,
    user=b"apanoiu",
    password=b"Mqtt741852",
    keepalive=7200,
    ssl=ssl_enabled,
    ssl_params={'server_hostname':'fc284e6f2eba4ea29babdcdc98e95188.s1.eu.hivemq.cloud'}
    )

    client.connect()
    return client

def publish(topic, value):
    #print(topic)
    #print(value)
    client.publish(topic, value)
    #print("publish Done")


client = connectMQTT(True)

def sub_cb(topic, msg): 
   print(f"Mesaj: {msg}") 
 
client.set_callback(sub_cb)
client.connect()

client.subscribe(topic = 'picow/humidity')
import struct
import random

while True:
    time.sleep(1)
    received = client.check_msg()
    value = random.random()
    publish('picow/frompico', str(value)  )
    
    if received:
        print(f"Received: {received}")
    
print("nu")
while True:
#Read sensor data
    
    print(value)
    #publish as MQTT payload
    
    #publish('picow/temperature', sensor_reading + 1)
    #publish('picow/pressure', sensor_reading + 2)
    #delay 5 seconds
    time.sleep(5)
