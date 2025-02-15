import machine, neopixel

class NEOPIXEL_UTIL:
    def __init__(self,pin = 21):
        self.np = neopixel.NeoPixel(machine.Pin(pin), 1)
        self.np[0] = (0, 0, 0)
        self.np.write()
        self.led_status = False
    def toggle(self,new_status = None):
        if new_status is None and not self.led_status:
            self.set_value("on")
            self.led_status = True
        elif new_status is None and self.led_status:
            self.set_value("off")
            self.led_status = False
        elif type(self.led_status) == bool:
            self.set_value(new_status)
            self.led_status = new_status
        else:
            print(f"invalid toggle {new_status}")
    
    def on(self):
        self.value(True)

    def off(self):
        self.value(False)

    def value(self,new_value):
        self.set_value(new_value)
        
    def set_value(self,color = "red"):
        if color == "red":
            self.np[0] = (1, 0, 0)
        elif color == "green":
            self.np[0] = (0, 1, 0)
        elif color == "blue":
            self.np[0] = (0, 0, 1)
        elif color == "off" or color == False:
            self.np[0] = (0, 0, 0)
            self.led_status = False
        elif color == "on" or color == True:
            self.np[0] = (1, 1, 1)
            self.led_status = True
        
        else:
            print("else...")
            self.np[0] = color
        self.np.write()
    
    