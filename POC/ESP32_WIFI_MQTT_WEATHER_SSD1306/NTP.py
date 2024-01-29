import ntptime,time
import sys
import json
import asyncio
import requests
from machine import RTC

class NTP:
    EPOCH_OFFSET = 0
    UTC_OFFSET = 0
    
    last_update = 0
    rtc = ""
    def __init__(self,wlan,event_wifi_connected):
        self.wlan = wlan
        result = False
        self.event_wifi_connected = event_wifi_connected
        self.rtc = RTC()

        if sys.platform == "ESP32":
            #time based on 2000, not 1970
            EPOCH_OFFSET = 946684800
        else:
            print("find epoch offset")
        print("NTP initialised, call as update_ntp(event_wifi_connected)")
        #self._run = asyncio.create_task(self.update_ntp())


    async def update_ntp(self):
        
            while True:
                
                await self.event_wifi_connected.wait()
                print("NTP wifi event ok")
                if self.wlan.isconnected() and (self.last_update == 0 or self.last_update != self.rtc.datetime()[2]):
                    print("Get ntp time")
                    err=True
                    retry_count = 50
                    while err and retry_count > 0:
                        try:
                            ntptime.settime()
                            print(f"NTP OK, Time: {self.rtc.datetime()}") #, current day: {self.rtc.datetime()[2]}")
                            self.last_update = self.rtc.datetime()[2]
                            await asyncio.sleep_ms(100)
                            await self.update_timezone()
                            err=False
                                
                                    
                                #return
                        except Exception as ex:
                            retry_count-=1
                            print(f"err ntp, retry count: {retry_count}, Err: {ex}")
                            await asyncio.sleep(0.6)
                    await asyncio.sleep(50)
                        #await asyncio.sleep_ms(10)
                else:
                    pass
                
                await asyncio.sleep(30)
                        #pass
                       #print(f"last update: {self.last_update}; RTC: {self.rtc.datetime()[2]}") 
                    
                
    async def update_timezone(self):
            err=True
            retry_count = 50
            print("Timezone")
            while err and retry_count > 0:

                try:
                    #res = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest").json()
                    self.UTC_OFFSET = int(requests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest").json()["raw_offset"]/3600)
                    result = True
                    print(f"Before UTC: {self.rtc.datetime()}")
                    if self.UTC_OFFSET != 0 :
                        self.rtc.init((self.rtc.datetime()[0],self.rtc.datetime()[1],self.rtc.datetime()[2],self.rtc.datetime()[3] ,self.rtc.datetime()[4]+ self.UTC_OFFSET,self.rtc.datetime()[5],self.rtc.datetime()[6],self.rtc.datetime()[7]+500000))
                        print(f"After UTC: {self.rtc.datetime()}; UTC_OFFSET= {self.UTC_OFFSET}")
                        await asyncio.sleep(0.5)
                    err = False
                except Exception as ex:
                    retry_count-=1
                    print(f"err getting timezone, err: {ex}")
                    await asyncio.sleep(2)

    def ro_time():
        return time.localtime(time.time() + UTC_OFFSET)
    def ro_time_epoch():
        return time.time() + UTC_OFFSET
