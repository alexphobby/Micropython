import machine, neopixel
np = neopixel.NeoPixel(machine.Pin(21), 1)
np[0] = (0, 0, 0)
np.write()

def led(color = "red"):
    if color == "red":
        np[0] = (30, 0, 0)
    elif color == "green":
        np[0] = (0, 30, 0)
    elif color == "blue":
        np[0] = (0, 0, 30)
    elif color == "off":
        np[0] = (0, 0, 0)
    elif color == "on":
        np[0] = (30, 30, 30)
    else:
        np[0] = color
    np.write()
    
    