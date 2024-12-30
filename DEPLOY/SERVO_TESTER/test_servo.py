from machine import Pin
from Servo import Servo
import time


servo = Servo(4)


from machine import Pin
import asyncio
from Encoder import Encoder

async def main():
    print("Test servo")
    servo_range = 180
    px = Pin(3, Pin.IN, Pin.PULL_UP)  # Change to match hardware
    py = Pin(2, Pin.IN, Pin.PULL_UP)
    enc = Encoder(px, py, div=1)  # div mtches mechanical detents
    old_value = 0
    servo.write(int(servo_range - old_value))
    async for value in enc:
        print(f"Value = {value}")
        while value > old_value:
            old_value +=1
            servo.write(int(servo_range - old_value))
            await asyncio.sleep_ms(10)
        while value < old_value and value >= 0:
            old_value -=1
            servo.write(int(servo_range - old_value))
            await asyncio.sleep_ms(10)
        

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