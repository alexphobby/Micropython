from machine import Pin,Signal,unique_id,lightsleep,freq
#freq(80000000)
touch_1_pin = 1
touch_2_pin = 2
led_pin = 13
led_pin_invert = True
pir_pin = 3
radar_pin = 4
pir = Pin(pir_pin,Pin.IN,Pin.PULL_DOWN)
radar = Pin(radar_pin,Pin.IN,Pin.PULL_DOWN)
auto = True
light_on=False

import network
import asyncio
import aioespnow

import ubinascii
import time
from time_util import *
import json
from machine import ADC

guid = str(ubinascii.hexlify(unique_id()),"UTF-8")

if guid == 'c04e30814b98':
    led_pin = 0
led_pin = Pin(led_pin,Pin.OUT,value=1)
led = Signal(led_pin,invert=led_pin_invert)


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
event_auto.clear()


#event_off = asyncio.Event()
#event_off.clear()

pot_pin=6
delay = 30
pot_adc=ADC(pot_pin,atten=ADC.ATTN_11DB)
last_motion = 0

def command(pin):
    global auto,light_on,last_motion
    pin.irq(trigger=0)
    if pin == touch_1: #ON/OFF
        if event_auto.is_set():
            event_auto.clear()
        try:
            if led.value() == False:
                #led.value(1)
                led.on()
                e.send(broadcast,json.dumps({"light":1,"addr":1,"auto":int(event_auto.is_set())}))
            else:
                led.off()
                e.send(broadcast,json.dumps({"light":0,"addr":1,"auto":int(event_auto.is_set())}))
        except:
            print('err')
        print(f"Manual {'ON' if led.value() else 'OFF'}")
    
    if pin == touch_2: #AUTO
        if event_auto.is_set(): #AUTO -> MANUAL
            event_auto.clear()
        else: #MANUAL -> AUTO
            event_auto.set()
            last_motion = get_seconds()
            try:
                led.on()
                e.send(broadcast,json.dumps({"light":1,"addr":1,"auto":int(event_auto.is_set())}))
            except:
                print('err')
        
        print(f"Auto {'ON' if event_auto.is_set() else 'OFF'}")
        
    
    pin.irq(command,trigger=Pin.IRQ_RISING)
    
touch_1=Pin(touch_1_pin,Pin.IN,Pin.PULL_DOWN)
touch_2=Pin(touch_2_pin,Pin.IN,Pin.PULL_DOWN)

touch_1.irq(command,Pin.IRQ_RISING)
touch_2.irq(command,Pin.IRQ_RISING)

def motion_irq(pin):
    global last_motion
    if not auto: #AUTO DISABLED
        return
    
    pin.irq(trigger=0)
    print(f"motion on {pin}")
    last_motion = get_seconds()
    if pin == pir and not event_pir.is_set():
        print("motion event set")
        event_pir.set()
        led.on()
        try:
            print("sending")
            e.send(broadcast,json.dumps({"light":1,"addr":1,"auto":int(event_auto.is_set())}))
            #time.sleep(0.5)
        except:
            print('err')
    
    if pin == radar and not event_radar.is_set():
        print("motion event set")
        event_radar.set()
        led.on()
        try:
            print("sending")
            e.send(broadcast,json.dumps({"light":1,"addr":1,"auto":int(event_auto.is_set())}))
            #time.sleep(0.5)
        except:
            print('err')
    
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
    global e
    global delay
    print("Init receive")
    async for mac, msg in e:
        print(f'Echo: {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")} - {msg}')
        #debug_oled(f'{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")}')
        try:
            if msg in ["1","0",1,0]:
                print(f"match: {msg}")
                led.value(int(msg))
            else:
                msg_parsed = json.loads(msg)
                if 'delay' in msg_parsed.keys():
                    print(f'Delay is: {msg_parsed['delay']}')
                    delay = msg_parsed['delay']
                if 'light' in msg_parsed.keys():
                    led.value(msg_parsed['light'])
                    last_motion = set_seconds()
                    print("light on - espnow")
                if 'auto' in msg_parsed.keys():
                    if msg_parsed['auto']:
                        event_auto.set()
                    else:
                        event_auto.clear()
                
        except Exception as ex:
            print(f'err: {ex}')
        
def set_delay():
    global delay
    if pot_adc.read_u16() > 100 and pot_adc.read_u16() < 60000:
        delay = int(pot_adc.read_u16()/100)+20
        print(f'Set delay: {delay}')
    else:
        print(f'Err delay read: {pot_adc.read_u16()}')
        
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
        await asyncio.sleep(10)
        if not event_auto.is_set():
            print("not auto, skipping")
            continue
        
        if pir.value() == 1 or radar.value() == 1:
            last_motion = get_seconds()
            print(f"pir:{pir.value()} radar:{radar.value()}")
            try:
                e.send(broadcast,json.dumps({"light":1,"addr":1}))
            except:
                print('err')
            led.on()
            await asyncio.sleep(delay)
            #lightsleep(delay*1000)
        elif get_seconds() - last_motion > delay and led.value():
            print(f"off : {get_seconds()} - {last_motion} > {delay}")
        
            try:
                e.send(broadcast,json.dumps({"light":0,"addr":1}))
            except:
                print('err')
            led.off()
        else:
            print("skipping")
        
        #led.value(1)
        #pir.irq(motion_irq,Pin.IRQ_RISING)
        #try:
        #    e.send(broadcast,b'1')
        #except:
        #    print('err')
        
        
            
async def main():
    #t_connect = asyncio.create_task(wifi.check_and_connect())
    t_send = None #asyncio.create_task(process_ir_queue(ir_queue))
    asyncio.create_task(worker())
    asyncio.create_task(off_worker())
    asyncio.create_task(receive())
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
    asyncio.new_event_loop()
    
    
