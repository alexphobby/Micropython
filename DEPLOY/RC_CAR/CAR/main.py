import ustruct as struct
import utime
import time
from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01
from micropython import const


time.sleep(2)
#machine.freq(20000000)

#from machine import Pin, I2C, SPI,PWM
import struct

#/OLED

#cfg = {"spi": 1, "miso": 12, "mosi": 11, "sck": 10, "csn": 15, "ce": 14}

#cfg = {"spi": 1, "miso": 12, "mosi": 11, "sck": 10, "csn": 9, "ce": 8}


        
#test_master()

#SERVO
pwm = PWM(Pin(5))
pwm.freq(50)
SERVO_MIN = const(750)
SERVO_MAX=const(1350)

#Function to set an angle
#The position is expected as a parameter
def setServoFill (position):
    pwm.duty_u16(position)
    time.sleep(0.01)

def setServoFillNs (position):
    if position < SERVO_MIN:
        position = SERVO_MIN
    if position > SERVO_MAX:
        position = SERVO_MAX
    
    pwm.duty_ns(int(position*1000))
    time.sleep(0.01)

#servo_trim = -10  # + dreapta - stanga

#servo_middle= int((servo_min+servo_max)/2)

def setServoNs (position,speed):
    global servo_middle
    #print(f"Position: {position}")
    #return
    #speed between -65000 and 65000
    deviate_from_middle = position - servo_middle
    
    #if abs(speed) > 50000:
    #    position = servo_middle + deviate_from_middle * 0.3
    if abs(speed) > 25000:
        position = servo_middle + deviate_from_middle * 25000 / abs(speed)
    #print(f"dev: {deviate_from_middle}; Pos: {position}; Middle: {servo_middle}")
    pwm.duty_ns(int(position*1000))
    #print(f"Pos to: {position*1000}")
    time.sleep(0.01)

#/SERVO

#MAP
from MAP import MAP


steering_map = MAP(54,12,SERVO_MIN,SERVO_MAX) #54..12
throttle_map = MAP(10,53,65000,-65000)  #10...53#


#/MAP
#H-BRIDGE

a1 = Pin(2,Pin.OUT,0)
a2 = Pin(3,Pin.OUT,0)
en = PWM(Pin(4))
#en.freq(2000)
#en.duty_u16(0)

def drive(speed):
    global a1,a1,en
    dir = 0
    speed = int(speed)
    #print(f"Speed: {speed}")
    if speed > -8000 and speed < 8000:
        dir = 0
        #print("deadzone")
    elif speed < 0:
        dir = -1
        
    else:
        dir = 1
    
    if dir==1:
        a1.on()
        a2.off()
        en.duty_u16(abs(speed))
        #print(f"fw {speed}")
    if dir==-1:
        
        a1.off()
        a2.on()
        
        en.duty_u16(abs(speed))
        #print(f"backw {speed}")
    if dir=="B":
        a1.on()
        a2.on()
        
        en.duty_u16(65000)
    if dir==0:
        a1.off()
        a2.off()
        en.duty_u16(0)

drive(0)

#/H-BRIDGE

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

cfg = {"spi": 1, "miso": 8, "mosi": 11, "sck": 10, "csn": 15, "ce": 14}


def slave():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #if cfg["spi"] == -1:
    #spi = SPI(cfg["spi"], sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    spi = SPI(1)
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    #else:
    #    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

    #while True:
        #servo_pos = int(input("Servo Pos:")) # 1350..1150..
        #setServoCycle(steering_val*100)
        #setServoNs(servo_pos)
    #    throttle_val = int(input("throttle:"))
    #    if throttle_val <28:
    #        drive(-1,throttle_val*1000)
    #    elif throttle_val > 35:
    #        drive(1,(30-throttle_val)*2000)
    #    else:
    #        drive(0,throttle_val*100)


    while True:
        
        
        
        
        #time.sleep_ms(100)
        if nrf.any():
            #print("any")
            while nrf.any():
                try:
                #    pass
                #except:
                #    pass
                #if True:
                    #print("w")
                    buf = nrf.recv()
                    
                    throttle_val,steering_val = struct.unpack("ii", buf)
                    
                    throttle_out = throttle_map.map_value(throttle_val)
                    drive(throttle_out)
                    
                    #steering_out = steering_map.map_value(steering_val)
                    setServoFillNs(steering_map.map_value(steering_val))
                except Exception as err:
                    print(err)

slave()
#master()


#/NRF
            



throttle = machine.ADC(26) #2..332..655

steering = machine.ADC(27) # 2..335..655
adc_value = 0
oled.fill(0)
while True:
    print(f"Throttle: {int(throttle.read_u16()/100)}; Steering: {int(steering.read_u16())}")
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
 


