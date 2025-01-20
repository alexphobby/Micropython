class dummy_light_sensor:
    enabled = False
    def __init__(self,i2c = ""):
        print("no light sensor, default to dummy")

    def light(self):
        return -1