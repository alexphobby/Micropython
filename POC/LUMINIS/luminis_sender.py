from machine import Pin,unique_id
led_pin = 4
pir_pin = 3
radar_pin = 5
led = Pin(led_pin,Pin.OUT,value=0)
pir = Pin(pir_pin,Pin.IN)
radar = Pin(radar_pin,Pin.IN,Pin.PULL_UP)

import network
import asyncio
import aioespnow

import ubinascii
import time

guid = str(ubinascii.hexlify(unique_id()),"UTF-8")
role = "receiver" #"sender"
#from i2c_init import *
#from CONFIG import CONFIG
#config=CONFIG(debug=True)
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(False)
sta.active(True)
#sta.disconnect()      # For ESP8266
#sta.config(channel = config.read("channel"))
event_pir = asyncio.Event()
event_pir.clear()

def command(pin):
    pin.irq(trigger=0)
    
    if pin == Pin(1):
        print("ON")
        try:
            e.send(broadcast,b'1')
        except:
            print('err')
    else:
        print("OFF")
        try:
            e.send(broadcast,b'0')
        except:
            print('err')
    #print(f'Touched: {pin}')
    
    #while pin.value() == 1:
    #    print(f'Still Touched: {pin}')
    #    time.sleep(0.5)
    
    pin.irq(command,trigger=Pin.IRQ_RISING)
    
t1=Pin(1,Pin.IN,Pin.PULL_DOWN)
t2=Pin(2,Pin.IN,Pin.PULL_DOWN)

t1.irq(command,Pin.IRQ_RISING)
t2.irq(command,Pin.IRQ_RISING)

def motion_irq(pin):
    pin.irq(trigger=0)
    #print("motion")
    if not event_pir.is_set():
        #print("motion event set")
        event_pir.set()
        led.value(1)
    pin.irq(motion_irq,Pin.IRQ_RISING)
    
pir.irq(motion_irq,Pin.IRQ_RISING)
radar.irq(motion_irq,Pin.IRQ_RISING)

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')

e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support

e.active(False)
e.active(True)

#e = espnow.ESPNow()
#e.active(True)
peer_receiver = b'\xc0N0\x81K\x98'   # MAC address of peer's wifi interface
peer_sender = b'\xc0N0\x81A`' #sender mac   # MAC address of peer's wifi interface
broadcast = b'\xff\xff\xff\xff\xff\xff'
e.add_peer(broadcast)

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
    print("Init receive")
    async for mac, msg in e:
        print(f'Echo: {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")} - {msg}')
        debug_oled(f'{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")}')
        try:
            if int(msg) in [1,0]:
                print(f"match: {msg}")
                led.value(int(msg))
                
        except Exception as ex:
            print(ex)
    

async def worker():
    await asyncio.sleep(5)
    while True:
        print("worker")
        await asyncio.sleep(5)


async def pir_worker():
    global pir
    await asyncio.sleep(5)
    while True:
        print("pir_worker")
        await event_pir.wait()
        event_pir.clear()
        print("Event captured")
        #led.value(1)
        #pir.irq(motion_irq,Pin.IRQ_RISING)
        await asyncio.sleep(20)
        #time.sleep(10)
        led.value(0)
        
async def main():
    #t_connect = asyncio.create_task(wifi.check_and_connect())
    t_send = None #asyncio.create_task(process_ir_queue(ir_queue))
    asyncio.create_task(worker())
    asyncio.create_task(pir_worker())
    if role == "sender":
        print("Sender Role")
        asyncio.create_task(send())
    else:
        print("Receiver Role")
        asyncio.create_task(receive())
  
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
