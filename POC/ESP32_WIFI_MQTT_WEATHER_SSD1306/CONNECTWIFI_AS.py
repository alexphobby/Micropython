import network
import urequests
import time
import secrets
import asyncio
from machine import Pin

#import binascii

class CONNECTWIFI_AS:
#    hotspots = []
    hotspot = ""
    wlan=None
    #wlanPower = Pin(23,Pin.OUT)
    
    #wlan = ""
    i=0
    def __init__(self,event_wifi_connected,hostname="esp-default"):
        self.event_wifi_connected = event_wifi_connected
        """Initialize wifi connection and try all hotspots with a password
            It needs the secrets.py file with PASSWORD = 'pass'
        """
        print("Init wlan")
        network.WLAN(network.AP_IF).active(False)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)
        self.wlan.active(True)
        self.wlan.config(dhcp_hostname=hostname)
        #self.wlan.config(pm=self.wlan.PM_POWERSAVE) #PM_NONE|PM_PERFORMANCE|PM_POWERSAVE
        
        print("call async check_and_connect")
        #self.check_and_connect()
        
        
    async def check_and_connect(self):
        #print(f"check and connect event: {self.event_wifi_connected.state}")
        if self.wlan is None:
            print("no wlan")
            
        if self.wlan.isconnected() == True and self.event_wifi_connected.state:
            self.event_wifi_connected.set()
            
        else:
            print("Need to connect")
            self.event_wifi_connected.clear()
            await self.connect()
        
    
    def is_connected(self):
        
        return self.wlan.isconnected()
        
    async def connect(self):
        #err=True
        counter = 50
        
        while not self.wlan.isconnected() and counter > 0 : #and err:
            
            counter -= 1
            print(f"Wlan not connected, wlan status = {self.wlan.status()}")
            #self.wlan.scan()
            try:
                self.wlan.connect(secrets.SSIDS[0], secrets.PASSWORDS[0])
                await asyncio.sleep(2)
                print(f"wlan status = {self.wlan.status()}")
                while self.wlan.status() in [1,1001,202,201]: #STAT_CONNECTING
                    print(f"Connecting, status: {self.wlan.status()}, is connected: {self.wlan.isconnected()}")
                    await asyncio.sleep(2)
                    
                if self.wlan.isconnected():
                    print("Connected, check for connection")
                    for _ in range(5):
                        if not self.wlan.isconnected():
                            print("conn unstable")
                        await asyncio.sleep(0.5)
                    
                    self.event_wifi_connected.set()
                    print("Connection stable")
                    return
                else:
                    print(f"wlan status = {self.wlan.status()}")
                self.hotspots = []
                print(f"Hotspots: {self.hotspots}")
                    
                while len(self.hotspots) == 0:
                    self.hotspots = self.wlan.scan()
                    #asyncio.sleep(5)
                        
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
                            await asyncio.sleep(5)
                            print(f"Status = {self.wlan.status()}")
                            
                            if self.wlan.status()==1:
                                print(f"Connecting to {str(hotspot[0])}")
                                await asyncio.sleep(3)
                            
                            if self.wlan.status() == -2:
                                print(f"Cannot connect to: {str(hotspot[0])}")
                            
                            if self.wlan.status() == -3:
                                print(f"Cannot connect to: {str(hotspot[0])}, bad auth")
                            
                            if self.wlan.status() == 2:
                                print(f"Wait to connect to: {str(hotspot[0])}")
                                await asyncio.sleep(3)
                            
                            if self.wlan.isconnected():
                                print(f"Connected to: {str(hotspot[0])}")
                                return
                            else:
                                self.wlan.active(False)
                                self.wlan.active(True)
                                await asyncio.sleep(5)
                        
                    #wlan.connect(secrets.SSID, secrets.PASSWORD)
                    #wdt.feed()
                    #time.sleep(2)
                            
            except Exception as ex:
#                pass
                print(f"Err - Cannot connect , current status = {self.wlan.status()}, {ex}")
                time.sleep(1)

        

        
        
        
