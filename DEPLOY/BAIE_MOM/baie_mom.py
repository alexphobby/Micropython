#Timer baie
#INT PIR 22
#INT RADAR 21
#ACS switch 20
#LED PWM 19
#I2c 0 & 1
#pwr 3.3v
#pwr disable buckboost(enable to GND)

#Pinout baie:
#brown -
#red +
#blue radar
#white pir
#green sda
#black scl

from machine import Pin
import time
from machine import Timer
from machine import PWM
from machine import ADC
import secrets

import machine # import deepsleep,reset_cause,DEEPSLEEP_RESET

from hdc1080_util import hdc1080_util

from dim import Dim
from brightness_map import brightness_map
import micropython #import alloc_emergency_exception_buf
import sys
import ubinascii

import random

LED_TIMEOUT=1*5 #1 minut
micropython.alloc_emergency_exception_buf(100)
#Pinout:
#PIN26: ADC potentiometer for dimming
#PIN22: Digital IN motionPIR
#PIN25: Digital OUT PWM LED


print(machine.reset_cause())
time.sleep(1)

hdc1080 = hdc1080_util()

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

#adc = ADC(26)
motionPIR = Pin(22, Pin.IN) #,Pin.PULL_DOWN)
motionRADAR = Pin(21, Pin.IN,Pin.PULL_DOWN)
fan = Pin(20,Pin.OUT)

#dimSetPoint = int(config["light_value"])
#humiditySetPoint = int(config["humidity_setpoint"])

fade_time_ms=4000
dim = Dim(19,16,0,236,0,230,fade_time_ms)

fan.off()

def readConfig():
    global settings_dict,dimSetPoint,humiditySetPoint
    import json
    #saved settings: {"humiditySetPoint":"50","dimSetPoint":"10"}
    file = open("config.py", "r")
    settings = file.read()

    settings_dict = json.loads(settings.replace("\'","\""))
    humiditySetPoint = int(settings_dict["humiditySetPoint"])
    dimSetPoint = int(settings_dict["dimSetPoint"])
    print(f"Loaded from settings: Humidity setpoint: {humiditySetPoint}; Light setpoint: {dimSetPoint}")

readConfig()

def updateConfig():
    global settings_dict


    file = open("config.py", "w")
    file.__del__()
    file.close()

    #settings_dict = json.loads(settings)
    settings_dict["humiditySetPoint"] = str(humiditySetPoint)
    settings_dict["dimSetPoint"] = str(dimSetPoint)
    print(f"Save settings: Humidity setpoint: {humiditySetPoint}; Light setpoint: {dimSetPoint}")
    file = open("config.py", "w")
    settings = file.write(str(settings_dict))
    file.close()
    

#machine.deepsleep(10000)


#dimSetPoint = int(adc.read_u16()* 233 / 65000)

#analogReadings = []
#analogReading = 0
#def analogReadings(self):
#    global analogReading,motionPIR
#    average = 0
#    analogReadings = []
#    if motionPIR.value() == 1:
#        return

#    for i in range(20):
#        analogReadings.append(int(adc.read_u16()* 233 / 65000))
#        analogReadings.pop(0)
        
#pwm_pin = Pin(15,Pin.OUT)
#pwm_pin.low()

#pwm = PWM(pwm_pin)
#pwm.freq(30000)
#pwm.duty_u16(0)


timer_led_off = Timer()
timer_blink = Timer()
timer_motionPIR = Timer()
timer_humidity = Timer()
timer_fan = Timer()
timer_check_mqtt = Timer()

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
    #if abs(dimSetPoint - int(adc.read_u16()* 233 / 65000)) > 3:
    #    pass

sensed=False

def dimToOff(timer):
    global dim
    if motionRADAR.value() == 0 and motionPIR.value() == 0:
        print("Dim To off")
        dim.dimToOff()
    else:
       print("Do not dim To off, extend time")
       timer_led_off.init(period=LED_TIMEOUT*1000, mode=Timer.ONE_SHOT, callback=dimToOff)


