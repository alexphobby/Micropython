from machine import Pin,PWM
from time import sleep
import asyncio
class BUZZER:
    def __init__(self,pin,freq=800,max_duty=5):
        self.buzzer = PWM(pin, freq=freq, duty_u16=0)
        self.max_duty = max_duty
    def buzz(self,times = 1):
        if times == 1:
            self.buzzer.duty(self.max_duty)
            sleep(0.2)
            self.buzzer.duty(0)
            return
        
        for i in range(times):
            self.buzzer.duty(self.max_duty)
            sleep(0.2)
            self.buzzer.duty(0)
            sleep(0.2)

    async def buzz_as(self,times = 1):
        if times == 1:
            self.buzzer.duty(self.max_duty)
            await asyncio.sleep(0.16)
            self.buzzer.duty(0)
            return

        for i in range(times):
            self.buzzer.duty(self.max_duty)
            await asyncio.sleep(0.16)
            self.buzzer.duty(0)
            await asyncio.sleep(0.16)
