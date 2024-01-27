import time
from machine import Pin
from ir_remote_read import ir_remote_read
from my_remotes import *
ir_pin = Pin(1,Pin.IN,Pin.PULL_UP)


def ir_callback(remote,command,combo):
    print((remote,command))
    try:
        print(remote_samsung[combo])
        return
    except:
        pass
    
    try:
        print(remote_tiny[combo])
    except:
        pass
    #print((remote,command))
    
    
ir_remote_read(ir_pin,ir_callback)

while True:
    time.sleep(5)