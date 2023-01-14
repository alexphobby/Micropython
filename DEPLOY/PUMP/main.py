# Generic Tests for radio-fast module.
# Modify config.py to provide master_config and slave_config for your hardware.
import machine #, radiofast
import time
from time import ticks_ms, ticks_diff
#from config import master_config, slave_config, FromMaster, ToMaster

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI,PWM
from machine import Timer
import onewire,ds18x20

import struct

last_run_time = 0

time_wait_start_pump = int(30 * 1000 * 60)
time_wait_stop_pump = int(2 * 1000 * 60)


led_pin = Pin(25,Pin.OUT)
load_pin = Pin(22,Pin.OUT)

pir_pin = Pin(5,Pin.IN,Pin.PULL_DOWN)

load_pin.high()
led_pin.low()


time.sleep(30)


# the device is on GPIO12
dat = machine.Pin(2)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
rom = ds.scan()[0]
# print('found devices:', roms)

# loop 10 times and print all temperatures
ds.convert_temp()
time.sleep_ms(750)
ds.read_temp(rom)
#for rom in roms:
print(ds.read_temp(rom), end=' ')
#    print()




sensed = False

timer = Timer()

def load_off(timer):
    global last_run_time
    
    load_pin.high()
    led_pin.low()
    last_run_time = ticks_ms()

#timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)





def pir_sense(pin):
    global sensed
    
    pin.irq(trigger=0) #0|Pin.IRQ_RISING|Pin.IRQ_FALLING
    print("PIR")
    sensed = True
    pin.irq(trigger=Pin.IRQ_RISING, handler=pir_sense) #Pin.IRQ_RISING|Pin.IRQ_FALLING

pir_pin.irq(trigger=Pin.IRQ_RISING, handler=pir_sense) #Pin.IRQ_RISING|Pin.IRQ_FALLING


while True:
    if ticks_diff(tmp := ticks_ms(), last_run_time) >= time_wait_start_pump or last_run_time == 0:
        
        #print("elapsed")
        #print(sensed)
        if sensed:
            #print("sensed")
            last_run_time = tmp
            
            load_pin.low()
            led_pin.high()

            timer.init(period=time_wait_stop_pump, mode=Timer.ONE_SHOT, callback=load_off)   # Timer.ONE_SHOT . Period in ms
            sensed=False
        else:
            ds.convert_temp()
            time.sleep_ms(750)
            temp = ds.read_temp(rom)
            if int(temp) > 30:
                load_off(temp)

    #print(pir_pin.value())
    time.sleep(0.5)

import onewire,ds18x20

# the device is on GPIO12
dat = machine.Pin(2)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('found devices:', roms)

# loop 10 times and print all temperatures
for i in range(100):
    print('temperatures:', end=' ')
    ds.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(ds.read_temp(rom), end=' ')
    print()
    
    
    
#pwm_pin1 = Pin"""Test for nrf24l01 module.  Portable between MicroPython targets."""

import usys
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

if usys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 5}
elif usys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 33, "sck": 25, "csn": 26, "ce": 27}
elif usys.platform == "rp2":  # Software SPI
    print("pi pico")
    cfg = {"spi": 1, "miso": 12, "mosi": 11, "sck": 10, "csn": 15, "ce": 14}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")


def master():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #if cfg["spi"] == -1:
    spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    #else:
    #    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    num_needed = 16
    num_successes = 0
    num_failures = 0
    led_state = 0

    print("NRF24L01 master mode, sending %d packets..." % num_needed)

    while num_successes < num_needed and num_failures < num_needed:
        # stop listening and send packet
        nrf.stop_listening()
        millis = utime.ticks_ms()
        led_state = max(1, (led_state << 1) & 0x0F)
        print("sending:", millis, led_state)
        try:
            nrf.send(struct.pack("ii", millis, led_state))
        except OSError:
            pass

        # start listening again
        nrf.start_listening()

        # wait for response, with 250ms timeout
        start_time = utime.ticks_ms()
        timeout = False
        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
                timeout = True

        if timeout:
            print("failed, response timed out")
            num_failures += 1

        else:
            # recv packet
            (got_millis,) = struct.unpack("i", nrf.recv())

            # print response and round-trip delay
            print(
                "got response:",
                got_millis,
                "(delay",
                utime.ticks_diff(utime.ticks_ms(), got_millis),
                "ms)",
            )
            num_successes += 1

        # delay then loop
        utime.sleep_ms(250)

    print("master finished sending; successes=%d, failures=%d" % (num_successes, num_failures))


def slave():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #if cfg["spi"] == -1:
    spi = SPI(cfg["spi"], sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    #else:
    #    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

    while True:
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                millis, led_state = struct.unpack("ii", buf)
                print("received:", millis, led_state)
                if led_state & 1:
                    load_pin.low()
                    led_pin.high()
                else:
                    load_pin.high()
                    led_pin.low()
                led_state >>= 1
                utime.sleep_ms(_RX_POLL_DELAY)

            # Give master time to get into receive mode.
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            nrf.stop_listening()
            try:
                nrf.send(struct.pack("i", millis))
            except OSError:
                pass
            print("sent response")
            nrf.start_listening()

slave()

print("NRF24L01 test module loaded")
print("NRF24L01 pinout for test:")
print("    CE on", cfg["ce"])
print("    CSN on", cfg["csn"])
print("    SCK on", cfg["sck"])
print("    MISO on", cfg["miso"])
print("    MOSI on", cfg["mosi"])
print("run nrf24l01test.slave() on slave, then nrf24l01test.master() on master")