def onSensed(irqpin):
    global sensed, timer,dimToOff,dimSetPoint,motionPIR,motionRADAR
    motionPIR.irq(trigger=0)
    motionRADAR.irq(trigger=0)
    print(f"IRQ {irqpin}")
    
    dim.setReqIndex1(dimSetPoint)
    #time.sleep(2)
    
    timer_led_off.init(period=LED_TIMEOUT*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in m
    motionPIR.irq(trigger=Pin.IRQ_RISING, handler=onSensed)
    motionRADAR.irq(trigger=Pin.IRQ_RISING, handler=onSensed)
    
    #timer_motionPIR.init(period=2000, mode=Timer.ONE_SHOT, callback = disableSensed)  #print("sensed timer"))
humidityNow = 0
humidityThreshold = 5
def readHumidity(firedTimer):
    global hdc1080
    humidityNow = hdc1080.humidity()
    #if True:
    try:
        if (humidityNow > humiditySetPoint + humidityThreshold ):
            print(f"Humidity too high: {humidityNow}")
            runFan()
            #print(f"Humidity: {hdc1080.humidity()}")
        elif (humidityNow < humiditySetPoint - humidityThreshold):
            print(f"Humidity in range: {humiditySetPoint - humidityThreshold} < {humidityNow} < {humiditySetPoint + humidityThreshold}")
            #stopFan()
        else:
            print(f"Humidity ok: {humidityNow}")
            #stopFan()
    except:
        print("Err read humidity")
        
    
            

print("Enable Timers ant Interrupts")


    
motionPIR.irq(trigger=Pin.IRQ_RISING, handler=onSensed) #Pin.IRQ_RISING|Pin.IRQ_FALLING

motionRADAR.irq(trigger=Pin.IRQ_RISING, handler=onSensed) #Pin.IRQ_RISING|Pin.IRQ_FALLING

timer_humidity.init(period=10000, mode=Timer.PERIODIC, callback=readHumidity)   # Timer.ONE_SHOT . Period in m



#time.sleep(2)


#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
#timer.init(period=1000, mode=Timer.ONE_SHOT, callback=analogReadings)   # Timer.ONE_SHOT . Period in m

machine_id = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")

from CONNECTWIFI import CONNECTWIFI
wifi = CONNECTWIFI()

from MACHINES import MACHINES
machines = MACHINES()

print(f"This machine: {machines.guid}, {machines.device}")
topic_receive = machines.topic_receive
topic_send = machines.topic_send



def discovery(sender):
    global topic_send,machines,lastMotion
    print(f"Discovery function called by {sender}")
    #temperature = read_temperature()
    try:
        humidity = hdc1080.humidity()
        temperature = hdc1080.temperature()
    except:
        humidity = 0
        temperature = 0
    #ambient = read_light()
    #dim = read_dim()
    #output = {"devicename":str(machines.device),"roomname":str(machines.name),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(ambient),"dim":str(dim),"lastmotion":lastMotion,"autobrightness":autoBrightness}
    output = {"devicename":str(machines.device),"roomname":str(machines.name),"temperature":str(temperature),"humidity":str(humidity),"ambient":str(0),"dim":str(dimSetPoint),"lastmotion":0,"autobrightness":0}
    #output = json.loads()
    #publish(topic_send, f"device:{machines.device}")
    #publish(topic_send, f"name:{machines.name}")
    #if (time.time() - lastMotion ) / 60 < 5:
    #publish(topic_send, f"lastmotion:{lastMotion}")
    #sendTemperature("Discovery")
    publish(topic_send, f"jsonDiscovery:{output}")
    print(f"jsonDiscovery:{output}")

def sub_cb(topic, msg):
    global light,last_run_time_send,dimSetPoint,humiditySetPoint #,topic
    
    
    print(f"Topic: {topic}; Mesaj: {msg}")
    
    
    
    if topic_receive == bytearray(topic,'UTF-8'):
        print("Matched topic")
        #print("Lights")
        if msg == b'true':
            dim.dimToOn()
            print("Lights ON")
        elif msg == b'false':
            dim.dimToOff()
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
                    intValue = int((int(strValue)*220)/100)
                    #dim.setReqIndex1(round(intValue*200/100))
                    dimSetPoint = intValue
                    print(f"Command: {command}, Value: {strValue}, index: {intValue}")                
                    updateConfig()
                if command == "humidity":
                    intValue = int(strValue)
                    humiditySetPoint = intValue
                    updateConfig()
                if command == "setAutoBrightness":
                    print("setAutoBrightness")
                    locals()[command](strValue)
                    discovery("setAutobrightness")
                    
      
      
    elif str(topic)[str(topic).find('/')+1:str(topic).find('/')+2] == '*' and str(topic)[2:str(topic).find('/')] == str(topic_receive)[0:str(topic_receive).find('/')]:
        print("broadcast")
        try:
            locals()[msg.decode()]("mqtt")
        except:
            print(f"Cannot decode function name: {msg}")
    else:
        print(f"Other {topic}: {str(topic)[str(topic).find('/')+1:str(topic).find('/')+2]}")
 
from mqtt import MQTTClient

def mqttClient(ssl_enabled = False,name="pico"):
    client = MQTTClient(client_id=b"" + name,
    server=secrets.MQTT_SERVER,
    port=8883,
    user=secrets.MQTT_USERNAME,
    password=secrets.MQTT_PASSWORD,
    keepalive=3600,
    ssl=ssl_enabled,
    ssl_params={'server_hostname':secrets.MQTT_SERVER}
    )
    return client

def publish(topic_send, value):
    global client
    #print(topic)
    #print(f"Sending to {topic_send} Message: {value}")
    client.publish(topic_send, value)
    #print("publish Done")


print("Init MQTT")
mqttInit = False
retryCount = 0
while mqttInit == False and retryCount < 5:
    #if True:
    try:
        client = mqttClient(True,machines.device)
        client.set_callback(sub_cb)
        client.connect()

        client.subscribe(topic = topic_receive)
        client.subscribe(topic = "to/#")
        print(f"Subscribed to: {topic_receive}")
        discovery("Init")
        timer_check_mqtt.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:client.check_msg())   # Timer.ONE_SHOT . Period in m
        mqttInit= True

    except:
        retryCount  += 1
        print("err mqtt")
    

#client.subscribe(topic = "picow/lights")

last_run_time_send = 0
last_run_time_receive = 0

while True:
        if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_send) >= 100000:
            last_run_time_send = tmp
            try:
                blink_period = 5000
                if wifi.is_connected():
                    blink_period = 1000
                timer_blink.init(period=blink_period, mode=Timer.PERIODIC, callback = blinkOnboardLed)

                print("MQTT ping")
                client.ping()
                
                
            except Exception as ex:
                print(f"Error sending to MQ: {ex}")
                client.connect()

while False: #never run
    if motionPIR.value() == 1:
        dim.setReqIndex1(dimSetPoint)
        timer.init(period=1*60*1000, mode=Timer.ONE_SHOT, callback=dimToOff)   # Timer.ONE_SHOT . Period in m
        
      