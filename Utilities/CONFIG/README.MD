from CONFIG import CONFIG
config=CONFIG(config_file="config.cfg",debug=True) #default to config.cfg
c.read("channel")
c.write("channel",2)
c.read_all()