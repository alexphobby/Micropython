
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI

#import struct
import writer
import freesans20
#from i2c_init import 
#i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)

#display i2c scan= [60]
oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

write_custom_font = writer.Writer(oled, freesans20)

write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring("Welcome! ")
oled.show()