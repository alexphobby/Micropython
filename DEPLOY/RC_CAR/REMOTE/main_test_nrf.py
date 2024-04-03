import ustruct as struct
import utime
import time
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const

time.sleep(2)
#OLED
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI,PWM
import struct
import writer
import freesans20
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

oled = SSD1306_I2C(128, 64, i2c)
oled.fill(0)

write_custom_font = writer.Writer(oled, freesans20)

write_custom_font.set_textpos(oled,0,0)
write_custom_font.printstring("Welcome! ")
oled.show()
time.sleep(2)
#/OLED

cfg = {"spi": 1, "miso": 12, "mosi": 11, "sck": 10, "csn": 15, "ce": 14}


# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

#cfg = {"spi": 0, "miso": 4, "mosi": 3, "sck": 2, "csn": 15, "ce": 14}
#sck=Pin(2), mosi=Pin(3), miso=Pin(4))
#v1_config = RadioConfig(spi_no = 0, csn_pin = 15, ce_pin = 14)   # V1 Micropower PCB
# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")


def master():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #if cfg["spi"] == -1:
    spi = SPI(1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    #else:
    #    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    num_needed = 10006
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
            write_custom_font.set_textpos(oled,30,0)
            write_custom_font.printstring(f"s:{millis}   ")
            oled.show()

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
        utime.sleep_ms(1000)

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
                for led in leds:
                    if led_state & 1:
                        led.on()
                    else:
                        led.off()
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

#slave()
master()


#/NRF
            



throttle = machine.ADC(26) #2..332..655

steering = machine.ADC(27) # 2..335..655
adc_value = 0
oled.fill(0)
while True:
    #print(f"Throttle: {int(throttle.read_u16()/100)}; Steering: {int(steering.read_u16())}")
    adc_value = steering.read_u16()
    #print(f"Steering: {adc_value}")
    #print(f"Throttle: {int(throttle.read_u16()/100)}; Steering: {int(steering.read_u16()/100)}")
    
    write_custom_font.set_textpos(oled,0,0)
    write_custom_font.printstring(f"T:{int(throttle.read_u16()/100)}      ")
    write_custom_font.set_textpos(oled,30,0)
    write_custom_font.printstring(f"S:{int(steering.read_u16()/100)}      ")
    oled.show()

    time.sleep_ms(550)


#DIMMING
from dim import Dim

last_run_time_dim1 = 0
last_run_time_dim2 = 0
myDim = Dim(pin1=11,pin2=25,min1=0,max1=234,min2=50,max2=134,fade_time_ms=1000)
myDim.dimToOff()
while not myDim.atSetpoint():
    myDim.setDimValueStep()

#/DIMMING
time.sleep(4)

#IR
from my_remotes import remote_samsung
from my_remotes import remote_tiny
from ir_remote_read import ir_remote_read
#/IR


#MOTION
motion_pin= machine.ADC(26)
old_rating = motion_pin.read_u16()
current_read = old_rating

motion_pin_dig = machine.Pin(22,Pin.IN)
sensed_times = 0
def sensed_dig(pin):
    global sensed_times
    motion_pin_dig.irq(trigger=0) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    sensed_times = sensed_times + 1
    print(f"{sensed_times}")
    time.sleep(1)
    motion_pin_dig.irq(trigger=Pin.IRQ_FALLING, handler=sensed_dig) #Pin.IRQ_RISING|Pin.IRQ_FALLING
    
motion_pin_dig.irq(trigger=Pin.IRQ_FALLING, handler=sensed_dig) #Pin.IRQ_RISING|Pin.IRQ_FALLING
while True:
    #print(f"Pin = {motion_pin_dig.value()}")
    #time.sleep_ms(200)
    pass

#/MOTION


#LIGHT SENSOR
lightSensor_pin= machine.ADC(27)
lightNow = int(lightSensor_pin.read_u16()/10)
lightOld = lightNow
lightReadings = []
last_run_time_lightRead = 0
for i in range(20):
    lightReadings.append(lightNow)

lightIndexMax = len(lightReadings)

#LIGHT SENSOR


#PID
from pid import PID
    
def pid_read():
    #read function
    global old_average
    return old_average
        
def pid_output(message):
    #action function
    global myDim
    #print(f"message={message}")
    if message < -2:
        
        myDim.reqIndex1 = myDim.reqIndex1 - 1
        return
        
    if message > 2:
        
        myDim.reqIndex1 = myDim.reqIndex1 + 1
        print(myDim.reqIndex1)
        return
        
pid = PID(pid_read,pid_output,P=0.5, I=-0.01, D=0.1,debug = False)

pid.set_point = 630
    
#    pid.tune(P=-15.0, I=-0.01, D=0.0)
    
#    pid.set_point = i
#    pid.update()

#/PID
time.sleep(1)
oled.fill(0)
oled.show()

average = 0.0
old_average = 0.0

#myDim.reqIndex1 = 100

while True:
    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_lightRead) >= 100:
        last_run_time_lightRead = tmp
        lightReadings.append(int(lightSensor_pin.read_u16()/10))
        lightReadings.pop(0)
        
        #print(f"Instant: {lightReadings[-1]};average: {old_average}")
    #average = 0
    
        for value in lightReadings:
            average = average + value/lightIndexMax
        
        if int(abs(average - old_average)) > 3:
            #print(f"Update: {int(average)}")
            old_average = int(average)
            
            write_custom_font.set_textpos(oled,0,0)
            write_custom_font.printstring(f"AVG: {old_average}   ")
        
        
        pid.update()
        myDim.setDimValueStep(step = 1)
        
        
        
        write_custom_font.set_textpos(oled,30,0)
        write_custom_font.printstring(f"NOW: {lightReadings[-1]}   ")
        oled.show()
        
        average = 0
    
    #current_read = motion_pin.read_u16()
    #current_read = motion_pin.read_u16()
    #if abs(current_read - old_rating) > 5000:
        #print(f"Motion")
    #    pass
    #old_rating = current_read
    #time.sleep_ms(150)
