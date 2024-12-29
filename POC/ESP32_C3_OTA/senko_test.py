#v_local
#from i2c_init import *


#from mqtt_as_init import *
#test()

from CONNECTWIFI import *
wan = CONNECTWIFI()

from MACHINES import *
my_machine = MACHINES()
github_folder=my_machine.github_folder

from senko import Senko
OTA = Senko(user="alexphobby",branch = "main", repo="Micropython", headers =  {'User-Agent': 'alexphobby'}, working_dir=my_machine.github_folder, files=["*"])
updated = OTA.update()

if updated:
    print("Updated to the latest version! Rebooting...")
    machine.reset()
