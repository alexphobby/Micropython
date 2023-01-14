# Generic Tests for radio-fast module.
# Modify config.py to provide master_config and slave_config for your hardware.
import machine, radiofast
import time
from config import master_config, slave_config, FromMaster, ToMaster

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI,PWM
import struct

time.sleep(5)

led_pin = Pin(25,Pin.OUT)
pwm_pin1 = Pin(13,Pin.OUT)
pwm_pin2 = Pin(11,Pin.OUT)

pwm1 = PWM(pwm_pin1)

pwm1.freq(50)
pwm1.duty_u16(int(65536/2))

pwm2 = PWM(pwm_pin2)

pwm2.freq(210)
pwm2.duty_u16(5000)

#i2c = I2C(0)   # default assignment: scl=Pin(9), sda=Pin(8)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

import writer
import freesans20



oled_pin = SSD1306_I2C(128, 64, i2c)
oled_pin.fill(0)

write_custom_font = writer.Writer(oled_pin, freesans20)

write_custom_font.set_textpos(oled_pin,0,0)
write_custom_font.printstring("Welcome! ")
oled_pin.show()


def test_master():
    m = radiofast.Master(master_config)
    send_msg = FromMaster()
    while True:
        led_pin.toggle()
        result = m.exchange(send_msg)
        if result is not None:
            print(result.i0)
        else:
            print('M Timeout')
        send_msg.i0 += 1
        time.sleep_ms(1000)

def test_slave():
    
    s = radiofast.Slave(slave_config)
    send_msg = ToMaster()
    while True:
        led_pin.toggle()
        result = s.exchange(send_msg)       # Wait for master
        if result is not None:
            print(result.i0)
            oled_pin.fill(0)
            write_custom_font.set_textpos(oled_pin,0,0)
            write_custom_font.printstring(str(result.i0))
            oled_pin.show()

        else:
            print('S Timeout')
            oled_pin.fill(0)
            write_custom_font.set_textpos(oled_pin,0,0)
            write_custom_font.printstring("Timeout")
            oled_pin.show()

        send_msg.i0 += 1

test_slave()
#test_master()






