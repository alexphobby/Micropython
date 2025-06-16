


from time import sleep
#import ubinascii
#guid = str(ubinascii.hexlify(unique_id()),"UTF-8")

motion_vcc_pin = 7
#motion_vcc = Pin(motion_vcc_pin, Pin.OUT,value=1)

from CONFIG import CONFIG
config=CONFIG(debug=True)

from machine import Pin
import RTC
import json
rtc=RTC()
light_on=False


def init_espnow():
    import network
    import esp32
#    import asyncio
    import espnow
    e = espnow.ESPNow()
    e.active(True)
    peer_receiver = b'4\xb7\xdaR\xf8\x00'   # MAC address of peer's wifi interface
    peer_sender = b'\xc0N0\x81A`' #sender mac   # MAC address of peer's wifi interface
    broadcast = b'\xff\xff\xff\xff\xff\xff'
    e.add_peer(broadcast)

    try:
        sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
        sta.active(True)
        sta.config(channel = config.read("channel"))
        #if not ping():
        #    scan()
         
    except Exception as ex:
        print(f'Enabling sta err: {ex}')



try:
    #if len(rtc.memory())
    if json.loads(rtc.memory())['light_status'] == 1:
        print("load from mem, light on")
    else:
        print("get light status")
        init_espnow()
        get_light_status()
        
    





if False:
    from machine import Pin,ADC
    measure_vcc = Pin(12,mode = Pin.OUT)
    measure_adc_pin = 13
    adc = ADC(measure_adc_pin,atten=ADC.ATTN_6DB)
    measure_vcc.value(1)
    sleep(0.1)
    v_batt = adc.read_uv()*2/1000000  + 0.4
    measure_vcc.value(0)
    print(f'Battery: {v_batt}V')

    if v_batt < 3.1:
        deepsleep_time = 60000
        battery_low = False
#motion sensor
deepsleep_time = 60000
battery_low = False 

motion_sense_pin = 4
#motion_vcc = Pin(motion_vcc_pin, Pin.OUT,hold=True,drive=Pin.DRIVE_3,value=1) #, drive=Pin.DRIVE_3) #,value=0)
motion_vcc = Pin(motion_vcc_pin, Pin.OUT,hold=True,value=0) #, drive=Pin.DRIVE_3) #,value=0)
motion_sense = Pin(motion_sense_pin,Pin.IN, Pin.PULL_DOWN)


#e = aioespnow.AIOESPNow()  # Returns AIOESPNow enhanced with async support
#esp32.gpio_deep_sleep_hold(True)
led = Pin(2,Pin.OUT)
led.off()

channel = 0
mac = ""

#debug =  Pin(38,Pin.IN, Pin.PULL_DOWN)


#motion_vcc.value(1)
print("enter")
import esp32
#motion_sense.irq(isr,Pin.IRQ_LOW_LEVEL,wake=SLEEP)
from machine import lightsleep,deepsleep
esp32.wake_on_ext0(4, esp32.WAKEUP_ANY_HIGH)

lightsleep(30000)
esp32.wake_on_ext0(None, esp32.WAKEUP_ANY_HIGH)
#motion_vcc = Pin(motion_vcc_pin, Pin.OUT,hold=True)
print("exit")



if motion_sense.value() != 1:
    print("Not sensed")
    #motion_vcc.value(1)
    motion_vcc = Pin(motion_vcc_pin, Pin.OUT,hold=True,value=1)
    deepsleep(deepsleep_time)
#elif debug.value()== 0:
else:
    print("Sensed")
    
    motion_vcc = Pin(motion_vcc_pin, Pin.OUT,hold=True,value=1)

    init_espnow()    
    try:
        #led.on()
        e.send(broadcast, f'1',False)
        print("sent")
    except Exception as ex:
        print(ex)
    sta.active(False) 
    #sleep(0.2)
    #led.off()
    print(f"enter deepsleep for {deepsleep_time}")
    deepsleep(deepsleep_time)

def ping():
    e.send(broadcast, f'PING',False)
    mac,response = e.recv(1000)
    print(f"Channel: {config.read("channel")}, received: {mac} {str(response)}")
    if response is not None and response == b'PONG':
        print(f'Confirmed response: {response}')
        return True
    else:
        print(f'NOT confirmed response: {response}')
        return False


        
        
