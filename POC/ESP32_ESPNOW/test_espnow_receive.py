import network
import espnow
import time
# A WLAN interface must be active to send()/recv()
#sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
#sta.active(True)
#sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\x80e\x99j\xd2<'   # MAC address of peer's wifi interface
e.add_peer(peer)      # Must add_peer() before send()

#e.send(peer, "Starting...")
i=0
while True:
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        e.send(peer, "R")
        print(host, msg)
        if msg == b'end':
            break
    
    time.sleep(1)

