def pi_pico_ntp():
    result = False
    while result == False:
        try:
            res = urequests.get("http://worldtimeapi.org/api/timezone/Europe/Bucharest")
            result = True
        except:
            print("err requests")
            
    print("-----------")
    #print(res.json()["unixtime"])

    import ujson
    unixtime = int(res.json()["unixtime"])
    UTC_OFFSET = int(res.json()["utc_offset"][2:3])

    adjustedunixtime = int(unixtime + UTC_OFFSET*60*60)
    #print(f"Got time: {res.json()["unixtime"]}")
    tm = time.localtime(adjustedunixtime)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    print(unixtime)
    print(adjustedunixtime)
    print(time.localtime())
    print(f"Time is: {time.localtime()[3]}:{time.localtime()[4]}")
    print("-----------")
