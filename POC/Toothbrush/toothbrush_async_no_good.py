
from machine import Pin, PWM,freq,deepsleep
#freq(160_000_000)
from time import sleep,sleep_ms,sleep_us
import asyncio
from asyncio import Event
from machine import Signal
import esp32

sleep(3)
button_on = Event()
button_on.clear()
#frequency = 500
#led = PWM(Pin(20), frequency)
led = Signal(Pin(20,Pin.OUT,value = 1),invert=True)

pin1=Pin(20,Pin.OUT)
#pin1(0)

pin2=Pin(21,Pin.OUT)
#pin2(0)
pin5=Pin(5,Pin.IN,Pin.PULL_UP)


pin1.value(0)
pin2.value(0)
start = False

def interruption_handler(pin):
    global button_on
    global start
    pin5.irq(trigger=0)
    
    if button_on.is_set():
        print("Stop")
        button_on.clear()
        start= False
        led.off()
                
    else:
                
        button_on.set()
        print("Start")
        start=True
        led.on()
    #sleep(0.2)
    pin5.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)

pin5.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)

async def read_button():
    global button_on
    while True:
        if pin5.value()==1:
            #print("touch")
            await asyncio.sleep(0.2)
            if button_on.is_set():
                print("Stop")
                button_on.clear()
                #await asyncio.sleep(0.6)
                pin1.value(0)
                pin2.value(0)
                led.off()
                
            else:
                
                button_on.set()
                print("Start")
                led.on()
        await asyncio.sleep(0)
            #button_off_clear()

async def blink_led():
    while True:
        await asyncio.sleep(1)
        led.value(not led.value())


        
async def motor_on():
    global button_on
    while True:

#    if pin1.value() ==1 or pin2.value() ==1:
        pin1.value(0)
        pin2.value(0)
    #while pin5.value()==1:
        
        await button_on.wait()
        #print("bz")
        for i in range(0,50):
            pin2.off()
            sleep_us(400)
            pin1.on()
            sleep_us(2500)

            pin1.off()
            sleep_us(400)
            pin2.on()
                
            sleep_us(2500)
        await asyncio.sleep_ms(0)
        #pin2.off()
        #sleep(0.05)


async def main():
#    await wifi.check_and_connect()
    #blink = asyncio.create_task(blink_led())
    #read = asyncio.create_task(read_button())
    motor = asyncio.create_task(motor_on())
    while True:
        await asyncio.sleep(1)
        #if blink.done():
        #        print("blink is done")
        #        blink=None
        #        blink = asyncio.create_task(blink_led())
        #if read.done():
        #        print("read is done")
        #        read=None
        #        read = asyncio.create_task(read())
        #if motor.done():
        #        print("motor is done")
        #        motor=None
        #        motor = asyncio.create_task(motor())        
  
while True:
    if start:
        pin2.off()
        sleep_us(200)
        pin1.on()
        sleep_us(2200)

        pin1.off()
        sleep_us(200)
        pin2.on()
                
        sleep_us(2200)
    else:
        
        pin1.off()
        pin2.off()
        

try:
    print("Async call main")
    #asyncio.run(main())
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
except Exception as ex:
    print(f"Catch: {ex}")

finally:
    print(f"finally: ")
    #asyncio.new_event_loop()



