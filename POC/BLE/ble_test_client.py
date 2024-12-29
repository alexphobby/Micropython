import sys

# ruff: noqa: E402
sys.path.append("")

from micropython import const

import asyncio
#import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214') #0x181A)
#_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')#0x2A6E)


# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    #print(data)
    return str(data,'UTF-8')#struct.unpack("<h", data) #[0] / 100


async def find_temp_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    #aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
    async with scan.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        
        async for result in scanner:
            #print(result.name())
            # See if it matches our name and the environmental sensing service.
            if result.name() == "ESP32" and _ENV_SENSE_UUID in result.services():
                return result.device
    return None


async def main():
    device = await find_temp_sensor()
    if not device:
        print("Temperature sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    
    
    while True:
        try:
            connection = await device.connect()
            temp_service = await connection.service(_ENV_SENSE_UUID)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            continue
        except asyncio.TimeoutError:
            print("Timeout during connection")

        
        while connection.is_connected():
            try:
                temp_deg_c = _decode_temperature(await temp_characteristic.read())
                print(f"Temperature: {temp_deg_c}")#{:.2f}".format(temp_deg_c))
                await asyncio.sleep_ms(500)
            except Exception as ex:
                print(f'Exception: {ex}')
                await asyncio.sleep_ms(1500)
    
    
 #   async with connection:
  

asyncio.run(main())