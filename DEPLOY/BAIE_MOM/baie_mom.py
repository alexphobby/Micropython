from machine import Pin
import time
from machine import Timer
from machine import PWM
from machine import ADC
import machine # import deepsleep,reset_cause,DEEPSLEEP_RESET
from HDC1080 import HDC1080
from config import config
from dim import Dim
from brightness_map import brightness_map
import micropython #import alloc_emergency_exception_buf
import sys
import ubinascii

import random

micropython.alloc_emergency_exception_buf(100)
#Pinout:
#PIN26: ADC potentiometer for dimming
#PIN22: Digital IN motionPIR
#PIN25: Digital OUT PWM LED


print(machine.reset_cause())
time.sleep(4)


#if machine.reset_cause() == machine.DEEPSLEEP_RESET:
#    print('woke from a deep sleep')
#else:
#import network
#wlan = network.WLAN(network.STA_IF)
#wlan.active(True)

#time.sleep(2)
#wlan.deinit()

#time.sleep(2)
print("Setting Pins")
led = Pin("LED",Pin.OUT)

#radio = Pin(23,Pin.OUT)
#radio.off()
time.sleep(2)

adc = ADC(26)
motionPIR = Pin(22, Pin.IN,Pin.PULL_DOWN)
motionRADAR = Pin(21, Pin.IN,Pin.PULL_DOWN)
fan = Pin(20,Pin.OUT)

dimSetPoint = int(config["light_value"])
humiditySetPoint = int(config["humidity_setpoint"])

fade_time_ms=4000
dim = Dim(19,16,0,236,0,230,fade_time_ms)


fan.off()




#machine.deepsleep(10000)


#dimSetPoint = int(adc.read_u16()* 233 / 65000)

try:
    i2c = machine.I2C(0,scl=Pin(1),sda=Pin(0))
except:
    print("no i2c")
    
try:
    hdc1080 = HDC1080(i2c)
    print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
    print(f"Humidity: {int(hdc1080.read_humidity())}")


except:
    print("no humidity")

#analogReadings = []
analogReading = 0
def analogReadings(self):
    global analogReading,motionPIR
    average = 0
    analogReadings = []
    if motionPIR.value() == 1:
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


timer = Timer()
timer_blink = Timer()
timer_motionPIR = Timer()
timer_humidity = Timer()
timer_fan = Timer()


def stopFan(timer):
    global fan
    fan.off()
    print("fan off")
    
def runFan():
    global fan,timer_fan
    fan.on()
    print("fan on")
    timer_fan.init(period=120000, mode=Timer.ONE_SHOT, callback=stopFan)

def blinkOnboardLed(timer):
    global led,adc,dimSetPoint
    led.toggle()
    #print(motionPIR.value())
    if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:
        pass

sensed=False

def dimToOff(timer):
    global dim
    if motionRADAR.value == 0:
        print("Dim To off")
        dim.dimToOff()
    else:
       timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)


def onSensed(irqpin):
    global sensed, timer,dimToOff,dimSetPoint,motionPIR,motionRADAR
    motionPIR.irq(trigger=0)
    motionRADAR.irq(trigger=0)
    print(f"IRQ {irqpin}")
    
    dim.setReqIndex1(dimSetPoint)
    #time.sleep(2)
    
    timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in m
    motionPIR.irq(trigger=Pin.IRQ_RISING, handler=onSensed)
    motionRADAR.irq(trigger=Pin.IRQ_RISING, handler=onSensed)
    
    #timer_motionPIR.init(period=2000, mode=Timer.ONE_SHOT, callback = disableSensed)  #print("sensed timer"))
def readHumidity(firedTimer):
    global hdc1080
    print("readHumidity")
    
    #firedTimer.deinit()
    try:
        if (int(hdc1080.read_humidity()) > humiditySetPoint):
            print("humid")
            runFan()
    except:
        print("Err read humidity")
        
    #print(f"Temp: {round(hdc1080.read_temperature(celsius=True),1)}")
    print(f"Humidity: {int(hdc1080.read_humidity())}")
            

