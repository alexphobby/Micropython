__author__ = 'beau'
import time
class PID:
    """
    Discrete PID control
    """
    debug = False
    def __init__(self,input_fun,output_fun, P=3., I=0.01, D=0.0,debug = False):
        self.debug = debug
        self.Kp=P
        self.Ki=I
        self.Kd=D

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

        self.last_update_time = time.ticks_ms()


    def update(self):

        if time.ticks_ms()-self.last_update_time > 50:
            """
            Calculate PID output value for given reference input and feedback
            """
            current_value = self.input_fun()
            self.error = self.set_point - current_value
            #     print ('temp '+str(current_value))
            #    print ('SP'+str(self.set_point))
            
            self.P_value = self.Kp * self.error
            self.D_value = self.Kd * ( current_value-self.prev_value)


            lapsed_time = time.ticks_ms()-self.last_update_time
            lapsed_time/=1000. #convert to seconds
            self.last_update_time = time.ticks_ms()





            self.I_value += self.error * self.Ki

            if self.I_value > self.I_max:
                self.I_value = self.I_max
            elif self.I_value < self.I_min:
                self.I_value = self.I_min

            self.output = int((self.P_value + self.I_value - self.D_value)/20)

            #if self.output<-100:
            #    self.output = -100.0
            #if self.output>100:
            #    self.output = 100.0
            if self.debug:
                print("PID Input: {} ; PID SetPoint: {}; PID Error: {}".format(current_value,self.set_point,self.error))

                #print("Setpoint: "+str(self.set_point))
                print("P: "+str(self.P_value))
                print("I: "+str(self.I_value))
                print("D: " +str(self.D_value))
                print("Output: "+str(self.output))
                #print ()

            self.output_fun(self.output)

            self.last_update_time=time.ticks_ms()
