import network
#import espnow
import asyncio
import aioespnow

import ubinascii
import machine
import time
guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
role = "receiver" #"sender"
from i2c_init import *
from CONFIG import CONFIG
config=CONFIG(debug=True)
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
#sta.disconnect()      # For ESP8266
sta.config(channel = config.read("channel"))

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')

e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
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
    async for mac, msg in e:
        print(f'Echo: {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")}')
        debug_oled(f'{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]} - {str(msg,"UTF-8")}')
    
    while True:
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
    asyncio.create_task(worker())
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