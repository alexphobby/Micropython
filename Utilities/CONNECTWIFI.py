import network
import urequests
import time
import secrets
from machine import Pin


class CONNECTWIFI:
#    hotspots = []
    hotspot = ""
    wlan=None
    wlanPower = Pin(23,Pin.OUT)
    
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
            #time.sleep(1)
            self.wlan.active(True)
            #time.sleep(2)
            
            if self.wlan is None:
                print("Cycle power to radio")
                self.wlanPower.off()
                time.sleep(1)
                self.wlanPower.on()
                time.sleep(1)    
        
        if self.wlan.isconnected() == False:
            print("Need to connect")
            self.connect()
        else:
            print("Is Connected")
    def is_connected(self):
        if self.wlan.status() == 3:
            return True
        else:
            return False
        
    def connect(self):

        while not self.wlan.isconnected():
            print(f"Wlan not connected, wlan status = {self.wlan.status()}")
            #define CYW43_LINK_DOWN (0)
            #define CYW43_LINK_JOIN (1)
            #define CYW43_LINK_NOIP (2)
            #define CYW43_LINK_UP (3)
            #define CYW43_LINK_FAIL (-1)
            #define CYW43_LINK_NONET (-2)
            #define CYW43_LINK_BADAUTH (-3)
#            if True:
            try:
                if self.wlan.status() == 1: # after wlan.active(True)
                    print("Joining")
                    time.sleep(2)
                
                if self.wlan.status() != 2 : # after wlan.active(True)
                    print(f"wlan status = {self.wlan.status()}")
                    self.hotspots = []
                    print(f"Hotspots: {self.hotspots}")
                    while len(self.hotspots) == 0:
                        self.hotspots = self.wlan.scan()
                        
                    _i=0
                    print("Available hotspots:")
                    for hotspot in self.hotspots:
                        print(f"{_i}: {hotspot[0]}")
                        _i=_i+1
                    
                    for hotspot in self.hotspots:
                        #if self.wlan.isconnected():
                        #    break
                        
                        for password in secrets.PASSWORDS:
                            print(f"Trying to connect to: {str(hotspot[0])} with password: {password}, current status = {self.wlan.status()}")
                            self.wlan.connect(hotspot[0], password)
                            time.sleep(5)
                            
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
                            
                            if self.wlan.status() == 3:
                                print(f"Connected to: {str(hotspot[0])}")
                                return
                        
                    #wlan.connect(secrets.SSID, secrets.PASSWORD)
                    #wdt.feed()
                    #time.sleep(2)
                            
            except Exception as ex:
#                pass
                print(f"Err - Cannot connect to {hotspot[0]}, current status = {self.wlan.status()}, {ex}")
                time.sleep(10)

        

        
        
        