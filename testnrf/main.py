#import machine
import time
from machine import Timer
from machine import Pin
from machine import I2C
from ssd1306 import SSD1306_I2C

import writer
import freesans20

#time.sleep(1)           # sleep for 1 second
#time.sleep_ms(500)      # sleep for 500 milliseconds
#time.sleep_us(10)       # sleep for 10 microseconds
#start = time.ticks_ms() # get millisecond counter
#delta = time.ticks_diff(time.ticks_ms(), start) # compute time difference

led = Pin(25, Pin.OUT)

def blink(timer):
    led.toggle()

timer = Timer()
#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)
timer.init(period=3000, mode=Timer.PERIODIC, callback=blink)
from machine import Pin, I2C

#i2c = I2C(0)   # default assignment: scl=Pin(9), sda=Pin(8)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)


#import ssd1306

# using default address 0x3C
#i2c = I2C(sda=Pin(4), scl=Pin(5))
#lcd.init_i2c(scl=15,sda= 14, width = 128,height = 64, i2c = 1)
#display = ssd1306.SSD1306_I2C(128, 64, i2c)
#ssd1306.write

#display.text('Hello, World!', 0, 0, 8)

#write_custom_font = ssd1306.Write(display, arial)
#write_custom_font.text("Espresso IDE", 0, 0)

#display.show()





oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

write_custom_font = writer.Writer(oled, freesans20)
from machine import ADC
adc = ADC(4)     # create ADC object on ADC pin
#adc.read_u16()         # read value, 0-65535 across voltage range 0.0v - 3.3v
conversion_factor = 3.3 / (65535)

#for i in range(100):
reading = adc.read_u16() * conversion_factor
temp = int((27 - (reading - 0.706)/0.001721)*10) / 10
write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring("T= " + str(temp)+ "    ")
oled.show()
time.sleep(0.5)
    
#display.contrast(0)

import time
import radiofast
from config import master_config, slave_config, FromMaster, ToMaster
def test_master():
    m = radiofast.Master(master_config)
    send_msg = FromMaster()
    while True:
        rx_msg = m.exchange(send_msg)
        if rx_msg is not None:
            print(rx_msg.i0)
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring(str(rx_msg.i0)+ "    ")
        else:
            write_custom_font.printstring("Timeout     ")
            print('Timeout')
        send_msg.i0 += 1
        oled.show()
        time.sleep_ms(1000)

def test_master():
    m = radiofast.Master(master_config)
    send_msg = FromMaster()
    while True:
        rx_msg = m.exchange(send_msg)
        if rx_msg is not None:
            print(rx_msg.i0)
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring(str(rx_msg.i0)+ "    ")
        else:
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring("Timeout     ")
            print('Timeout')
        send_msg.i0 += 1
        oled.show()
        time.sleep_ms(1000)
        
test_master()
