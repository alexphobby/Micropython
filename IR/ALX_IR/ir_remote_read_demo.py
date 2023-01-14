import time
from ir_remote_read import ir_remote_read
from machine import Pin

ir_pin = Pin(16)


def ir_callback(remote,command,combo):
    print(combo)
    
ir_remote_read(ir_pin,ir_callback)

while True:
    time.sleep(5)