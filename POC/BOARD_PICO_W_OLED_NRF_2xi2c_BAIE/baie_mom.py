import urequests

import machine
import time
import utime
import ntptime
import json

import sys
import ubinascii

import random
machine_id = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
#sys.exit()
#machines = {"e6614103e763b337":"a36_cam_mica","e6614103e7739437":"a36_cam_medie"}
time.sleep(2)
from CONNECTWIFI import CONNECTWIFI
wifi = CONNECTWIFI()

from MACHINES import MACHINES
machines = MACHINES()

print(f"This machine: {machines.guid}, {machines.device}")
topic_receive = machines.topic_receive
topic_send = machines.topic_send


lastMotion = 0
#NRF
from machine import SPI
from machine import Pin
time.sleep(0.2)

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

time.sleep(0.2)

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
    global topic_send,machines
    print(f"sendTemperature function called by {sender}")
    #publish(topic_send, f"name:{machines.name}")
    publish(topic_send, f"temperature:{read_temperature()}")
    publish(topic_send, f"humidity:{read_humidity()}")
    publish(topic_send, f"ambient:{read_light()}")
    publish(topic_send, f"dim:{read_dim()}")


def discovery(sender):
    global topic_send,machines,lastMotion
    print(f"Discovery function called by {sender}")
    publish(topic_send, f"device:{machines.device}")
    publish(topic_send, f"name:{machines.name}")
    #if (time.time() - lastMotion ) / 60 < 5:
    publish(topic_send, f"lastmotion:{lastMotion}")
    sendTemperature("Discovery")

def sub_cb(topic, msg):
    global light,last_run_time_send,light_pwm #,topic
    
    
    print(f"Topic: {topic}; Mesaj: {msg}")
    
    
    
    if topic_receive == bytearray(topic,'UTF-8'):
        print("Matched topic")
        #print("Lights")
        if msg == b'true':
            light.on()
            print("Lights ON")
        elif msg == b'false':
            light.off()
            print("Lights OFF")
            #publish('picow/frompico', f"Received:{msg}")
        elif msg == b'discovery':
            print("discovery")
            locals()[msg.decode()]("mqtt")
        elif msg == b'sendTemperature':
            #last_run_time_send = 0
            locals()[msg.decode()]("mqtt")
            
        #elif: msg.contains
        else:
            try:
                command,strValue = msg.decode().split(':')
                value = int(strValue)
                light_pwm.duty_u16(round(value*65534/100))
                #val = int(msg)
                print(f"Command: {command}, Value: {value}")
            except:# ex as Exception:
                #pass
                #print("Error parsing, {ex}")
                print("Err")

    elif str(topic)[str(topic).find('/')+1:str(topic).find('/')+2] == '*' and str(topic)[2:str(topic).find('/')] == str(topic_receive)[0:str(topic_receive).find('/')]:
        print("broadcast")
        try:
            locals()[msg.decode()]("mqtt")
        except:
            print(f"Cannot decode function name: {msg}")
    else:
        print(f"Other {topic}: {str(topic)[str(topic).find('/')+1:str(topic).find('/')+2]}")
 
client.set_callback(sub_cb)
client.connect()

client.subscribe(topic = topic_receive)
client.subscribe(topic = "to/#")
print(f"Subscribed to: {topic_receive}")
#client.subscribe(topic = "picow/lights")

import struct
import random


#Update time from NTP

import NTP
from NTP import ro_time_epoch

try:
            
    client.ping()
    sendTemperature("Init")
    discovery("Init")
except Exception as ex:
    print(f"Error sending to MQ: {ex}")
    client.connect()




from machine import Timer
from machine import PWM
from machine import ADC

from dim import Dim
from brightness_map import brightness_map
adc = ADC(26)



#saved settings:
file = open("config.py", "r")
settings = file.read()
settings_dict = json.loads(settings)
humidity_setpoint = int(settings_dict["humidity_setpoint"])

dimSetPoint = int(adc.read_u16()* 233 / 65000)

#analogReadings = []
analogReading = 0
def analogReadings(self):
    global analogReading,motion
    average = 0
    analogReadings = []
    if motion.value() == 1:
        return

    for i in range(20):
        analogReadings.append(int(adc.read_u16()* 233 / 65000))
        analogReadings.pop(0)
        
        #print(f"Instant: {lightReadings[-1]};average: {old_average}")
    #average = 0
    
    for value in analogReadings:
        average = average + value/20
        
    if int(abs(average - analogReading)) > 3:
            #print(f"Update: {int(average)}")
        analogReading = int(average)
#pwm_pin = Pin(15,Pin.OUT)
#pwm_pin.low()

#pwm = PWM(pwm_pin)
#pwm.freq(30000)
#pwm.duty_u16(0)
fade_time_ms=1000
dim = Dim(15,16,0,236,0,230,fade_time_ms)


#led = Pin(25,Pin.OUT)
led = Pin('LED',Pin.OUT)
#led12 = Pin(15,Pin.OUT)
#led12.on()

motion = Pin(22, Pin.IN,Pin.PULL_DOWN)

timer = Timer()
timer_blink = Timer()
timer_check_messages = Timer()




#timer_test.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:timerTest)   # Timer.ONE_SHOT . Period in m

def blinkOnboardLed(timer):
    global led
    led.toggle()
    #if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:

timer_blink.init(period=1000, mode=Timer.PERIODIC, callback = blinkOnboardLed)

time.sleep(0.2)

def dimToOff(timer):
    global dim
    dim.dimToOff()

   

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
timer.init(period=1000, mode=Timer.ONE_SHOT, callback=analogReadings)   # Timer.ONE_SHOT . Period in m

timer_check_messages.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:client.check_msg())   # Timer.ONE_SHOT . Period in m

def motion_sensed(pin):
    global lastMotion
    pin.irq(trigger=0)
    lastMotion = time.time()
    timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)
    print("motion")
    #time.sleep(5)
    pin.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)

motion.irq(trigger=Pin.IRQ_RISING,handler=motion_sensed)


while True:
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_receive) >= 1000:
        last_run_time_receive = tmp
        #received = client.check_msg()

    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 300000:
        last_run_time_send = tmp
        try:
            
            client.ping()
            #publish('fromCMica', f"dt:{str(round(ds.read_temp(ds_id),1 ) )}")
            #publish('fromCMica', f"t:{read_temperature()}")
            #publish('fromCMica', f"h:{read_humidity()}")
            #publish('fromCMica', f"l:{read_light()}")
            #sendTemperature("300s loop")
            
        except Exception as ex:
            print(f"Error sending to MQ: {ex}")
            client.connect()

    
#        publish(topic_send, f"random:{random.randint(0,100)}")

#    pass
    #if motion.value() != 1:
        
        #print("motion timer")
    #    dim.setReqIndex1(dimSetPoint)
           # Timer.ONE_SHOT . Period in m
        
        
    #led.toggle()
#    led12.toggle()
    #time.sleep(0.2)
    



while True:
    #time.sleep(0.5)
    #print(ds.read_temp(ds_id), end=' ')

    #wdt.feed()
    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_receive) >= 3000:
        last_run_time_receive = tmp
        
        publish(topic_send, f"random:{random.randint(0,100)}")
        
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


