import utime
from machine import Pin
from array import array
from machine import Timer
#from utime import ticks_us
#from array import array
#machine.freq(250000000)
#import time


def ir_callback(remote,command,combo,ac=True):
    pass
    #print(combo)

class ir_remote_read:
    def __init__(self,pin,callback,ac=False, debug = False):
        self._pin = pin
        self._callback = callback
        self._ac = ac
        
        self._current_edge = 0
        self._last_edge = 0
        
        self._bits = 0
        self._parsed_bits = 0
        self._state = 0
        self._delay = 0
        self._message = ""
        self._times = array('i',  (0 for _ in range(70 + 1)))  # +1 for overrun
        self._delays = ""
        self._ir_timer = Timer()
        self._debug = debug
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._aquire) #Pin.IRQ_RISING|Pin.IRQ_FALLING

        
    def _aquire(self,ir):
        
        self._current_edge =  utime.ticks_us()
        self._times[self._bits] = self._current_edge - self._last_edge
        self._bits +=1 
        self._last_edge = self._current_edge
        
        self._ir_timer.init(period=15 , mode=Timer.ONE_SHOT, callback=self._timeout)
        
        #if self._delay > 15000 or self._delay <0 or self._bits >= 32: #Reset to 0 - await IR start
        #    self._bits = 0
             #Pin.IRQ_RISING|Pin.IRQ_FALLING
            #self._read_bits()
            
    def _read_bits(self):
        self._state = 1
        self._message = ""
        self._parsed_bits = 0
        self._delays = ""
        self._bits = 0
        for i in range(len(self._times)):
            self._delays += str(self._times[i]) + ";"
            
            if self._times[i] > 0 and self._times[i] < 1600 :
                #print(" zero ")
                self._message += "0"
                self._parsed_bits += 1
                
                #print("Delay: {} - Message: {}".format(delay,message))
                
            elif  self._times[i] > 0 and self._times[i] < 3000:
                self._message += "1"
                self._parsed_bits += 1
            
            if self._times[i] > 10000 and self._times[i] < 12000 :
                print("Repeat")
                self._callback("","","R")
                #print("Delay: {} - Message: {}".format(delay,message))
            
        #print("Parsed: {} Message:{}".format(self._parsed_bits,self._message))
        #print("Delays: {}".format(self._delays))
#            if self._state == 0 and self._delay > 10000 and self._delay < 12000 :
#                self._callback("","","R")
#                self._bits = 0
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._aquire) #Pin.IRQ_RISING|Pin.IRQ_FALLING
        self._times = array('i',  (0 for _ in range(70 + 1)))  # +1 for overrun
        
    def _timeout(self,t):
        if self._debug:
            print("Timeout")
            print("err parsing")
            print("Parsed: {} Message:{}".format(self._parsed_bits,self._message))
            print("Delays: {}".format(self._delays))
        self._pin.irq(trigger=0)
        self._read_bits()
        try:
            self._callback(int(self._message[0:16],2),int(self._message[16:32],2),"{}_{}".format(int(self._message[0:16],2),int(self._message[16:32],2)))
        except:
            if self._debug:
                print("err parsing")
                print("Parsed: {} Message:{}".format(self._parsed_bits,self._message))
                print("Delays: {}".format(self._delays))
        
