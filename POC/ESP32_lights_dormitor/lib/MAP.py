class MAP:
    in_min = 0
    in_max = 0
    out_min = 0
    out_max = 0
    slope = 0
    def __init__(self, in_min, in_max,out_min,out_max):
        if out_max == 0 or out_min == 0 or in_max == 0:
            print("out_min, out_max and in_max should be different to 0")
        self.in_min = in_min
        self.in_max = in_max
        self.out_min = out_min
        self.out_max = out_max
        self.slope = (out_max - out_min) / (in_max - in_min)
    
    def map_value(self,input):
        if abs(input) > abs(self.in_max):
            return self.out_max
        elif abs(input) < abs(self.in_min):
            return self.out_min
        #output = self.in_max * self.out_min/self.out_max
        #print(f"{self.out_min} + {self.slope} * ({input} - {self.in_min})")
        
        output = self.out_min + self.slope * (input - self.in_min)
        #print(output)
        return output
        