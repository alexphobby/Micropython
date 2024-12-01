
from machine import Pin, PWM,freq,deepsleep
#freq(160_000_000)
from time import sleep,sleep_ms,sleep_us
#import asyncio
from asyncio import Event
from machine import Signal
import esp32
from machine import Timer
timer = Timer(0)
timer_stop = Timer(1)

button_on = Event()
button_on.clear()
#frequency = 500
#led = PWM(Pin(20), frequency)
led = Signal(Pin(8,Pin.OUT,value = 1),invert=True)

pin1=Pin(20,Pin.OUT)
pin2=Pin(21,Pin.OUT)
pin5=Pin(0,Pin.IN,Pin.PULL_UP)


pin1.value(0)
pin2.value(0)
cycle=3
sleep(1)

start = False

def blink(timer):
    global cycle
    global pin1
    global pin2
    global led
    led.on()
    print("timer")
    pin1.off()
    pin2.off()
    
    sleep_ms(100)
    pwm = PWM(pin1,freq=1000,duty_u16=0)
    
    for i in range(0,cycle):
        #pin1.on()
        pwm.duty_u16(65000)
        sleep_ms(150)
        pwm.duty_u16(0)
        sleep_ms(150)
        
        #pin1.off()
        
        #pin2.on()
        #sleep_ms(10)
        #pin2.off()
    #sleep_ms(300)
    cycle += 1
    pwm.deinit()
    pin1=Pin(20,Pin.OUT)
    pin1.off()
    led.on()

def stop(mytimer):
    global start
    global timer
    led.off()
    start=False
    timer.deinit()
    mytimer.deinit()



def interruption_handler(pin):
    global button_on
    global timer
    global timer_stop
    global start
    global cycle
    pin5.irq(trigger=0)
    cycle = 1
    
    if button_on.is_set():
        print("Stop")
        button_on.clear()
        start= False
        led.off()
        timer.deinit()
        timer_stop.deinit()
        sleep(1)
                
    else:
        button_on.set()
        print("Start")
        start=True
        timer.init(period=30000, mode=Timer.PERIODIC, callback=blink)   #
        timer_stop.init(period=5*30*1000, mode=Timer.ONE_SHOT, callback=stop)   #
        led.on()
        sleep(1)
    
    pin5.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)

pin5.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)

async def read_button():
    global button_on
    global cycle
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




#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)

off=200
on=2200

#f=1/(on+off)
#fill = on/off
f=250.0
fill=0.5
#fill=0.1

off=int(1000000/(f*(1+fill)))
on=int(fill*off)
print(f'on: {on}; off: {off}')

while True:
    if start:
        pin2.off()
        sleep_us(off)
        pin1.on()
        sleep_us(on)

        pin1.off()
        sleep_us(off)
        pin2.on()
                
        sleep_us(on)
    else:
        pin1.off()
        pin2.off()
        sleep(0.5)
        

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



