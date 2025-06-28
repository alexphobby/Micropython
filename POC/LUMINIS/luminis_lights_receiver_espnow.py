from machine import Pin,Signal,unique_id,lightsleep,freq
from os import uname
#freq(80000000)
startup = True

if "C3" in uname().machine:
    print("C3")
    led_1_pin_nr = 5
    led_2_pin_nr = 6
    pot_pin=4
    pir_pin_nr = 20
    radar_pin_nr = 21
    addr1_pin_nr = 3
    addr2_pin_nr = 4
else:
    print("S3")
    led_1_pin_nr = 13
    led_2_pin_nr = 12
    pot_pin=14
    pir_pin_nr = 6
    radar_pin_nr = 5
    addr1_pin_nr = 7
    addr2_pin_nr = 8

touch_1_pin = 1
touch_2_pin = 2
touch_3_pin = 3

led_1_pin_invert = True
led_2_pin_invert = True


pir = Pin(pir_pin_nr,Pin.IN,Pin.PULL_DOWN)
radar = Pin(radar_pin_nr,Pin.IN,Pin.PULL_DOWN)
auto = True
light_on=False


addr1_pin = Pin(addr1_pin_nr,Pin.IN,Pin.PULL_UP)
addr2_pin = Pin(addr2_pin_nr,Pin.IN,Pin.PULL_UP)
addr = 3 - addr1_pin.value() - addr2_pin.value()
print(f'Addr: {addr}')

import network
import asyncio
import aioespnow

import ubinascii
import time
from time_util import *
import json
from machine import ADC

guid = str(ubinascii.hexlify(unique_id()),"UTF-8")
receiver_role = 1

if guid == 'c04e30814b98':
    led_1_pin = 0
elif guid == '50787d18e0ac':
    receiver_role = 0
led_1_pin = Pin(led_1_pin_nr,Pin.OUT,value=1)
led_1 = Signal(led_1_pin,invert=led_2_pin_invert)
led_2_pin = Pin(led_2_pin_nr,Pin.OUT,value=1)
led_2 = Signal(led_2_pin,invert=led_2_pin_invert)


#from i2c_init import *
#from CONFIG import CONFIG
#config=CONFIG(debug=True)
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(False)
sta.active(True)
print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')
e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
e.active(False)
e.active(True)
peer_receiver = b'\xc0N0\x81K\x98'   # MAC address of peer's wifi interface
peer_sender = b'\xc0N0\x81A`' #sender mac   # MAC address of peer's wifi interface
broadcast = b'\xff\xff\xff\xff\xff\xff'
e.add_peer(broadcast)

#sta.disconnect()      # For ESP8266
#sta.config(channel = config.read("channel"))
#sta.config(channel = 5)
event_pir = asyncio.Event()
event_pir.clear()
event_radar = asyncio.Event()
event_radar.clear()
event_remote = asyncio.Event()
event_remote.clear()


event_auto = asyncio.Event()
event_auto.set()


#event_off = asyncio.Event()
#event_off.clear()


delay = 30
pot_adc=ADC(pot_pin,atten=ADC.ATTN_11DB)
last_motion = 0

