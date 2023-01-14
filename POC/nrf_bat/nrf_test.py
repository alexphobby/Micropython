# Generic Tests for radio-fast module.
# Modify config.py to provide master_config and slave_config for your hardware.
import machine, radiofast
import time
from config import master_config, slave_config, FromMaster, ToMaster

def test_master():
    m = radiofast.Master(master_config)
    send_msg = FromMaster()
    while True:
        result = m.exchange(send_msg)
        if result is not None:
            print(result.i0)
        else:
            print('M Timeout')
        send_msg.i0 += 1
        time.sleep_ms(1000)

def test_slave():
    s = radiofast.Slave(slave_config)
    send_msg = ToMaster()
    while True:
        result = s.exchange(send_msg)       # Wait for master
        if result is not None:
            print(result.i0)
        else:
            print('S Timeout')
        send_msg.i0 += 1

test_slave()
#test_master()




