from BUZZER import BUZZER
import asyncio
pin=17
buzzer = BUZZER(pin,max_duty=2)

asyncio.run(buzzer.buzz_as())
#await buzzer.buzz_as()
#buzzer.buzz(5)