def command(pin):
    global auto,light_on,last_motion,addr
    pin.irq(trigger=0)
    print(f'Touched: {pin}')
    if pin == touch_1: #ON/OFF
        if event_auto.is_set():
            event_auto.clear()
        try:
            if led_1.value() == False:
                #led.value(1)
                led_1.on()
                for i in range(3):
                    e.send(broadcast,json.dumps({"light_1":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
                    
            else:
                led_1.off()
                for i in range(3):
                    e.send(broadcast,json.dumps({"light_1":0,"addr":addr,"auto":int(event_auto.is_set())}),False)
                
        except:
            print('err')
        print(f"Manual {'ON' if led_1.value() else 'OFF'} 1")

    if pin == touch_2: #ON/OFF
        if event_auto.is_set():
            event_auto.clear()
        try:
            if led_2.value() == False:
                #led.value(1)
                led_2.on()
                e.send(broadcast,json.dumps({"light_2":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
            else:
                led_2.off()
                e.send(broadcast,json.dumps({"light_2":0,"addr":addr,"auto":int(event_auto.is_set())}),False)
        except:
            print('err')
        print(f"Manual {'ON' if led_2.value() else 'OFF'} 2")

    if pin == touch_3: #AUTO
        if event_auto.is_set(): #AUTO -> MANUAL
            event_auto.clear()
        else: #MANUAL -> AUTO
            event_auto.set()
            last_motion = get_seconds()
            try:
                led_1.on()
                led_2.on()
                e.send(broadcast,json.dumps({"light":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
            except:
                print('err')
        
        print(f"Auto {'ON' if event_auto.is_set() else 'OFF'}")
        
    
    pin.irq(command,trigger=Pin.IRQ_RISING)
    
touch_1=Pin(touch_1_pin,Pin.IN,Pin.PULL_DOWN)
touch_2=Pin(touch_2_pin,Pin.IN,Pin.PULL_DOWN)
touch_3=Pin(touch_3_pin,Pin.IN,Pin.PULL_DOWN)
time.sleep(0.5)

touch_1.irq(command,Pin.IRQ_RISING)
touch_2.irq(command,Pin.IRQ_RISING)
touch_3.irq(command,Pin.IRQ_RISING)

def motion_irq(pin):
    global last_motion
    if not event_auto.is_set(): #AUTO DISABLED
        return
    
    pin.irq(trigger=0)
    print(f"motion on {pin}, event_pir.is_set(): {event_pir.is_set()} event_radar.is_set(): {event_radar.is_set()}")
    last_motion = get_seconds()
    if pin == pir:
        if not event_pir.is_set():
            print("motion event set")
            event_pir.set()
            led_1.on()
            led_2.on()
            try:
                print("sending")
                for i in range(3):
                    e.send(broadcast,json.dumps({"light":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
                #time.sleep(0.5)
            except:
                print('err')
        #else:
        #event_pir.clear()
        #print("Celar event_pir")
    
    if pin == radar and not event_radar.is_set():
        print("radar motion event set")
        event_radar.set()
        led_1.on()
        led_2.on()
        try:
            print("sending")
            for i in range(3):
                e.send(broadcast,json.dumps({"light":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
            #time.sleep(0.5)
        except:
            print('err')
    #else:
    #    event_radar.clear()
    #    print("Clear event_radar")
    #time.sleep(1)
    pin.irq(motion_irq,Pin.IRQ_RISING)

pir.irq(motion_irq,Pin.IRQ_RISING)    
radar.irq(motion_irq,Pin.IRQ_RISING)



#e = espnow.ESPNow()
#e.active(True)

debug=True

def debug_oled(message):
    global debug
    if debug:
        print("oled msg")
        oled_write.set_textpos(oled,56,0)
        oled_write.printstring(f'{message}')
        oled.show()
        
async def send():
    await asyncio.sleep(1)
    try:
        e.add_peer(peer_receiver)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

    #e.send(peer_receiver, "Starting...")
    

    while True:
        #await event_matter.wait()
        #event_matter.clear()
        print("Send ping")
        #e.send(peer_receiver, "ping") #, True)
        await e.asend(peer_receiver, b'ping')
        await asyncio.sleep(5)

async def receive():
    global e,last_motion,delay

    print("Init receive")
    async for mac, msg in e:
        #print(f'Echo: {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")} - {msg}')
        #debug_oled(f'{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")}')
        try:
            #if msg in ["1","0",1,0]:
            #    print(f"match: {msg}")
            #    led.value(int(msg))
            #else:
            msg_parsed = json.loads(msg)
            print(f'Received: {msg_parsed}')
            if 'addr' in msg_parsed.keys():
                if msg_parsed['addr'] != addr:
                    print("wrong address")
                    continue
            if 'delay' in msg_parsed.keys():
                print(f'Delay is: {msg_parsed['delay']}')
                delay = msg_parsed['delay']
            if 'light' in msg_parsed.keys():
                led_1.value(msg_parsed['light'])
                led_2.value(msg_parsed['light'])
                if msg_parsed['light']:
                    last_motion = get_seconds()
                    event_remote.set()
                    print(f'ESPNOW Set lastmotion: {last_motion}')
                print(f"Light {'ON' if msg_parsed['light'] else 'OFF'} - espnow")
            
            if 'light_1' in msg_parsed.keys():
                led_1.value(msg_parsed['light_1'])
                if msg_parsed['light_1']:
                    last_motion = get_seconds()
                    event_remote.set()
                    print(f'ESPNOW Set lastmotion: {last_motion}')
                print(f"Light_1 {'ON' if msg_parsed['light_1'] else 'OFF'} - espnow")

            if 'light_2' in msg_parsed.keys():
                led_2.value(msg_parsed['light_2'])
                if msg_parsed['light_2']:
                    last_motion = get_seconds()
                    event_remote.set()
                    print(f'ESPNOW Set lastmotion: {last_motion}')
                print(f"Light_2 {'ON' if msg_parsed['light_2'] else 'OFF'} - espnow")
            
            if 'auto' in msg_parsed.keys():
                if msg_parsed['auto']:
                    event_auto.set()
                else:
                    event_auto.clear()
                
        except Exception as ex:
            print(f'err: {ex}')
        
def set_delay():
    global delay
    #if pot_adc.read_u16() > 10 and pot_adc.read_u16() < 64000:
    delay = int(pot_adc.read_u16()/100)+10
    print(f'Set delay: {delay}, pot: {pot_adc.read_u16()}')
    #else:
    #    print(f'Err delay read: {pot_adc.read_u16()}')
        
set_delay()

async def worker():
    await asyncio.sleep(5)
    while True:
        print("worker")
        
        set_delay()
        
        await asyncio.sleep(5000)



async def read_adc():
    global delay
    while True:
        await event_pir.wait()
        await asyncio.sleep(2)
        delay = int(pot_adc.read_u16()/100)
        print(f'Read ADC: {delay} s')
        await e.asend(broadcast, json.dumps({"delay":delay}))
        
async def off_worker():
    global pir,last_motion
    global delay
    await asyncio.sleep(5)
    while True:
        #print("pir_worker")
        #if event_pir.is_set():
        #await event_pir.wait()
        #event_pir.clear()
        #print("Event captured")
        await asyncio.sleep(5)
        if not event_auto.is_set():
            print("not auto, skipping")
            continue
        
        if pir.value() == 1 or radar.value() == 1:
                
            last_motion = get_seconds()
            print(f"pir:{pir.value()} radar:{radar.value()}")
            try:
                for i in range(3):
                    e.send(broadcast,json.dumps({"light":1,"addr":addr}),False)
            except:
                print('err')
            led_1.on()
            led_2.on()
            await asyncio.sleep(delay)
            #lightsleep(delay*1000)
        elif get_seconds() - last_motion > delay and (led_1.value() or led_2.value()):
            print(f"off : {get_seconds()} - {last_motion} > {delay}")
        
            try:
                event_pir.clear()
                event_radar.clear()
                event_remote.clear()
                for i in range(3):
                    e.send(broadcast,json.dumps({"light":0,"addr":addr}),False)
            except:
                print('err')
            led_1.off()
            led_2.off()
        else:
            
            print("skipping")

def sense():
    print(f'Sense: pir: {pir.value()} radar: {radar.value()}')
    if pir.value():
        event_pir.set()
    if radar.value():
        event_radar.set()
    
    if event_radar.is_set() or event_pir.is_set():
        led_1.on()
        led_2.on()
        try:
            print("sending")
            for i in range(3):
                e.send(broadcast,json.dumps({"light":1,"addr":addr,"auto":int(event_auto.is_set())}),False)
                #time.sleep(0.5)
        except:
            print('err')

        
    
            
async def main():
    global startup
    #t_connect = asyncio.create_task(wifi.check_and_connect())
    t_send = None #asyncio.create_task(process_ir_queue(ir_queue))
    asyncio.create_task(worker())
    asyncio.create_task(off_worker())
    if receiver_role:
        print("Receiver role")
        asyncio.create_task(receive())
    
    if startup:
        print("Startup")
        sense()
        #command(pir)
        #command(radar)
        startup = False
#    asyncio.create_task(read_adc())
#    if role == "sender":
#        print("Sender Role")
#        asyncio.create_task(send())
#    else:
#        print("Receiver Role")
#        asyncio.create_task(receive())
  
    while True:
        await asyncio.sleep(1)
        #gc.collect()
        #if t_send is None or t_send.done():
        #    t_send = None
        #    print("restart task t_process_ir_queue")
        #    t_send = asyncio.create_task(send())
      
        await asyncio.sleep(30)

try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    print("Finally")
    touch_1.irq(trigger=0)
    touch_2.irq(trigger=0)
    touch_3.irq(trigger=0)
    asyncio.new_event_loop()
    
    
