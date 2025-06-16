import network
import espnow
import asyncio

import ubinascii
import machine
guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
role = "receiver"


sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
#sta.disconnect()      # For ESP8266

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')

e = espnow.ESPNow()
e.active(True)
peer = b'\xbb\xbb\xbb\xbb\xbb\xbb'   # MAC address of peer's wifi interface


async def send():
    await asyncio.sleep(5)
    try:
        e.add_peer(peer)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

    e.send(peer, "Starting...")

    while True:
        #await event_matter.wait()
        #event_matter.clear()
        e.send(peer, "ping", True)
        await asyncio.sleep(5)

def esp_receive(espnow):
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        print(host, msg)
#e.irq(esp_receive)
async def receive():
    
    while True:
        print("Try receive")
        host, msg = e.recv(0)
        if msg:             # msg == None if timeout in recv()
            print(f'Receive: {host, msg}')
        await asyncio.sleep(10)

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