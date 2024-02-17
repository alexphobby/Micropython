import ubinascii
import machine

class MACHINES:
    github_folder = ""
    devicetype = ""
    features = []
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
            self.devicetype = "lights"
            self.features = ["thermometer","humidity","ambientlight"]
            
        elif self.guid == "e6614103e7739437":
            self.device = "a36_other1"
            self.name = "Other1"
        
        elif self.guid == "e6614103e74f192e":
            self.device = "a36_Birou"
            self.name = "Birou"
            self.devicetype = "lights"
            self.features = ["thermometer","humidity","ambientlight"]

        
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
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity","count"]
            
        
        elif self.guid == "64e83382cb54":
            self.device = "a36_esp32c3_2"
            self.name = "Dormitor"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity","ambientlight","count"]
        
        elif self.guid == "ecda3bc03ae0":
            self.device = "a36_esp32c3_3"
            self.name = "Dormitor_2"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity","ambientlight","count"]
            
        elif self.guid == "c04e30813a64":
            self.device = "a36_esp32c3_4"
            self.name = "Birou"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity","ambientlight","count"]
            
        elif self.guid == "c04e30814b98":
            self.device = "a36_esp32c3_5"
            self.name = "Box_1"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity"]


        elif self.guid == "8065996ad23c":
            self.device = "a36_esp32c3_6"
            self.name = "Box_2"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity"]

        elif self.guid == "c04e30814160":
            self.device = "a36_esp32c3_7"
            self.name = "Box_3"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
            self.devicetype = "thermometer"
            self.features = ["thermometer","display","humidity"]

        elif self.guid == "3030f9baa92c":
            self.device = "a36_birou"
            self.name = "Birou"
            self.devicetype = "lights"
            self.features = ["thermometer","humidity","ambientlight"]



        else:
            print(f"Machine {self.guid} not defined")
            
            self.device = "not defined"
            self.name = "not defined"
            self.github_folder = "POC/ESP32_WIFI_MQTT_WEATHER_SSD1306"
        
        self.topic_receive = f"to/{self.device}"
        self.topic_send = f"from/{self.device}"
        
        print(f"Machine Name: {self.name}")
        print(f"Machine Topics: Receiving:{self.topic_receive}; Sending:{self.topic_send}")
        print(f"Machine Features: {self.features}")