#/MOTION


#/OLED

led_pin = Pin(25,Pin.OUT)
ir_pin = Pin(9,Pin.IN)


debug = False

def ir_callback(remote,command,combo):
    #print(combo)
    global remote_button
    global debug
    #print("try combo: {}".format(combo))
    
    if combo == "R":
        print("Repeat {}".format(remote_button))
    else:
        remote_button = ""
    try:
        remote_button = remote_samsung[combo]
        
    except:
        pass
        
    try:
        remote_button = remote_tiny[combo]
        
    except:
        pass
    print("Button: {}   Cod: {}".format(remote_button,combo))
    if remote_button == "5":
        myDim.dimToOn()

    write_custom_font.set_textpos(oled,30,0) #y,x
    write_custom_font.printstring(remote_button + "      ")
    oled.show()
    

    
    if debug:
        print("Button: {}   Cod: {}".format(remote_button,combo))
        
    
ir_remote_read(ir_pin,ir_callback, debug = debug)    

led_pin.high()
time.sleep_ms(500)
led_pin.low()
time.sleep_ms(500)
        
#extLed_pin = Pin(9,Pin.OUT)
#pin1,pin2,min1,max1,min2,max2,fade_time_ms):



while True:

    
    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_dim1) >= int(myDim.timeStep1) and not myDim.atSetpoint1():
        last_run_time_dim1 = tmp
        myDim.setDimValueStep()
        #print(myStates.atSetpoint1())

    if time.ticks_diff(tmp := time.ticks_ms(), last_run_time_dim2) >= int(myDim.timeStep2) and not myDim.atSetpoint2():
        last_run_time_dim2 = tmp
        myDim.setDimValueStep()

print("Done")

while True:
    #extLed_pin.toggle()
    #led_pin.toggle()
    time.sleep(1)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
 
