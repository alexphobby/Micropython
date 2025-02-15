import utime
from machine import Pin
from array import array
from machine import Timer
import asyncio
import my_remotes
#from utime import ticks_us
#from array import array
#machine.freq(250000000)
#import time
from sys import platform

#def ir_callback(remote,command,combo,ac=True):
#    pass
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
        self._times = array('i',  (0 for _ in range(200 + 1)))  # +1 for overrun
        self._delays = ""
        
        if (platform == "esp32"):
            pass
            #self._ir_timer = Timer(0)
        elif platform == "rp2":
            pass
            #self._ir_timer = Timer()
        else:
            print("unknown")
            
        self._debug = debug
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._aquire) #Pin.IRQ_RISING|Pin.IRQ_FALLING
        self.timeout = 20000
        #self.last_edge = 0
    async def process(self,queue):
        print("IR listen")
        while True:
            await asyncio.sleep(1)
            if self._debug:
                print("process loop")
            if utime.ticks_us() - self._last_edge > self.timeout and self._bits > 30:
                _valid = False
                _val = 0
                _addr=0
                _cmd=0
                for i in range(0,len(self._times)): #,2):
                    if self._times[i] == 0:
                        print("break")
                        break
                    #print(f'{self._times[i]}')
                    #if self._times[i] < self.timeout and i !=0 :
                    #print(f'{self._times[i]} - {self._times[i-1]}')
                    #if 20000 < self._times[i] < 60000:
                    #    print('R')
                    if 4000 < self._times[i] < 20000:
                        _valid =True
                        _count = 0
                        #print("Start")
                        continue
                    if _valid and self._times[i] > 20000:
                        #print("end")
                        break
                    _val >>= 1
                    
                    #print(f'{self._times[i]} - {self._times[i-1]}')
                    #if _valid and 300 < self._times[i] < 1000 and 300 < self._times[i-1] < 1000:
                    if _valid and 800 < self._times[i] < 1600:
                        #print("0")
                        continue
                    if _valid and 1600 < self._times[i] < 3000:
                        _val |= 0x80000000
                        #print("1")
                        continue
                #print(_val)
                #print(bin(_val))
                _addr = _val & 0xFF
                _cmd = (_val >> 16) & 0xFF
                if self._debug:
                    print(f'addr: {_addr} - cmd:{_cmd} - bits: {self._bits}')
                self._bits = 0
                self._times = array('i',  (0 for _ in range(200 + 1)))
                if self._bits%4 != 0:
                    await asyncio.sleep(0.3)
                    continue
                for remote in dir(my_remotes):
                    if remote.startswith("__"):
                        continue
                    try:
                        _remote = eval(f'my_remotes.{remote}')
                        _button = _remote['_'.join((str(_addr),str(_cmd)))]
                        await queue.aput(_button)
                        print(f'Ir read {_button}')
                        self._callback(_button)
                        break
                    except Exception as ex:
                        #print(f'Err: {ex}')
                        pass
            

    def _aquire(self,ir):
        self._current_edge =  utime.ticks_us()
        self._times[self._bits] = self._current_edge - self._last_edge
        self._bits +=1 
        self._last_edge = self._current_edge
            
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
                asyncio.run(self._callback("","","R"))
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
            asyncio.run(self._callback(int(self._message[0:16],2),int(self._message[16:32],2),"{}_{}".format(int(self._message[0:16],2),int(self._message[16:32],2))) )
        except:
            if self._debug:
                print("err parsing")
                print("Parsed: {} Message:{}".format(self._parsed_bits,self._message))
                print("Delays: {}".format(self._delays))
        
