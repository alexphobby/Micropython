#Usage: from i2c_init import *
import sys

from machine import Pin,I2C
i2c = ""
known_devices = [["BH1750","Light sensor",0x23,35],["HDC1080","Temp and humidity",0x40,64],["VL53L0X","LIDAR",0x29,41],["SSD1306","OLED display",0x3C,60]] #name,hexa,dec

if True: #try:
    if (sys.platform == "esp32"):
        print("ESP32 - I2C on pins: scl=Pin(3),sda=Pin(4)")
        i2c = I2C(0,scl=Pin(3),sda=Pin(4))
    else:
        print("non ESP32")
        i2c = I2C(0,scl=Pin(1),sda=Pin(0))
        
    found_devices = i2c.scan()
    for found_device in found_devices:
        #print(f"Device iterated: {device[0]}")
        known = False
        for known_device in known_devices:
            if known_device[3] == found_device:
                known =True
                print(f"Found I2C: {known_device[0]} - {known_device[1]}")
        if not known:
            print(f"Not known device: {found_device}")
        
#except:
#    print("no i2c")