import ubinascii
import machine

class MACHINES:
    
    def __init__(self):
        """ MQTT guid"""
        self.guid = str(ubinascii.hexlify(machine.unique_id()),"UTF-8")
        
        if self.guid == "e6614103e763b337":
            self.device = "a_baie"
            self.name = "Baie"
        elif self.guid == "e6614103e763b33x":
            self.device = "a36_cam_mica"
            self.name = "Camera Mica"
        elif self.guid == "e6614103e7739437":
            self.device = "a36_cam_medie"
            self.name = "Dormitor"
            
        else:
            print("Machine not defined")
            
        self.topic_receive = f"to/{self.device}"
        self.topic_send = f"from/{self.device}"
            
        print(f"Topics: Receiving:{self.topic_receive}; Sending:{self.topic_send}")

