import requests
import asyncio
import gc
import time
class WEATHER:
    weather = []
    last_updated_minute = -100
    def __init__(self,event_wifi_connected,event_weather_updated,event_request_ready,event_sleep_ready):
        self.event_wifi_connected = event_wifi_connected
        self.event_weather_updated = event_weather_updated
        self.event_request_ready = event_request_ready
        self.event_sleep_ready = event_sleep_ready
        self._run = asyncio.create_task(self.update_weather())
    
    async def update_weather(self):
        while True:
            #print("update weather if wifi connected")
            await self.event_wifi_connected.wait()
            if abs(self.last_updated_minute - time.localtime()[4]) > 10:
                hour = 0
                try:
                    await self.event_request_ready.wait()
                    self.event_request_ready.clear()
                    self.event_sleep_ready.clear()
                    #self.weather = requests.get("http://api.open-meteo.com/v1/forecast?latitude=44.42&longitude=26.06&hourly=temperature_2m,precipitation&timezone=Europe%2FMoscow&forecast_days=1").json()
                    self.weather = requests.get("http://api.open-meteo.com/v1/forecast?latitude=44.42&longitude=26.06&hourly=apparent_temperature,precipitation,temperature_2m&timezone=Europe%2FMoscow&forecast_days=1").json()
                    self.event_request_ready.set()
                    
                    #print(f"Outside temp: {self.weather["hourly"]["temperature_2m"][time.localtime()[3]]}")
                    for hour in range(time.localtime()[3],23):
                        if self.weather["hourly"]["precipitation"][hour] > 0.5:
                            self.precipitation_hour = hour
                            print(f"Precipitation at {hour}:00")
                            continue
                    print("Weather updated")
                    self.last_updated_minute = time.localtime()[4]
                    self.event_weather_updated.set()
                                
                except Exception as ex:
                    self.event_request_ready.set()
                    self.event_weather_updated.clear()
                    
                    print(f"Weather Exception {ex}")
                #print("await to retrive weather")
                await asyncio.sleep(1*60) #30*60)
            else:
                #print("Time wait")
                self.event_weather_updated.clear()
                self.event_sleep_ready.set()
                await asyncio.sleep(60)

            
            
    def temperature(self):
        temp = -100
        try:
            if time.localtime()[3] < 23:
                return f"{round(self.weather["hourly"]["temperature_2m"][time.localtime()[3]+1])}"
            else:
                return round(self.weather["hourly"]["temperature_2m"][time.localtime()[3]])
        except Exception as ex:
            print(f"Temp error {ex}")
            return -100
    def temperature_feel(self):
        temp = -100
        try:
            #return round(self.weather["hourly"]["temperature_2m"][time.localtime()[3]])
            return round(self.weather["hourly"]["apparent_temperature"][time.localtime()[3]])
        except Exception as ex:
            print(f"Temp error {ex}")
            return -100

    def precipitation(self):
        for hour in range(time.localtime()[3],23):
            if self.weather["hourly"]["precipitation"][hour] > 0.5:
                print(f"Precipitation at {hour}:00")
                return hour
        return None
    

