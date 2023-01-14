import utime
from machine import Pin
#from utime import ticks_us
from array import array
machine.freq(250000000)
#import time


def ir_callback(remote,command,combo):
    print(combo)

class ir_remote_read:
    def __init__(self,pin,callback):
        self._pin = pin
        self._callback = callback
        self._last_edge = 0
        self._state = 0
        self._delay = 0
        self._message = ""
        
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self.read) #Pin.IRQ_RISING|Pin.IRQ_FALLING

    def read(self,ir):
    
        _current_edge =  utime.ticks_us()
        
        self._delay = _current_edge - self._last_edge
        
        #delays += str(delay) + " - "
        self._last_edge = _current_edge
        if self._delay > 15000:
            self._state == 0
            #message = ""
            #print("State: {} - Delay: {} - Message: {}".format(state,delay,message))
            return
        if self._state == 0 and self._delay < 12000 and self._delay > 10000:
            self._callback("","","R")
            return
        if self._state == 0 and self._delay < 15000 and self._delay > 6000:
            self._state = 1 #Record messages
            #print("Start state: {} - Delay: {} - Message: {}".format(state,delay,message))
            #message = "b"
            return
        
        
        if self._state == 1 and self._delay < 1700 :
            #print(" zero ")
            self._message += "0"
            #print("Delay: {} - Message: {}".format(delay,message))
            return
        elif self._state == 1 and self._delay < 3000:
            self._message += "1"
            #print("Delay: {} - Message: {}".format(delay,message))
            return
        elif self._delay > 3000 and self._state ==1:
            self._state = 0
            
            try:
                #print("Message: {}".format(message))
                #print("{} - {} - {} - {}".format((message[0:8]),(message[8:16]),(message[16:24]),(message[24:32])))
                #print("{} - {} - {} - {}".format(int(message[0:8],2),int(message[8:16],2),int(message[16:24],2),int(message[24:32],2)))
                #print("Remote: {} - Commands: {} - {}".format(int(message[0:16],2),int(message[16:24],2),int(message[24:32],2)))
                #print("{}_{}".format(int(message[0:16],2),int(message[16:32],2)))
                self._callback(int(self._message[0:16],2),int(self._message[16:32],2),"{}_{}".format(int(self._message[0:16],2),int(self._message[16:32],2)))
                #delays = ""
                
            except:
                #print(delays)
                print("err")
                pass
        
            delays = ""
            message = ""
            return



ir_sensor = Pin(16)

ir_remote_read(ir_sensor,ir_callback)
#ir_sensor.irq(trigger=Pin.IRQ_FALLING, handler=read_code2) #Pin.IRQ_RISING|Pin.IRQ_FALLING



while True:
    utime.sleep(20)
