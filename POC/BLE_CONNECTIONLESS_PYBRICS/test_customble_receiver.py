import bluetooth
from struct import pack_into, unpack

from Queue import Queue
import asyncio


bt_queue=Queue()
#ble.gap_advertise(1000000, send_buffer)
_IRQ_SCAN_RESULT = const(5)
def observe_irq(event, data):
    global bt_queue
    if event != _IRQ_SCAN_RESULT :
        return
    addr_type, addr, adv_type, rssi, adv_data = data
    #print(f'evt: {event} - data: addr_type:{addr_type}, addr: {bytes(addr)}, adv_type: {adv_type}, rssi: {rssi}, adv_data: {bytes(adv_data)}')
    try:
        bt_queue.put_nowait(bytes(adv_data))
    except Exception as ex:
        print(f'{bytes(adv_data)} - {ex}')
    #print(data)
ble = bluetooth.BLE()
ble.active(True)
ble.irq(observe_irq)
ble.gap_scan(0)
async def process_bt_queue(queue):
    while True:
        message = await queue.get()
        print(message)
        await asyncio.sleep(0)
        
async def main():
    t_process_bt_queue = None
    while True:
        await asyncio.sleep(1)
        #gc.collect()
        if t_process_bt_queue is None or t_process_bt_queue.done():
        #    t_ble_send = None
        #    print("restart task t_ble_send")
            t_process_bt_queue = asyncio.create_task(process_bt_queue(bt_queue))
        

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

