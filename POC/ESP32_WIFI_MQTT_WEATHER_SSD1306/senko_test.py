#from i2c_init import *
#from mqtt_as_init import *
#test()
from CONNECTWIFI import *
wifi = CONNECTWIFI()
from MACHINES import *
my_machine = MACHINES()

from senko import Senko
OTA = Senko(user="alexphobby",branch = "main", repo="Micropython", working_dir=my_machine.github_folder, files=["*"])
OTA.update()

if OTA.update():
    print("Updated to the latest version! Rebooting...")
    machine.reset()