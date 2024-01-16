import utime
from machine import Pin
#from utime import ticks_us
#from array import array
#machine.freq(250000000)
#import time


def ir_callback(remote,command,combo,ac=True):
    print(combo)

class ir_remote_read:
    def __init__(self,pin,callback,ac=False):
        self._pin = pin
        self._callback = callback
        self._ac = ac
        self._last_edge = 0
        self._bits = 0
        self._state = 0
        self._delay = 0
        self._message = ""
        
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self.read) #Pin.IRQ_RISING|Pin.IRQ_FALLING

    def read(self,ir):
    
        _current_edge =  utime.ticks_us()
        
        self._delay = _current_edge - self._last_edge
        
        #delays += str(delay) + " - "
        self._last_edge = _current_edge
        if self._delay > 15000: #Reset to 0 - await IR start
            self._state == 0
            #message = ""
            #print("State: {} - Delay: {} - Message: {}".format(state,delay,message))
            return
        if self._state == 0 and self._delay > 10000 and self._delay < 12000 :
            self._callback("","","R")
            self._bits = 0
            return
        if self._state == 0 and self._delay < 15000 and self._delay > 3000:
            self._state = 1 #Record messages
            #print("Start state: {} - Delay: {} - Message: {}".format(state,delay,message))
            #message = "b"
            return
        
        
        if self._state == 1 and self._delay < 1600 :
            #print(" zero ")
            self._message += "0"
            self._bits += 1
            #print("Delay: {} - Message: {}".format(delay,message))
            return
        elif self._state == 1 and self._delay < 3000:
            self._message += "1"
            self._bits += 1
            #print("Delay: {} - Message: {}".format(delay,message))
            return
        elif self._bits > 38 or (self._delay > 3000 and self._state ==1) :
            self._state = 0
            
            #print("Message: {}".format(self._message))
            #self._callback(int(self._message[0:16],2),int(self._message[16:32],2),"{}_{}".format(int(self._message[0:16],2),int(self._message[16:32],2)))
            #self._message = ""
            try:
                #pass
                #print("Message: {}".format(self._message))
                #print("{} - {} - {} - {}".format((message[0:8]),(message[8:16]),(message[16:24]),(message[24:32])))
                #print("{} - {} - {} - {}".format(int(message[0:8],2),int(message[8:16],2),int(message[16:24],2),int(message[24:32],2)))
                #print("Remote: {} - Commands: {} - {}".format(int(message[0:16],2),int(message[16:24],2),int(message[24:32],2)))
                #print("{}_{}".format(int(message[0:16],2),int(message[16:32],2)))
                
                #print("bits:{} message: {}".format(self._bits,self._message))
                self._callback(int(self._message[0:16],2),int(self._message[16:32],2),"{}_{}".format(int(self._message[0:16],2),int(self._message[16:32],2)))
                self._message = ""
                self._bits = 0
                
                #delays = ""
                
            except:
                #print(delays)
                print("err")
                pass
        
            delays = ""
            message = ""
            #print("Bits: {}".format(self._bits))
            self._bits = 0
            return



