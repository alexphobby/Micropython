
from time import sleep,localtime
import asyncio
import esp32
led_pin = 7
presence_pin = 1


#presence = Pin(presence_pin,Pin.IN) #,value=Pin.PULL_DOWN)
#presence_2 = Pin(1, mode = Pin.IN, pull = Pin.PULL_DOWN)
presence = Pin(2, mode = Pin.IN) #4 ok
print(presence.value())
led = Pin(led_pin, Pin.OUT, value = 0)


from machine import deepsleep,lightsleep, wake_reason
#esp32.gpio_deep_sleep_hold(True)



#ESPNow



#print(f'Time: {localtime()[4]}:{localtime()[4]}')
#while True:
print(presence.value())
#    sleep(1)

#sleep(3)



if presence.value() == 1:
    print("present")
    #led.value(1)
    #sleep(0.1)
    #led.value(0)
    import network
    import espnow
    sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
    sta.active(True)
    e = espnow.ESPNow()
    e.active(True)
    broadcast = b'\xff\xff\xff\xff\xff\xff'
    e.add_peer(broadcast)

    e.send(broadcast,"ON")
    deepsleep(deepsleep_time)
else:
    print("absent")
    #e.send(broadcast,"OFF")
    led.value(0)
    #sleep(1)
    esp32.wake_on_ext0(pin = presence, level = esp32.WAKEUP_ANY_HIGH)
    deepsleep()




async def monitoring_presence():
    while True:
        if presence.value() == 1:
            led.value(1)
            deepsleep()
            #print(f'ON: {localtime()[4]}:{localtime()[5]}')
            #sleep(10)
        else:
            led.value(0)
            #print(f'OFF: {localtime()[4]}:{localtime()[5]}')
        
        #s
        await asyncio.sleep(1)

async def main():
    asyncio.create_task(monitoring_presence())
    while True:
        await asyncio.sleep(1)

try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()
