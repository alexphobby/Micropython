import time
from machine import Pin,freq
from ir_remote_read import ir_remote_read
from my_remotes import *
ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)


def ir_callback(remote,command,combo):
    err = True
    #print((remote,command))
    try:
        print(remote_samsung[combo])
        err = False
        return
    except:
        pass
    
    try:
        print(remote_tiny[combo])
        err = False
    except:
        pass
    
    if err:
        print(f"Not mapped: {(remote,command)}")
    
    
ir_remote_read(ir_pin,ir_callback)

#while True:
#    time.sleep(5)