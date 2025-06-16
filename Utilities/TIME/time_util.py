from time import localtime
def get_seconds():
    return localtime()[1]*30*24*3600 + localtime()[2]*24*3600 + localtime()[3]*3600 + localtime()[4]*60 + localtime()[5]
def set_seconds():
    global last_motion
    last_motion = localtime()[1]*30*24*3600 + localtime()[2]*24*3600 + localtime()[3]*3600 + localtime()[4]*60 + localtime()[5]