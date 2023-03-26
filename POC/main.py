import network
import urequests

import secrets

import time
import utime
import ntptime

import sys
import ubinascii
machine_id = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
#sys.exit()
#machines = {"e6614103e763b337":"a36_cam_mica","e6614103e7739437":"a36_cam_medie"}


class MACHINES:
    
    def __init__(self):
        self.guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
        
        if self.guid == "e6614103e763b337":
            self.device = "a36_cam_mica"
            
        elif self.guid == "e6614103e7739437":
            self.device = "a36_cam_medie"
            
        else:
            print("Machine not defined")
            
        self.topic_receive = f"to_{self.device}"
        self.topic_send = f"from_{self.device}"
            
        print(f"Topics: Receiving:{self.topic_receive}; Sending:{self.topic_send}")


machines = MACHINES()
topic_receive = machines.topic_receive
topic_send = machines.topic_send
#NRF
from machine import SPI
from machine import Pin
time.sleep(2)

try: 
    from nrf24l01 import NRF24L01
    import ustruct as struct

    spi = SPI(1)
    csn = Pin(13)
    ce=Pin(12)
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    _RX_POLL_DELAY = const(15)
    _SLAVE_SEND_DELAY = const(10)
    pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

except:
    print("no nrf")
#led = Pin('LED',Pin.OUT)





            
            

#DS
try:
    import onewire,ds18x20
    ds_data = Pin(14)
    # create the onewire object
    ds = ds18x20.DS18X20(onewire.OneWire(ds_data))
    ds_id = ds.scan()[0]
    # print('found devices:', roms)

    # loop 10 times and print all temperatures
    ds.convert_temp()
    time.sleep_ms(750)
    ds.read_temp(ds_id)
except:
    print("no ds")

from HDC1080 import HDC1080

from machine import WDT
from machine import Pin,PWM
print(machine.reset_cause())

time.sleep(3)

#wdt = WDT(timeout=8000)
#wdt.feed()

try:
    i2c = machine.I2C(0,scl=Pin(1),sda=Pin(0))
except:
    print("no i2c")
    
try:
    from BH1750 import BH1750
    bh1750 = BH1750(i2c)

except:
    print("no light sensor")


try:
    hdc1080 = HDC1080(i2c)
    print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
    print(f"Humidity: {int(hdc1080.read_humidity())}")


except:
    print("no humidity")
    
def read_light():
    try:
        read_1 = round(bh1750.luminance(bh1750.CONT_HIRES_2),1)
        time.sleep_ms(50)
        read_2 = round(bh1750.luminance(bh1750.CONT_HIRES_2),1)
        time.sleep_ms(50)
        read_3 = round(bh1750.luminance(bh1750.CONT_HIRES_2),1)
        return int((read_1+read_2+read_3)*10/3)
    
    except:
        return -1

ambient_light = read_light()
print(f"Lux: {ambient_light}")






def read_temperature():
    try:
        return round(hdc1080.read_temperature(celsius=True),1)
    except:
        return -1

def read_humidity():
    try:
        return int(hdc1080.read_humidity())
    except:
        return -1

def read_dim():
    global light_pwm
    
    return int(light_pwm.duty_u16()*100/65534)

#ds_pwr = Pin(15,Pin.OUT)
#ds_pwr.on()
time.sleep(0.1)


#for rom in roms:

#for i in range(10):
#    print(ds.read_temp(ds_id), end=' ')
#    time.sleep(1)



light = machine.Pin(16,machine.Pin.OUT)
light_pwm = PWM(light)


wlan = network.WLAN(network.STA_IF)
time.sleep(2)
wlan.active(True)

#wlan.config(hostname='Pico')
#wlan.config(reconnects=3)

#if not wlan.active():
#    print("Activating wifi")
#    wlan.active(True)
    
#    time.sleep(3)
    #wdt.feed()

#print(wlan.scan())
#//wlan.connect(secrets.SSID, secrets.PASSWORD)


