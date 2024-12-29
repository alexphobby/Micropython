#from i2c_init import *


#from mqtt_as_init import *
#test()
from CONNECTWIFI import *
wan = CONNECTWIFI()
from MACHINES import MACHINES
my_machine = MACHINES()
from senko import Senko
OTA = Senko(user="alexphobby",branch = "main", repo="Micropython", headers =  {'User-Agent': 'alexphobby'}, working_dir=my_machine.github_folder, files=["*"])
OTA.update()

if OTA.update():
    print("Updated to the latest version! Rebooting...")
    machine.reset()