def get_light_status():
    e.send(broadcast, f'STATUS',False)
    mac,response = e.recv(1000)
    print(f"received: {mac} {str(response)}")
    if response is not None and response == in [b'ON_AUTO',b'ON']:
        print(f'Confirmed response: {response}')
        
        return True
    else:
        print(f'NOT confirmed response: {response}')
        return False

def scan():
    for ch in range(1,12):
        sta.config(channel = ch)
        e.send(broadcast, f'CH',False)
        
        #time.sleep(1)
        mac,channel = e.recv(1000)
        print(f"Channel: {ch}, received: {mac} {channel}")
        if channel is not None and int(channel) > 0:
            sta.config(channel = int(channel))
            config.write("channel",int(channel))
            break
    print(f'Channel: {channel}')

try:
    sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
    sta.active(True)
    sta.config(channel = config.read("channel"))
    if not ping():
        scan()
    sta.active(False)
except Exception as ex:
    print(f'Enabling sta err: {ex}')


def click(pin):
    print("click")
    pin.irq(trigger=0)
    try:
        #print(sta.active())
        sta.active(True)
        if sta.config("channel") != config.read("channel"):
            #print(f'wrong ch: {sta.config("channel")} - {config.read("channel")}')
            sta.config(channel = config.read("channel"))
            
        #while not sta.active():
        #    sleep(0.1)
        #    print("sleep")
        #print(sta.config("channel"))
        #sta.config(channel = int(channel))
        
    except Exception as ex:
        print(ex)
    
    try:
        led.on()
        e.send(broadcast, f'1',False)
        print("sent")
    except Exception as ex:
        print(ex)
    #lightsleep(1)
    sleep(1)
    
    pin.irq(trigger=Pin.IRQ_FALLING,handler=click)
    
    sta.active(False)
    while sta.active():
        sleep(0.1)
    led.off()
    #lightsleep(1)
    


#switch.irq(trigger=Pin.IRQ_FALLING,handler=click)
#while True:
    
    
    
#    try:
#        e.add_peer(peer_receiver)      # Must add_peer() before send()
#    except Exception as ex:
#        print(ex)

#else:
#    led = Pin(2,Pin.OUT)
#    led.off()

#sta.disconnect()      # For ESP8266

print(f'guid: {guid}')
print(f'mac: {sta.config("mac")}')


async def send():
    i=1
    await asyncio.sleep(1)
    try:
        e.add_peer(peer_receiver)      # Must add_peer() before send()
    except Exception as ex:
        print(ex)

    #e.send(peer_receiver, "Starting...")
    

    while True:
        #await event_matter.wait()
        #event_matter.clear()
        print(f"Send ping {i}")
        #e.send(peer_receiver, "ping") #, True)
        await e.asend(peer_receiver, f'ping {i}')
        i += 1
        await asyncio.sleep(5)

async def receive():
    global e
    async for mac, msg in e:
        print(f'Echo: {msg} - {str(msg,"UTF-8")}')
        if str(msg,"UTF-8") == "1":
            led.on()
            sleep(1)
            led.off()
            print("on")
        else:
            led.off()
            print("off")

    while False:
        print("Try receive")
        host, msg = e.recv()
        if msg:             # msg == None if timeout in recv()
            print(host, msg)
        await asyncio.sleep(0.5)

async def worker():
    await asyncio.sleep(5)
    while True:
        print("worker")
        await asyncio.sleep(5)

async def main():
    #t_connect = asyncio.create_task(wifi.check_and_connect())
    t_send = None #asyncio.create_task(process_ir_queue(ir_queue))
    #asyncio.create_task(worker())
    #if role == "sender":
    #    print("Sender Role")
        #asyncio.create_task(send())

        
    #else:
    #    print("Receiver Role")
    #    asyncio.create_task(receive())
    #sleep(1)
    while True:
        await asyncio.sleep(0.5)
        #sta.active(False)
        #while sta.active():
        #    sleep(0.1)
        #lightsleep(1)
        #gc.collect()
        #if t_send is None or t_send.done():
        #    t_send = None
        #    print("restart task t_process_ir_queue")
        #    t_send = asyncio.create_task(send())
      


try:
    print("Async call main")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted")
finally:
    asyncio.new_event_loop()