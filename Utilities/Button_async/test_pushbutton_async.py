from pushbutton import Pushbutton
from machine import Pin
import asyncio
led_value=True
led = Pin(8,Pin.OUT,value=led_value)
def launch(func, tup_args):
    res = func(*tup_args)
    if isinstance(res, type_coro):
        res = asyncio.create_task(res)
    return res

def toggle(led):
    global led_value
    led_value = not led_value
    led.value(led_value)
    
    print("sw")

async def my_app():
    pin = Pin(5, Pin.IN, Pin.PULL_DOWN)  # Pushbutton to gnd
    
    pb = Pushbutton(pin,suppress=True)
    
    pb.release_func(print, ("SHORT",))
    pb.double_func(print, ("DOUBLE",))
    pb.long_func(print, ("LONG",))
    
    #pb.press_func(toggle, (led,))  # Note how function and args are passed
    await asyncio.sleep(60)  # Dummy



asyncio.run(my_app())  # Run main application code