import network
import espnow
import time
# A WLAN interface must be active to send()/recv()
#sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
#sta.active(True)
#sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer=b'\xec\xda;\xc0: '
#peer = b'\xFF\xFF\xFF\xFF\xFF\xFF'   # MAC address of peer's wifi interface
e.add_peer(peer)      # Must add_peer() before send()

e.send(peer, "Starting...")
i=0
while True:
    i+=1
    e.send(peer, f"Send {str(i)}", True)
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv(
        print("Received: " ,host, msg)

    print(f"sent {i}")
    time.sleep(1)
e.send(peer, b'end')