hotspots = []
hotspot = ""
while not wlan.isconnected():
    print(f"Wlan not connected, wlan status = {wlan.status()}")
    #define CYW43_LINK_DOWN (0)
    #define CYW43_LINK_JOIN (1)
    #define CYW43_LINK_NOIP (2)
    #define CYW43_LINK_UP (3)
    #define CYW43_LINK_FAIL (-1)
    #define CYW43_LINK_NONET (-2)
    #define CYW43_LINK_BADAUTH (-3)

    try:
        if wlan.status() == 1: # after wlan.active(True)
            print("Joining")
            time.sleep(2)
        
        if wlan.status() != 2 : # after wlan.active(True)
            print(f"wlan status = {wlan.status()}")
            hotspots = []
            while len(hotspots) == 0:
                hotspots = wlan.scan()
                print(hotspots)
            
            for hotspot in hotspots:
                print(f"Trying to connect to: {str(hotspot[0])}, current status = {wlan.status()}")
                wlan.connect(hotspot[0], secrets.PASSWORD)
                time.sleep(5)
                if wlan.status()==1:
                    print(f"Connecting to {str(hotspot[0])}")
                    time.sleep(3)
                if wlan.status() == -2:
                    print(f"Cannot connect to: {str(hotspot[0])}")
                if wlan.status() == -3:
                    print(f"Cannot connect to: {str(hotspot[0])}, bad auth")
                if wlan.status() == 2:
                    print(f"Wait to connect to: {str(hotspot[0])}")
                    time.sleep(3)
                if wlan.status() == 3:
                    print(f"Connected to: {str(hotspot[0])}")
                    break
                
            #wlan.connect(secrets.SSID, secrets.PASSWORD)
            #wdt.feed()
            #time.sleep(2)

    except:
        print(f"Err - Cannot connect to {hotspot[0]}, current status = {wlan.status()}")


#res = urequests.get("https://google.com")
last_run_time_send = 0
last_run_time_receive = 0


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

def publish(topic_send, value):
    global client
    #print(topic)
    #print(f"Sending to {topic_send} Message: {value}")
    client.publish(topic_send, value)
    #print("publish Done")


client = mqttClient(True,machines.device)
def sendTemperature(sender):
    global topic_send
    print(f"sendTemperature function called by {sender}")
    publish(topic_send, f"temperature:{read_temperature()}")
    publish(topic_send, f"humidity:{read_humidity()}")
    publish(topic_send, f"ambient:{read_light()}")
    publish(topic_send, f"dim:{read_dim()}")
    
def sub_cb(topic, msg):
    global light,last_run_time_send,light_pwm #,topic
    
    
    print(f"Topic: {topic_receive}; Mesaj: {msg}")
    if topic_receive == bytearray(topic,'UTF-8'):
        #print("Lights")
        if msg == b'true':
            light.on()
            print("Lights ON")
        elif msg == b'false':
            light.off()
            print("Lights OFF")
            #publish('picow/frompico', f"Received:{msg}")
        elif msg == b'sendTemperature':
            #last_run_time_send = 0
            locals()[msg.decode()]("mqtt")
            
        #elif: msg.contains
        else:
            try:
                command,strValue = msg.decode().split(':')
                value = int(strValue)
                light_pwm.duty_u16(int(value*65534/100))
                #val = int(msg)
                print(f"Command: {command}, Value: {value}")
            except:# ex as Exception:
                #pass
                #print("Error parsing, {ex}")
                print("Err")

    elif topic_receive == b'picow/humidity':
        print("Humidity")
    else:
        print("Other")
 
client.set_callback(sub_cb)
client.connect()

client.subscribe(topic = topic_receive)
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



try:
            
    client.ping()
    sendTemperature("Init")
except Exception as ex:
    print(f"Error sending to MQ: {ex}")
    client.connect()
            
while True:
    #time.sleep(0.5)

    while not wlan.isconnected():
        print("Not Connected")
        time.sleep(1)
        
        try:
            print(f"Trying to connect to: {secrets.SSID}")
            wlan.connect(secrets.SSID, secrets.PASSWORD)
            wdt.feed()
        except:
            print("Cannot connect")

    
    #print(ds.read_temp(ds_id), end=' ')

    #wdt.feed()
    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_receive) >= 1000:
        last_run_time_receive = tmp
        received = client.check_msg()
        tmp_ambient_light = read_light()
        #print(f"Ambient instant read: {tmp_ambient_light}")
        if abs(ambient_light - tmp_ambient_light) >5:
            #print(f"Ambient changed, instant read: {tmp_ambient_light}, old value: {ambient_light}")
            #time.sleep(0.5)
            ambient_light = tmp_ambient_light
            sendTemperature("ambient light changed")
        
    
    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 300000:
        last_run_time_send = tmp
        try:
            
            client.ping()
            #publish('fromCMica', f"dt:{str(round(ds.read_temp(ds_id),1 ) )}")
            #publish('fromCMica', f"t:{read_temperature()}")
            #publish('fromCMica', f"h:{read_humidity()}")
            #publish('fromCMica', f"l:{read_light()}")
            sendTemperature("300s loop")
            
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






while True:
    if nrf.any():
        #print("any")
        while nrf.any():
            #print("w")
            buf = nrf.recv()
            led.toggle()
            led_state = struct.unpack("i", buf)
            print("received:", led_state)
            utime.sleep_ms(_RX_POLL_DELAY)

            # Give master time to get into receive mode.
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            #nrf.stop_listening()
            try:
                #nrf.send(struct.pack("i", 50))
                pass
            except OSError:
                pass
            #print("sent response")
            #nrf.start_listening()

