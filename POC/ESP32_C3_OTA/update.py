#from i2c_init import *
#from mqtt_as_init import *
#test()
print("Update from GitHub. Usage: update()")
def update():
    import MACHINES
    my_machine = MACHINES.MACHINES()
    import gc
    import machine
    
    import CONNECTWIFI
    wifi = CONNECTWIFI.CONNECTWIFI()
    
    from senko import Senko
    gc.collect()
    OTA = Senko(user="alexphobby",branch = "main", repo="Micropython", working_dir=my_machine.github_folder, files=["*"])
    result = OTA.update()
    if result:
        print("Updated to the latest version! Rebooting...")
        machine.reset()
