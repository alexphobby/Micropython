import ntptime,time
from sys import platform
import json
import asyncio
import requests
from machine import RTC

class NTP:
    EPOCH_OFFSET = 0
    UTC_OFFSET = 0
    
    last_update = 0
    rtc = ""
    def __init__(self,wlan,event_wifi_connected,event_request_ready,event_ntp_updated):
        self.wlan = wlan
        result = False
        self.event_wifi_connected = event_wifi_connected
        self.event_request_ready = event_request_ready
        self.event_ntp_updated = event_ntp_updated
        #self.rtc = RTC()
        

        if platform == "ESP32":
            #time based on 2000, not 1970
            EPOCH_OFFSET = 946684800
        else:
            print(f"find epoch offset, platform = {platform}")
        print("NTP initialised, call as update_ntp(event_wifi_connected)")

    async def update_ntp(self):
            while True:
                await self.event_wifi_connected.wait()
                if self.wlan.isconnected() and (self.last_update == 0 or self.last_update != time.localtime()[2]):
                    print("Get ntp time")
                    err=True
                    retry_count = 50
                    while err and retry_count > 0:
                        try:
                            await self.event_request_ready.wait()
                            self.event_request_ready.clear()
                            ntptime.settime()
                            print(f"NTP OK, Time: {time.localtime()}") #, current day: {self.rtc.datetime()[2]}")
                            self.last_update = time.localtime()[2]
                            #await asyncio.sleep_ms(100)
                            await self.update_timezone()
                            err=False
                                
                                    
                                #return
                        except Exception as ex:
                            retry_count-=1
                            self.event_request_ready.set()
                            print(f"err ntp, retry count: {retry_count}, Err: {ex}")
                            await asyncio.sleep(0.6)
                    await asyncio.sleep(50)
                        #await asyncio.sleep_ms(10)
                else:
                    pass
                
                await asyncio.sleep(3600)
                        #pass
                       #print(f"last update: {self.last_update}; RTC: {self.rtc.datetime()[2]}") 
                    
                
    async def update_timezone(self):
            err=True
            retry_count = 50
            while err and retry_count > 0:
                try:
                    print("Get timezone")
                    self.event_request_ready.clear()
                    #res = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest").json()
                    self.UTC_OFFSET = int(requests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest").json()["raw_offset"]/3600)
                    self.event_request_ready.set()
                    result = True
                    print(f"UTC OFFSET {self.UTC_OFFSET}")
                    if self.UTC_OFFSET != 0 :
                        _rtc = RTC()
                        print(f"Before UTC: {_rtc.datetime()}; UTC_OFFSET= {self.UTC_OFFSET}")
                        _tm = time.localtime()
                        _tm = _tm[0:3] + (0,_tm[3]+ self.UTC_OFFSET,) + _tm[4:6] + (0,)
                        print(_tm)
                        
                        _rtc.datetime(_tm)
                        #RTC().datetime(_tm)
                        _tm = None
                        #self.rtc.init((self.rtc.datetime()[0],self.rtc.datetime()[1],self.rtc.datetime()[2],self.rtc.datetime()[3] ,self.rtc.datetime()[4]+ self.UTC_OFFSET,self.rtc.datetime()[5],self.rtc.datetime()[6],self.rtc.datetime()[7]+500000))
                        print(f"After UTC: {_rtc.datetime()}; UTC_OFFSET= {self.UTC_OFFSET}")
                        self.event_ntp_updated.set()
                        #await asyncio.sleep(0.5)
                    err = False
                except Exception as ex:
                    retry_count-=1
                    self.event_request_ready.set()
                    print(f"err getting timezone, err: {ex}")
                    await asyncio.sleep(0.5)

    def ro_time():
        return time.localtime(time.time() + UTC_OFFSET)
    def ro_time_epoch():
        return time.time() + UTC_OFFSET
