#__author__ = 'beau'
from micropython import const

import time
class PID:
    """
    Discrete PID control
    
    from pid import PID
    
    def read_rps():
        #read function
        global rps,factor
        return rps * factor
        
    def print_output(message):
        #action function
        return
        
        pid = PID(read_rps,print_output,P=-3.0, I=-0.01, D=0.0,debug = False)
    
    
    pid.tune(P=-15.0, I=-0.01, D=0.0)
    
    pid.set_point = i
    pid.update()
    
    """
    debug = False
    def __init__(self,input_fun,output_fun, _P=const(3.), _I=const(0.01), _D=const(0.0),debug = False):
        self.debug = debug
        self._Kp=const(_P)
        self._Ki=const(_I)
        self._Kd=const(_D)

        self.I_value = 0
        self.P_value = 0
        self.D_value = 0

        self.I_max=2000.0
        self.I_min=0

        self.set_point=0.0

        self.prev_value = 0

        self.output = 0

        self.output_fun = output_fun
        self.input_fun = input_fun

        #self.last_update_time = time.ticks_ms()


    def update(self):
        #print("update")
        current_value = self.input_fun()
        self.error = self.set_point - current_value
            #     print ('temp '+str(current_value))
            #    print ('SP'+str(self.set_point))
            
        self.P_value = self._Kp * self.error
        self.D_value = self._Kd * ( current_value-self.prev_value)


            #lapsed_time = time.ticks_ms()-self.last_update_time
            #lapsed_time/=1000. #convert to seconds
            #self.last_update_time = time.ticks_ms()





        self.I_value += self.error * self._Ki

        if self.I_value > self.I_max:
                #self.I_value = self.I_max
            return
        elif self.I_value < self.I_min:
            self.I_value = self.I_min
            return
        else:
            self.output = int((self.P_value + self.I_value - self.D_value)/300)
            
        
        if self.output != 0: 
            self.output_fun(self.output)

            #if self.output<-100:
            #    self.output = -100.0
            #if self.output>100:
            #    self.output = 100.0
            #if self.debug:
            #    print(f"PID Input: {current_value} ; PID SetPoint: {self.set_point}; PID Output: {self.output}")

                #print("Setpoint: "+str(self.set_point))
                #print("P: "+str(self.P_value))
                #print("I: "+str(self.I_value))
                #print("D: " +str(self.D_value))
                #print("Output: "+str(self.output))
                #print ()

            

#            self.last_update_time=time.ticks_ms()
