

#test()

print(weather.temperature())

from machine import Pin
from ir_remote_read import ir_remote_read
from my_remotes import *

ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)
#from ir_remote_read_demo import *


#from aremote import NEC_IR, REPEAT
#from machine import Signal

#def cb(data, addr, led):
#    print(f"Addr: {addr} - Data: {data}")

#ir = NEC_IR(ir_pin, cb, True, Pin(8,Pin.OUT))

def ir_callback(remote,command,combo):
    print((remote,command))
    try:
        print(remote_samsung[combo])
        return
    except:
        pass
    
    try:
        print(remote_tiny[combo])
    except:
        pass
    #print((remote,command))
    
    
ir = ir_remote_read(ir_pin,ir_callback)


#ir_remote_read(ir_pin,ir_callback)
from machine import RTC
rtc = RTC()

##init HDC temperature sensor, already we have i2c
from hdc1080_util import hdc1080_util
hdc1080 = hdc1080_util(i2c)


from ssd1306 import SSD1306_I2C
import writer
import freesans20
#Init Oled display i2c scan= [60]
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)
write_custom_font = writer.Writer(oled, freesans20)
write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring(f"Loading...")
oled.show()



async def heartbeat_oled():
    global set_temp,ir,weather
    print("heartbeat_oled")
    print(ir)
    s = True
    last_minute = -1 #rtc.datetime()[5]
    await client.connect()
    while True:
        
        if last_minute == rtc.datetime()[5]:
            write_custom_font.set_textpos(oled,0,0)
            #write_custom_font.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}     ')
            oled.show()
            await asyncio.sleep_ms(1000)
            #last_minute = rtc.datetime()[6]
        else:
            print(f"update temp: {last_minute} != {rtc.datetime()[5]}")
            oled.fill(0)
            write_custom_font.set_textpos(oled,0,0)
            #write_custom_font.printstring(f'{rtc.datetime()[2]:02d}/{rtc.datetime()[1]:02d}/{rtc.datetime()[0]} - {rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.printstring(f'{rtc.datetime()[4]:02d}:{rtc.datetime()[5]:02d}:{rtc.datetime()[6]:02d}')
            write_custom_font.set_textpos(oled,20,0)
            write_custom_font.printstring(f'{hdc1080.temperature()} C')
            
            write_custom_font.set_textpos(oled,20,60)
            write_custom_font.printstring(f' {hdc1080.humidity()} %   ')
            
            if weather.temperature() > -100:
                write_custom_font.set_textpos(oled,40,0)
                write_custom_font.printstring(f'Out: {weather.temperature()} C  ')
                #oled.drawCircle(50, 50, 10, WHITE)
            oled.show()
            last_minute = rtc.datetime()[5]
            await asyncio.sleep_ms(1000)
            
    
        
        

#asyncio.create_task(heartbeat_oled())
asyncio.run(heartbeat_oled())
