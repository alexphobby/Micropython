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
        elif self.guid == "e6614103e7147f24":
            self.device = "a36_cam_medie"
            self.name = "Dormitor"
        elif self.guid == "e6614103e7739437":
            self.device = "a36_other1"
            self.name = "Other1"
        
        elif self.guid == "e6614103e74f192e":
            self.device = "a36_other2"
            self.name = "Other2"
        
        elif self.guid == "e6614103e71a8e26":
            self.device = "a36_other3"
            self.name = "Other3"
        
        
        elif self.guid == "e6614103e7278226":
            self.device = "a36_other4"
            self.name = "Other4"
        
        elif self.guid == "e6614103e7666824":
            self.device = "a36_other5"
            self.name = "Other5"
        
        elif self.guid == "e6614103e749182e":
            self.device = "a36_other6"
            self.name = "Other6"
        
        elif self.guid == "64e833831c08":
            self.device = "a36_esp32c3_1"
            self.name = "Birou"
        
        elif self.guid == "64e83382cb54":
            self.device = "a36_esp32c3_2"
            self.name = "Dormitor"
        
        
        else:
            print("Machine not defined")
            
            self.device = "not defined"
            self.name = "not defined"
        
        self.topic_receive = f"to/{self.device}"
        self.topic_send = f"from/{self.device}"
            
        print(f"Topics: Receiving:{self.topic_receive}; Sending:{self.topic_send}")

