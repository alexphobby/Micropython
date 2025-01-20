class dummy_temp_sensor:
    enabled = False
    def __init__(self,i2c = ""):
        print("no temp sensor, default to dummy")
    def temperature(self):
        return -100
    
    def humidity(self):
        return -100

