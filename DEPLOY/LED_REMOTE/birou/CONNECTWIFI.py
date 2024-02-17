import network
import urequests
import time
import secrets
from machine import Pin
#import binascii
from sys import platform

class CONNECTWIFI:
#    hotspots = []
    hotspot = ""
    wlan=None
    #wlanPower = Pin(23,Pin.OUT)
    
    #wlan = ""
    i=0
    def __init__(self):
        """Initialize wifi connection and try all hotspots with a password
            It needs the secrets.py file with PASSWORD = 'pass'
        """
        
        self.check_and_connect()
        
        
    def check_and_connect(self):
        while self.wlan is None:
            print("Init wlan")
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            if platform == "rp2":
                time.sleep(6)
            elif platform == "ESP32":
                pass
        
        if self.wlan.isconnected() == False:
            print("Need to connect")
            self.connect()
        else:
            print("Is Connected")
    def is_connected(self):
        return self.wlan.isconnected()
        
    def connect(self):
        #err=True
        counter = 50
        

        while not self.wlan.isconnected() and counter > 0 : #and err:
            counter -= 1
            print(f"Wlan not connected, wlan status = {self.wlan.status()}")
            
            try:
                self.wlan.connect(secrets.SSIDS[0], secrets.PASSWORDS[0])
                time.sleep(1)
                print(f"wlan status = {self.wlan.status()}")
                while self.wlan.status() in [1,1001]: #STAT_CONNECTING
                    print("Connecting")
                    time.sleep(0.5)
                    
                if self.wlan.isconnected():
                    print("Connected!")
                    return
                else:
                    print(f"wlan status = {self.wlan.status()}")
                self.hotspots = []
                print(f"Hotspots: {self.hotspots}")
                    
                while len(self.hotspots) == 0:
                    self.hotspots = self.wlan.scan()
                    time.sleep(1)
                        
                    _i=0
                    print("Available hotspots:")
                    for hotspot in self.hotspots:
                        print(f"{_i}: {hotspot[0]}")
                        _i=_i+1
                    
                    for hotspot in self.hotspots:
                        if len(hotspot[0]) < 3 or str(hotspot[0],"UTF-8") not in secrets.SSIDS:
                            print(f"Skip {hotspot}")
                            continue
                        #if self.wlan.isconnected():
                        #    break
                        
                        for password in secrets.PASSWORDS:
                            print(f"Trying to connect to: {str(hotspot[0])} with password: {password}, current status = {self.wlan.status()}")
                            self.wlan.connect(hotspot[0], password)
                            time.sleep(5)
                            print(f"Status = {self.wlan.status()}")
                            
                            if self.wlan.status()==1:
                                print(f"Connecting to {str(hotspot[0])}")
                                time.sleep(3)
                            
                            if self.wlan.status() == -2:
                                print(f"Cannot connect to: {str(hotspot[0])}")
                            
                            if self.wlan.status() == -3:
                                print(f"Cannot connect to: {str(hotspot[0])}, bad auth")
                            
                            if self.wlan.status() == 2:
                                print(f"Wait to connect to: {str(hotspot[0])}")
                                time.sleep(3)
                            
                            if self.wlan.isconnected():
                                print(f"Connected to: {str(hotspot[0])}")
                                return
                            else:
                                self.wlan.active(False)
                                self.wlan.active(True)
                                time.sleep(5)
                        
                    #wlan.connect(secrets.SSID, secrets.PASSWORD)
                    #wdt.feed()
                    #time.sleep(2)
                            
            except Exception as ex:
#                pass
                print(f"Err - Cannot connect, current status = {self.wlan.status()}, {ex}")
                time.sleep(1)

        

        
        
        