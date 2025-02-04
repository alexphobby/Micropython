#Usage: from i2c_init import *
from sys import platform
from gc import collect

from machine import Pin,I2C

#Enable discovery of devices
temp_sensor_enabled = True
oled_enabled = True
light_sensor_enabled = True

i2c = ""
known_devices = [["BH1750","Light sensor",0x23,35],["HDC1080","Temp and humidity",0x40,64],["BMP280","Temp, humidity and pressure",0x76,118],["VL53L0X","LIDAR",0x29,41],["SSD1306","OLED display",0x3C,60]] #name,hexa,dec
found_devices = []
if True: #try:
    if (platform == "esp32"):
        print("ESP32 - I2C on pins: scl=Pin(3),sda=Pin(4)")
        i2c = I2C(0,scl=Pin(3),sda=Pin(4),freq=800000)
        print("I2c init done")
    else:
        print("non ESP32")
        i2c = I2C(0,scl=Pin(1),sda=Pin(0))
        
    found_addresses = i2c.scan()
    for found_address in found_addresses:
        #print(f"Device iterated: {device[0]}")
        known = False
        for known_device in known_devices:
            if known_device[3] == found_address:
                known =True
                print(f"Found I2C: {known_device[0]} - {known_device[1]}")
                found_devices.append(known_device[0])
        if not known:
            print(f"Not known device: {found_address}")
#collect()
#except:
#    print("no i2c")


if "BMP280" in found_devices and temp_sensor_enabled:
    #print("BMP280")
    from bmp280_util import bmp280_util
    temp_sensor = bmp280_util(i2c)
    print(f"Temperature: {temp_sensor.temperature()}")
elif "HDC1080" in found_devices and temp_sensor_enabled:
    #print("HDC1080")
    from hdc1080_util import hdc1080_util
    temp_sensor = hdc1080_util(i2c)
else:
    from dummy_temp_sensor import *
    temp_sensor = dummy_temp_sensor()

oled = None
oled_write = None


if oled_enabled is True and "SSD1306" in found_devices:
    #print("SH1106")
    from sh1106 import SH1106_I2C
    from writer import Writer
    import consolas12,consolas10
    oled = SH1106_I2C(128, 64, i2c,rotate=0) #180
    oled.contrast(2)
    oled_write = Writer(oled, consolas12) #,verbose=False)18 caractere 7 px/char
    oled_write.set_textpos(oled,0,0)
    oled_write.printstring(f"Loading...")
    oled.show()



if "BH1750" in found_devices and light_sensor_enabled:
    print("found BH1750")
    from bh1750_util import *
    light_sensor = bh1750_util(i2c)
else:
    from dummy_light_sensor import *
    light_sensor = dummy_light_sensor()
    
print("done i2c init")

