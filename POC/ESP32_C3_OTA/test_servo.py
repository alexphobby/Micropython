from machine import Pin
from Servo import Servo
import time


servo = Servo(4)


from machine import Pin
import asyncio
from Encoder import Encoder

async def main():
    px = Pin(3, Pin.IN, Pin.PULL_UP)  # Change to match hardware
    py = Pin(2, Pin.IN, Pin.PULL_UP)
    enc = Encoder(px, py, div=1)  # div mtches mechanical detents
    async for value in enc:
        print(f"Value = {value}")
        servo.write(int(value))

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
    
    

while True:
    servo.write(0)
    time.sleep(5)
    servo.write(90)
   # time.sleep(1)
    #servo.write(90)
    time.sleep(5)