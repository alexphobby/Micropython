from machine import Pin
from Servo import Servo
import time


servo = Servo(5)
while True:
    servo.write(30)
    time.sleep(1)
    servo.write(60)
    time.sleep(1)
    servo.write(90)
    time.sleep(5)
mid
 vcx\zVC