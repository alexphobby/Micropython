from machine import Pin, ADC,Timer
from machine import PWM
from brightness_map_1024 import brightness_map_1024 as brightness_map
from time import sleep
import asyncio
class Dim:
    step=1
    state = 0
    index1 = 0
    index2 = 0
    reqIndex1 = 0
    reqIndex2 = 0
    max_index = 0
    ch1Enabled = False
    ch2Enabled = False
    #timer1 = Timer()
    def __init__(self,pin1,pin2=None,min1=0,max1=1023,min2=0,max2=1023,fade_time_ms=12000,debug = False):
        #self.state = value
        self.max_index = len(brightness_map)
        self.pin1 = Pin(pin1,Pin.OUT)
        self.pwm_1 = PWM(self.pin1)
        self.pwm_1.deinit()
        self.pwm_1.init()
        self.pwm_1.freq(300)
        self.pwm_1.duty_u16(0)
        if pin2 is not None:
            self.pin2 = Pin(pin2,Pin.OUT)
            
            self.pwm_2 = PWM(self.pin2)
            self.pwm_2.freq(1000)
            self.pwm_2.duty_u16(0)


        self.min1 = min1
        self.max1 = max1
        
        self.min2 = min2
        self.max2 = max2
        
        self.fade_time_ms = fade_time_ms


        #self.pin1.low()
        #self.pin2.low()

                
        
        self.timeStep1 = max(1,int(self.fade_time_ms / (self.max1 - self.min1)))
        self.timeStep2 = max(1,int(self.fade_time_ms / (self.max2 - self.min2)))
        #print(f"Timestep1={self.timeStep1}")
        self.debug = debug
        #self.setPWM()
        
        #print(self.state, self.step1, self.step2)
        #print("Init to 0")
    
    async def dimToPercent(self,reqPercent1):
        await self.dimToIndex(round(reqPercent1 * self.max1 /100))

    async def dimToIndex(self,index):
        self.reqIndex1 = index
        #print(f'setReqas: {self.reqIndex1}, index1={self.index1}, req_percent: {reqPercent1}')
        self.ch1Enabled = True
        
        
        if self.reqIndex1 == 0:
            print(f"Channel 1 off")
            self.reqIndex1 = 0
            #return
        
        elif self.reqIndex1 < self.min1:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex1 = 0
            #return
        
        elif self.reqIndex1 > self.max1:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex1 = self.max1
            #return
        
        #print(f"Setting req index 1 to {reqIndex1}")
        #self.reqIndex1 = reqIndex1
        #self.dimToSetpoint()
        #while self.reqIndex1 != self.index1:
        while True:
            _ecart = self.reqIndex1 - self.index1
            #print(f'self.reqIndex1 != self.index1 Adj: req: {self.reqIndex1} , set: {self.index1}')
            if abs(_ecart) > 50 and self.index1 < 1023-10:
                self.index1 += int(10* _ecart / abs(_ecart))
                #print(f'd100 {self.index1}')
                self.pwm_1.duty_u16(brightness_map[self.index1])
                await asyncio.sleep(0.01)
            elif abs(_ecart) > 10 :
                self.index1 += int(5* _ecart / abs(_ecart))
                #print("d30")
                self.pwm_1.duty_u16(brightness_map[self.index1])
                await asyncio.sleep(0.03)
            elif abs(_ecart) > 5 :
                self.index1 += int(_ecart / abs(_ecart))
                #print("d30")
                self.pwm_1.duty_u16(brightness_map[self.index1])
                await asyncio.sleep(0.02)

            elif abs(_ecart) > 0 :
                #print(f'd1, index: {self.index1} - ecart: {_ecart}')
                self.index1 += int(_ecart / abs(_ecart))
                self.pwm_1.duty_u16(brightness_map[self.index1])
                await asyncio.sleep(0.03)
            
            else:
                print("Setpoint")
                return
            
            #print(self.index1)
            #await asyncio.sleep(0.05)

    def setReqIndex1(self,reqIndex1):
        self.ch1Enabled = True
        
        if reqIndex1 == 0:
            print(f"Channel 1 off")
            self.reqIndex1 = 0
            #return
        
        elif reqIndex1 < self.min1:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex1 = 0
            #return
        
        elif reqIndex1 > self.max1:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex1 = self.max1
            #return
        
        #print(f"Setting req index 1 to {reqIndex1}")
        self.reqIndex1 = reqIndex1
        self.dimToSetpoint()
        
    def setReqIndex2(self,reqIndex2):
        self.ch2Enabled = True
        if reqIndex2 > self.max2:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex2 = self.max2
            return
        
        if reqIndex2 < self.min2:
            print(f"Channel 1 outside working range required: {self.reqIndex1} between {self.min1} and {self.max1}")
            self.reqIndex2 = 0
            return
        
        self.reqIndex2 = reqIndex2
    
            
    def atSetpoint(self):
        return self.atSetpoint1() and self.atSetpoint2()
         
    def atSetpoint1(self):
        return self.reqIndex1 == self.index1
    
    def atSetpoint2(self):
        return self.reqIndex2 == self.index2
    
    def dimToOn(self):
        #print("require ON")
        self.setReqIndex1(self.max1)
        self.setReqIndex2(self.max2)
        self.dimToSetpoint()
    
    def dimToOff(self):
        #print("require OFF")
        self.setReqIndex1(0)
        self.setReqIndex2(0)
        self.dimToSetpoint()
    

    def dimToSetpoint(self):
        pass
        #ecart1 = self.reqIndex1 - self.index1
        #ecart2 = self.reqIndex1 - self.index1
        #print(f"Init Timer, period(ms) = {self.timeStep1}")
        #self.timer1.init(period = min(self.timeStep1,self.timeStep1),mode=Timer.PERIODIC, callback=self.dimStep)
    
        
    def dimStep(self,timer):
        #print("Dimstep")
        if self.reqIndex1 < self.min1:
            self.index1 = 0
            self.reqIndex1=0
            print("Default ch1 to 0")
        if self.reqIndex2 < self.min2:
            self.index2 = 0
            self.reqIndex2 = 0
            print("Default ch2 to 0")
        
        if self.atSetpoint():
            try:
                print("timer disable")
                #timer.deinit()
            except:
                print("timer err")
            
        step1 = 0
        step2 = 0
        if not self.atSetpoint1():
            
            if self.index1 < self.reqIndex1:
                step1 = self.step
            else:
                step1 = -self.step
            #print(f"Notsetpoint1, req: {self.reqIndex1}; current:{self.index1}")
            self.index1 = self.index1 + step1
            #print(f"Notsetpoint1, req: {self.reqIndex1}; current:{self.index1}")
        
        if not self.atSetpoint2():
            #print("Notsetpoint2")
            if self.index2 < self.reqIndex2:
                step2 = self.step
            else:
                step2 = -self.step
            self.index2 = self.index2 + step2
        
        #print(f"Req: {self.reqIndex1};{self.reqIndex2}")
#        print(f"Step: {step1};{step2}")
        
        self.setPWM()
        
        
    def setPWM(self):
        if self.debug:
            print(f"setPWM: {self.index1};{self.index2}")
        
        try:
            if self.ch1Enabled:
                self.pwm_1.duty_u16(brightness_map[self.index1])
            if self.ch2Enabled:
                self.pwm_2.duty_u16(brightness_map[self.index2])
        
        except:
            print(f"Error dimming to level: {self.index1} or {self.index2}")
    #def __doc__(self):
        
    def getPercent(self):
        #print(f'percent: {int(self.index1*100/self.max1)}, index1: {self.index1}')
        return round(self.index1*100/self.max1)