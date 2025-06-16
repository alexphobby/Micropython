#connectors:
#4x ana joysticks
#2x ana triggers
#2x dig triggers
#4x buttons
from machine import Pin,ADC
import asyncio
import aioespnow
import network

sta = network.WLAN(network.STA_IF)
#sta.config(protocol=network.MODE_LR)
sta.active(True)
sta.config(protocol=network.MODE_LR)

s_x_a_pin = 5
s_y_a_pin = 6
d_x_a_pin = 4
d_y_a_pin = 3
th_ana_pin = 1

br_ana_pin = 2

b_a_dig_pin =40
b_b_dig_pin = 39
b_x_dig_pin = 18 #41
b_y_dig_pin = 41

b_trg_s_dig_pin = 11
b_trg_d_dig_pin = 45

s_x_a = ADC(s_x_a_pin,atten=ADC.ATTN_11DB)
s_y_a = ADC(s_y_a_pin,atten=ADC.ATTN_11DB)
d_x_a = ADC(d_x_a_pin,atten=ADC.ATTN_11DB)
d_y_a = ADC(d_y_a_pin,atten=ADC.ATTN_11DB)
th_ana = ADC(th_ana_pin,atten=ADC.ATTN_11DB)
br_ana = ADC(br_ana_pin,atten=ADC.ATTN_11DB)

b_a_dig = Pin(b_a_dig_pin,Pin.IN,Pin.PULL_UP)
b_b_dig = Pin(b_b_dig_pin,Pin.IN,Pin.PULL_UP)
b_x_dig = Pin(b_x_dig_pin,Pin.IN,Pin.PULL_UP)
b_y_dig = Pin(b_y_dig_pin,Pin.IN,Pin.PULL_UP)

b_trg_s_dig = Pin(b_trg_s_dig_pin,Pin.IN,Pin.PULL_UP)
b_trg_d_dig = Pin(b_trg_d_dig_pin,Pin.IN,Pin.PULL_UP)

analog_inputs = {"s_x_a":s_x_a,"s_y_a":s_y_a,"d_x_a":d_x_a,"d_y_a":d_y_a,"th_ana":th_ana,"br_ana":br_ana}
digital_inputs= {"b_a_dig":b_a_dig,"b_b_dig":b_b_dig,"b_x_dig":b_x_dig,"b_y_dig":b_y_dig,"b_trg_s_dig":b_trg_s_dig,"b_trg_d_dig":b_trg_d_dig}

payload={"s_x_a":0,"s_y_a":0,"d_x_a":0,"d_y_a":0,"th_ana":0,"br_ana":0,"b_a_dig":0,"b_b_dig":0,"b_x_dig":0,"b_y_dig":0,"b_trg_s_dig":0,"b_trg_d_dig":0}

payload={"b_a_dig":0,"b_b_dig":0,"b_x_dig":0,"b_y_dig":0,"b_trg_s_dig":0,"b_trg_d_dig":0}

async def transmit_espnow():
    global payload
    print("Init transmit")
    e = aioespnow.AIOESPNow()
    e.active(True)
    broadcast = b'\xff\xff\xff\xff\xff\xff'
    try:
        e.add_peer(broadcast)
    except Exception as ex:
        print(f'Add peer: {ex}')
    
    while True:
        try:
            await e.asend(broadcast, str(payload),sync=False)
            print(f'Sent: {payload}')
        except Exception as ex:
            print(ex)
        await asyncio.sleep(0.5)
    
    
async def receive_espnow():
    #global e
    import aioespnow
    await event_wifi_connected.wait()
    e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
    e.active(True)
    broadcast = b'\xff\xff\xff\xff\xff\xff'
    try:
        e.add_peer(broadcast)
    except Exception as ex:
        print(f'Add peer: {ex}')
    
    print("Listen ESPNOW")
    print(f"WIFI channel: {wifi.channel()}")
    async for mac, msg in e:
        print(f'Echo: {msg} - {str(msg,"UTF-8")}')
        if str(msg,"UTF-8") == "PING":
            print("PING")
            try:
                e.add_peer(mac)
            except Exception as ex:
                print(f'Add peer {mac}: {ex}')
            try:
                await e.asend(mac, "PONG",False)
            except Exception as ex:
                print(f'Sent to {mac}: {ex}')
        
        if str(msg,"UTF-8") in ["ON","1"]:
            setSeconds()
            my_print("on ESPNOW")
        elif str(msg,"UTF-8") == "CH":
            try:
                e.add_peer(mac)
            except Exception as ex:
                print(f'Add peer {mac}: {ex}')
            try:
                await e.asend(mac, str(wifi.channel()),False)
            except Exception as ex:
                print(f'Sent to {mac}: {ex}')

        #elif str(msg,"UTF-8") == "1":
        #    print("on")
        
        elif str(msg,"UTF-8") == "0":
            print("off")
        else:
            print(str(msg,"UTF-8"))


async def read_analog():
    global payload
    print("Init read analog")
    while True:
        for input in analog_inputs:
            #analog_inputs[input].read_u16()
            #print(f'{input} - {analog_inputs[input].read_u16()}')
            #payload[input] = analog_inputs[input].read_u16()
            pass
        
        for input in digital_inputs:
            payload[input] = digital_inputs[input].value()
        await asyncio.sleep(0.5)
        
async def main():
    t_read_analog = None
    t_read_analog = asyncio.create_task(read_analog())
    
    t_transmit_espnow = asyncio.create_task(transmit_espnow())
    #t_read_pulse_in = asyncio.create_task(read_pulse_in())
    #t_print_pulse_in = asyncio.create_task(print_pulse_in())
    t_clear_oled = None
    t_receive_espnow = None
    while True:
        await asyncio.sleep(1)
        #gc.collect()
        
        
        if t_read_analog is None or t_read_analog.done():
            t_read_analog = None
            print("restart task t_read_analog")
            t_read_analog = asyncio.create_task(read_analog())
        
        await asyncio.sleep(30)

try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()
    #loop = asyncio.get_event_loop()
    #loop.run_forever()
    #asyncio.run(heartbeat_oled(client))
#except Exception as ex:
#    my_print(f"Catch: {ex}")

