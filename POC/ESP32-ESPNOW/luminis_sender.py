import network
#import espnow
import asyncio
import aioespnow
import espnow
import ubinascii
import machine
import time
guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
role = "receiver" #"sender"
from i2c_init import *
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(False)
sta.active(True)
#sta.disconnect()      # For ESP8266
#sta.config(channel = config.read("channel"))

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')

e = espnow.ESPNow()

#e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
e.active(False)
e.active(True)
broadcast = b'\xff\xff\xff\xff\xff\xff'
e.add_peer(broadcast)


from machine import Pin

def command(pin):
    pin.irq(trigger=0)
    
    if pin == Pin(4):
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
    
t1=Pin(4,Pin.IN)
t2=Pin(3,Pin.IN)

t1.irq(command,Pin.IRQ_RISING)
t2.irq(command,Pin.IRQ_RISING)