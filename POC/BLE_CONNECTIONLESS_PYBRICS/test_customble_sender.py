import bluetooth
from struct import pack_into, unpack

from Queue import Queue
import asyncio

ble = bluetooth.BLE()
ble_send_queue = Queue()
message="{'test': 1}"
async def ble_send(queue):
    ble.active(True)
        
    
    while True:
        asyncio.sleep(1)
        #message = await queue.get()
        print("sending")
        ble.gap_advertise(6250000, message)
        ble.gap_advertise(None)
        print("sent")
        await asyncio.sleep(0.5)
        #ble.active(False)
        await asyncio.sleep(1)
        
async def main():
    t_ble_send = None
    while True:
        await asyncio.sleep(1)
        #gc.collect()
        if t_ble_send is None or t_ble_send.done():
            t_ble_send = None
            print("restart task t_ble_send")
            t_ble_send = asyncio.create_task(ble_send(ble_send_queue))
        

        await asyncio.sleep(30)

try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
#except Exception as ex:
#    my_print(f"Catch: {ex}")


