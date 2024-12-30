from BOILER import *
cm = ROOM("camera_mica",0)
cm.setRequiredTemperature(21)
cm.temperature = 20
cm.update_temperature(20.5)
cm.update()