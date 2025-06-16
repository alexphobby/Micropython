import json
class CONFIG:
    config = {}
    def __init__(self,config_file="config.cfg",debug=False):
        print(f"Config file: {config_file}")
        self.debug=debug
        self.config_file = config_file
        self.read_file()
        
    def write(self,prop,value):
        try:
            self.config[prop] = value
            self.write_config()
            if self.debug:
                print(f'{self.config_file}\n{self.config}')
        except Exception as ex:
            print(ex)   
    
    def read(self,prop):
        return self.config[prop]

    def read_all(self):
        return self.config

    def read_file(self):
        try:
            f = open(self.config_file, 'r')
        except Exception as ex:
            print(ex)
            return
        
        try:
            self.config = json.loads(f.read())
        except Exception as ex:
            print(ex)
        
        f.close()
    
    def write_config(self):
        f = open(self.config_file, 'w')
        f.write(json.dumps(self.config))
        f.close()
            