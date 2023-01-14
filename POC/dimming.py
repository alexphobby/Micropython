from machine import Pin, ADC
from machine import PWM
from brightness_map import brightness_map

class DIMMING:
    state = 0
    index1 = 0
    index2 = 0
    reqIndex1 = 0
    reqIndex2 = 0
    
    def __init__(self,pin1,pin2,min1,max1,min2,max2,fade_time_ms):
        #self.state = value
        
        self.pin1 = Pin(pin1,Pin.OUT)
        self.pin2 = Pin(pin2,Pin.OUT)

        self.min1 = min1
        self.max1 = max1
        
        self.min2 = min2
        self.max2 = max2
        
        self.fade_time_ms = fade_time_ms


        self.pin1.low()
        self.pin2.low()

        self.pwm_1 = PWM(self.pin1)
        self.pwm_1.freq(1000)
        self.pwm_1.duty_u16(0)
        
        self.pwm_2 = PWM(self.pin2)
        self.pwm_2.freq(1000)
        self.pwm_2.duty_u16(0)
        
        self.timeStep1 = int(self.fade_time_ms / (self.max1 - self.min1))
        self.timeStep2 = int(self.fade_time_ms / (self.max2 - self.min2))
        
        
        self.setPWM()
        
        #print(self.state, self.step1, self.step2)
        print("Init to 0")
        
    def changeStateTo(self, newState):
        self.state = newState
        print(f"newstate = {newState}")
    
    def atSetpoint(self):
        return self.atSetpoint1() and self.atSetpoint2()
         
    def atSetpoint1(self):
        if self.reqIndex1 != self.index1:
            return False
        return True
    
    def atSetpoint2(self):
        if self.reqIndex2 != self.index2:
            return False
        return True
    
    def dimToOff(self):
        self.reqIndex1 = 0
        self.reqIndex2 = 0
        print("require OFF")

    def dimToOn(self):
        self.reqIndex1 = self.max1
        self.reqIndex2 = self.max2
        print("require ON")

    def setDimValueStep(self):
        if self.reqIndex1 < self.min1:
            self.index1 = 0
        if self.reqIndex2 < self.min2:
            self.index2 = 0
        step1 = 0
        step2 = 0
        if not self.atSetpoint1():
            #print("Notsetpoint1")
            if self.index1 < self.reqIndex1:
                step1 = 1
            else:
                step1 = -1
            self.index1 = self.index1 + step1
        
        if not self.atSetpoint2():
            #print("Notsetpoint2")
            if self.index2 < self.reqIndex2:
                step2 = 1
            else:
                step2 = -1
            self.index2 = self.index2 + step2
        
        #print(f"Req: {self.reqIndex1};{self.reqIndex2}")
#        print(f"Step: {step1};{step2}")
        
        self.setPWM()
        
        
    def setPWM(self):
        #print(f"setPWM: {self.index1};{self.index2}")
        self.pwm_1.duty_u16(brightness_map[self.index1])
        self.pwm_2.duty_u16(self.index2)
    
        