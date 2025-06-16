import time
from machine import Pin, I2C
from bma400 import BMA400

i2c = ""
known_devices = [["BH1750","Light sensor",0x23,35],["HDC1080","Temp and humidity",0x40,64],["BMP280","Temp, humidity and pressure",0x76,118],["VL53L0X","LIDAR",0x29,41],["SSD1306","OLED display",0x3C,60]] #name,hexa,dec
found_devices = []
if True: #try:
    if (True):
        print("ESP32 - I2C on pins: scl=Pin(3),sda=Pin(4)")
        i2c = I2C(0,scl=Pin(3),sda=Pin(4),freq=800000)
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
            
bma = BMA400(i2c)
#bma_tap=BMA220_TAP(bma) #bma.power_mode = const(0x01)
while True:
    accx, accy, accz = bma.acceleration
    print(f"x:{accx:.2f}Gs, y:{accy:.2f}Gs, z:{accz:.2f}Gs")
    time.sleep(0.5)
