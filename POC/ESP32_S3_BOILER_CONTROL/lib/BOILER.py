from Servo import Servo
from time import sleep
class ROOM:
    temperature = -100.0
    required_temperature = -100.0
    threshold = 0.2
    changed = False
    def __init__(self,name,servo_pin,servo_range=(30,90)):
        self.name = name
        self.servo_pin = servo_pin
        self.servo_range = servo_range
        self.servo = Servo(self.servo_pin,min_deg=self.servo_range[0],max_deg=self.servo_range[1])
    
    def setRequiredTemperature(self,temperature):
        self.required_temperature = temperature
        print(f"Required temperature for {self.name}: {self.required_temperature}")
    
    def update_temperature(self, new_temperature):
        if new_temperature != self.temperature:
            self.changed = True
            self.temperature = new_temperature
    
    def update(self):
        if not self.changed:
            print("not changed")
            return
        if self.temperature < self.required_temperature - self.threshold:
            print(f"{self.name}: on")
            self.servo.write(self.servo_range[1])
            sleep(3)
            self.servo.off()

        elif self.temperature > self.required_temperature + self.threshold:
            print(f"{self.name}: off")
            self.servo.write(self.servo_range[0])
            sleep(3)
            self.servo.off()
        else:
            print("idle")
            self.servo.write(int((self.servo_range[0] + self.servo_range[1])/3))
    
    def __eq__(self,other):
        if other is None or type(other) is not type(self):
            return False 
        return self.name == other.name and self.servo_pin == other.servo_pin
    
    def __hash__(self):
        return hash(f'{self.name}_{self.servo_pin}')
    def __repr__(self):
        return f'{self.name}_{self.servo_pin}'
    
class BOILER:
    def __init__(self, boiler_pin):
        self.rooms = set()
        self.rooms.add(ROOM("camera_mica",0))
        self.rooms.add(ROOM("dormitor",1))
        
        self.boiler_pin = boiler_pin
        
    def check_rooms(self):
        for room in self.rooms:
            print(f'Room: {room.name} T: {room.temperature} Req T: {room.required_temperature}')
            room.update()
        
    