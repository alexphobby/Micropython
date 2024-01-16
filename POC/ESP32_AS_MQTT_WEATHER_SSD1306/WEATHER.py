import requests
import asyncio
import gc
import time
class WEATHER:
    weather = []
    def __init__(self,wlan):
        self.wlan = wlan
        self._run = asyncio.create_task(self.update_weather())
    
    async def update_weather(self):
        while True:
            if(self.wlan.isconnected()):
                print("try to get weather details")
                hour = 0
                try:
                    gc.collect()
                    self.weather = requests.get("http://api.open-meteo.com/v1/forecast?latitude=44.42&longitude=26.06&hourly=temperature_2m,precipitation&timezone=Europe%2FMoscow&forecast_days=1").json()
                    
                    print(f"Outside temp: {self.weather["hourly"]["temperature_2m"][time.localtime()[3]]}")
                    for precipitation in self.weather["hourly"]["precipitation"]:
                        #print(weather["hourly"]["precipitation"][hour])
                        if self.weather["hourly"]["precipitation"][hour] > 0.5:
                            print(f"Precipitation at {hour}:00")
                        hour +=1
                except Exception as ex:
                    print(f"Weather Exception {ex}")
                await asyncio.sleep(30*60)
            else:
                print("No weather yet, no wlan")
                await asyncio.sleep(5)

            
            
    def temperature(self):
        temp = -100
        try:
            return self.weather["hourly"]["temperature_2m"][time.localtime()[3]]
        except Exception as ex:
            print(f"Temp error {ex}")
            return -100
    
    def precipitation(self):
        for hour in range(time.localtime()[3],23):
            if self.weather["hourly"]["precipitation"][hour] > 0.5:
                print(f"Precipitation at {hour}:00")
                return hour

        return ""
    