print("Enable Timers ant Interrupts")

timer_blink.init(period=200, mode=Timer.PERIODIC, callback = blinkOnboardLed)
    
motionPIR.irq(trigger=Pin.IRQ_RISING, handler=onSensed) #Pin.IRQ_RISING|Pin.IRQ_FALLING

motionRADAR.irq(trigger=Pin.IRQ_RISING, handler=onSensed) #Pin.IRQ_RISING|Pin.IRQ_FALLING

timer_humidity.init(period=30000, mode=Timer.PERIODIC, callback=readHumidity)   # Timer.ONE_SHOT . Period in m



#time.sleep(2)


#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
#timer.init(period=1000, mode=Timer.ONE_SHOT, callback=analogReadings)   # Timer.ONE_SHOT . Period in m
def read_humidity():
    try:
        return round(hdc1080.read_humidity())
    except:
        return -1

machine_id = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")

from CONNECTWIFI import CONNECTWIFI
wifi = CONNECTWIFI()

from MACHINES import MACHINES
machines = MACHINES()

print(f"This machine: {machines.guid}, {machines.device}")
topic_receive = machines.topic_receive
topic_send = machines.topic_send


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


def discovery(sender):
    global topic_send,machines,lastMotion,autoBrightness
    print(f"Discovery function called by {sender}")
    #temperature = read_temperature()
    humidity = read_humidity()
    #ambient = read_light()
    #dim = read_dim()
    #output = {"devicename":str(machines.device),"roomname":str(machines.name),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(ambient),"dim":str(dim),"lastmotion":lastMotion,"autobrightness":autoBrightness}
    output = {"devicename":str(machines.device),"roomname":str(machines.name),"temperature":str(0),"humidity":str(humidity),"ambient":str(0),"dim":str(0),"lastmotion":0,"autobrightness":0}
    #output = json.loads()
    #publish(topic_send, f"device:{machines.device}")
    #publish(topic_send, f"name:{machines.name}")
    #if (time.time() - lastMotion ) / 60 < 5:
    #publish(topic_send, f"lastmotion:{lastMotion}")
    #sendTemperature("Discovery")
    publish(topic_send, f"jsonDiscovery:{output}")
    print(f"jsonDiscovery:{output}")

def sub_cb(topic, msg):
    global light,last_run_time_send,light_pwm,timer_pid #,topic
    
    
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
            #try:
            if True:
                command,strValue = msg.decode().split(':')
                print(f"Command: {command}, Value: {strValue}")
                if command == "lights":
                    intValue = int(strValue)
                    timer_pid.deinit()
                    setAutoBrightness("false")
                    dim.setReqIndex1(round(intValue*200/100))
                    
                    #print(f"Command: {command}, Value: {strValue}, index: {round(value*200/100)}")                
                if command == "setAutoBrightness":
                    print("setAutoBrightness")
                    locals()[command](strValue)
                    discovery("setAutobrightness")
                    
                
                
                #light_pwm.duty_u16(round(value*65534/100))
                
                #val = int(msg)
            try:
                pass
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
 
 

print("Init MQTT")
try:
    client = mqttClient(True,machines.device)
    client.set_callback(sub_cb)
    client.connect()

    client.subscribe(topic = topic_receive)
    client.subscribe(topic = "to/#")
    print(f"Subscribed to: {topic_receive}")
    discovery("Init")

except:
    print("err mqtt")
    
discovery("Init")
#client.subscribe(topic = "picow/lights")

last_run_time_send = 0
last_run_time_receive = 0

while True:
        if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 30000:
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

while False: #never run
    if motionPIR.value() == 1:
        dim.setReqIndex1(dimSetPoint)
        timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in m
        
        
    #led.toggle()
#    led12.toggle()
    time.sleep(0.2)
    #print(motionPIR.value())
    #time.sleep(0.1)