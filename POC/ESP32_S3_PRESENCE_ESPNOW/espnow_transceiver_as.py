import network

#import espnow
import asyncio
import aioespnow
from machine import Pin,unique_id,lightsleep
from time import sleep
import ubinascii
guid = str(ubinascii.hexlify(unique_id()),"UTF-8")
role="receiver"
import time

e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
e.active(True)
peer_receiver = b'4\xb7\xdaR\xf8\x00'   # MAC address of peer's wifi interface
peer_sender = b'\xc0N0\x81A`' #sender mac   # MAC address of peer's wifi interface
broadcast = b'\xff\xff\xff\xff\xff\xff'
e.add_peer(broadcast)

led = Pin(2,Pin.OUT)
led.off()

def click(pin):
    pin.irq(trigger=0)
    sta.active(True)
    try:
        led.on()
        e.send(broadcast, f'1',False)
        print("sent")
    except Exception as ex:
        print(ex)
    #lightsleep(1)
    sleep(1)
    
    pin.irq(trigger=Pin.IRQ_FALLING,handler=click)
    
    sta.active(False)
    while sta.active():
        sleep(0.1)
    led.off()
    #lightsleep(1)
    
    

if guid == '24ec4a305118':
    role = "sender"
    try:
        e.add_peer(peer_receiver)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

    switch = Pin(1,Pin.IN, Pin.PULL_UP)
    switch.irq(trigger=Pin.IRQ_FALLING,handler=click)
    
    try:
        e.add_peer(peer_receiver)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

else:
    led = Pin(2,Pin.OUT)
    led.off()

try:
    sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
    sta.active(True)
except Exception as ex:
    print(f'Enabling sta err: {ex}')
#sta.disconnect()      # For ESP8266

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')


async def send():
    i=1
    await asyncio.sleep(1)
    try:
        e.add_peer(peer_receiver)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

    #e.send(peer_receiver, "Starting...")
    

    while True:
        #await event_matter.wait()
        #event_matter.clear()
        print(f"Send ping {i}")
        #e.send(peer_receiver, "ping") #, True)
        await e.asend(peer_receiver, f'ping {i}')
        i += 1
        await asyncio.sleep(5)

async def receive():
    global e
    async for mac, msg in e:
        print(f'Echo: {msg} - {str(msg,"UTF-8")}')
        if str(msg,"UTF-8") == "1":
            led.on()
            sleep(1)
            led.off()
            print("on")
        else:
            led.off()
            print("off")

    while False:
        print("Try receive")
        host, msg = e.recv()
        if msg:             # msg == None if timeout in recv()
            print(host, msg)
        await asyncio.sleep(0.5)

async def worker():
    await asyncio.sleep(5)
    while True:
        print("worker")
        await asyncio.sleep(5)

async def main():
    #t_connect = asyncio.create_task(wifi.check_and_connect())
    t_send = None #asyncio.create_task(process_ir_queue(ir_queue))
    #asyncio.create_task(worker())
    if role == "sender":
        print("Sender Role")
        #asyncio.create_task(send())

        
    else:
        print("Receiver Role")
        asyncio.create_task(receive())
    sleep(1)
    while True:
        await asyncio.sleep(0.5)
        #sta.active(False)
        #while sta.active():
        #    sleep(0.1)
        #lightsleep(1)
        #gc.collect()
        #if t_send is None or t_send.done():
        #    t_send = None
        #    print("restart task t_process_ir_queue")
        #    t_send = asyncio.create_task(send())
      


try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()