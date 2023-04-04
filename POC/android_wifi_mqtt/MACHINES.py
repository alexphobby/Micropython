import ubinascii
import machine

class MACHINES:
    
    def __init__(self):
        """ MQTT guid"""
        self.guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
        
        if self.guid == "e6614103e763b337":
            self.device = "a36_cam_mica"
            
        elif self.guid == "e6614103e7739437":
            self.device = "a36_cam_medie"
            
        else:
            print("Machine not defined")
            
        self.topic_receive = f"to_{self.device}"
        self.topic_send = f"from_{self.device}"
            
        print(f"Topics: Receiving:{self.topic_receive}; Sending:{self.topic_send}")

