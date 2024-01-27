import network
import urequests

import secrets

import time
import ntptime

import sys

#sys.exit()
import machine
from machine import Pin,PWM


#DS
import onewire,ds18x20
from BH1750 import BH1750
from HDC1080 import HDC1080
i2c = machine.I2C(0,scl=Pin(1),sda=Pin(0))
bh1750 = BH1750(i2c)
print(f"Lux: {round(bh1750.luminance(bh1750.CONT_HIRES_2)),1}")
hdc1080 = HDC1080(i2c)
print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
print(f"Humidity: {int(hdc1080.read_humidity())}")

#ds_pwr = Pin(15,Pin.OUT)
#ds_pwr.on()
time.sleep(0.1)

ds_data = Pin(14)
# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(ds_data))

# scan for devices on the bus
ds_id = ds.scan()[0]
# print('found devices:', roms)

# loop 10 times and print all temperatures
ds.convert_temp()
time.sleep_ms(750)
ds.read_temp(ds_id)
#for rom in roms:

#for i in range(10):
#    print(ds.read_temp(ds_id), end=' ')
#    time.sleep(1)



light = machine.Pin(16,machine.Pin.OUT)
light_pwm = PWM(light)


wlan = network.WLAN(network.STA_IF)
#wlan.config(hostname='Pico')
#wlan.config(reconnects=3)

if not wlan.active():
    print("Activating wifi")
    wlan.active(True)
    time.sleep(5)

#print(wlan.scan())
#//wlan.connect(secrets.SSID, secrets.PASSWORD)



while not wlan.isconnected():
    #define CYW43_LINK_DOWN (0)
#define CYW43_LINK_JOIN (1)
#define CYW43_LINK_NOIP (2)
#define CYW43_LINK_UP (3)
#define CYW43_LINK_FAIL (-1)
#define CYW43_LINK_NONET (-2)
#define CYW43_LINK_BADAUTH (-3)
    if wlan.status()==1:
        print("Connecting...")
        time.sleep(5)
    
    try:
        if wlan.status()==0: # after wlan.active(True)
            print(f"Trying to connect to: {secrets.SSID}, current status = {wlan.status()}")
            time.sleep(1)
            wlan.connect(secrets.SSID, secrets.PASSWORD)
            time.sleep(5)

    except:
        print(f"Cannot connect, current status = {wlan.status()}")

if wlan.isconnected():
    print(f"Connected to LAN: {wlan.isconnected()}")    

#astronauts = urequests.get("http://api.open-notify.org/astros.json").json()
#number = astronauts['number']

#for i in range(number):
#    print(astronauts['people'][i]['name'])

#res = urequests.get("https://google.com")
last_run_time_send = 0
last_run_time_receive = 0


from mqtt import MQTTClient

def mqttClient(ssl_enabled = False):
    client = MQTTClient(client_id=b"alexp_picow",
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

def publish(topic, value):
    global client
    #print(topic)
    #print(value)
    client.publish(topic, value)
    #print("publish Done")


client = mqttClient(True)
def sendTemperature():
    print("sendTemperature function")
    
def sub_cb(topic, msg):
    global light,last_run_time_send,light_pwm
    
    
    print(f"Topic: {topic}; Mesaj: {msg}")
    if topic == b'toCameraMica':
        #print("Lights")
        if msg == b'true':
            light.on()
            print("Lights ON")
        elif msg == b'false':
            light.off()
            print("Lights OFF")
            #publish('picow/frompico', f"Received:{msg}")
        elif msg == b'sendTemperature':
            last_run_time_send = 0
            locals()[msg.decode()]()
            
        #elif: msg.contains
        else:
            try:
                command,strValue = msg.decode().split(':')
                value = int(strValue)
                light_pwm.duty_u16(int(value*65534/100))
                #val = int(msg)
                print(f"Command: {command}, Value: {value}")
            except ex as Exception:
                #pass
                print("Error parsing, {ex}")

    elif topic == b'picow/humidity':
        print("Humidity")
    else:
        print("Other")
 
client.set_callback(sub_cb)
client.connect()

client.subscribe(topic = 'toCameraMica')
#client.subscribe(topic = "picow/lights")

import struct
import random


#Update time from NTP

print("Get ntp time")
err=True
retry_count = 3
while err or retry_count == 0:
    try:
        ntptime.settime()
        print(f"NTP OK, Time: {time.localtime()}")
        err=False
    except:
        retry_count-=1
        print(f"err ntp, retry count: {retry_count}")
        
while True:
    #time.sleep(0.5)

    while not wlan.isconnected():
        
        time.sleep(5)
        try:
            print(f"Trying to connect to: {secrets.SSID}")
            wlan.connect(secrets.SSID, secrets.PASSWORD)
            #time.sleep(2)

        except:
            print("Cannot connect")

    
    #print(ds.read_temp(ds_id), end=' ')

    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_receive) >= 1000:
        last_run_time_receive = tmp
        received = client.check_msg()
        
    
    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 30000:
        last_run_time_send = tmp
        ds.convert_temp()
        time.sleep_ms(750)
        try:
            client.ping()
            publish('fromCameraMica', str(round(ds.read_temp(ds_id),1 ) ))
            
        except Exception as ex:
            print(f"Error sending to MQ: {ex}")
            client.connect()
    #value = random.random()
    #print(".")
    
    #value = str(time.localtime())
    
    
    

    


    #print(f"Received: {received}")
    
print("nu")
while True:
#Read sensor data
    
    #print(value)
    #publish as MQTT payload
    
    #publish('picow/temperature', sensor_reading + 1)
    #publish('picow/pressure', sensor_reading + 2)
    #delay 5 seconds
    time.sleep(0.1)
