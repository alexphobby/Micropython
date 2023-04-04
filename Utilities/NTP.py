import ntptime,time
UTC_OFFSET = 3 * 60 * 60

print("Get ntp time")
err=True
retry_count = 30
while err and retry_count > 0:
    try:
        ##ntptime.host="ro.pool.ntp.org"
        ntptime.settime()
        
        print(f"NTP OK, Time: {time.localtime()}")
        err=False
        #return
    except:
        retry_count-=1
        time.sleep(0.5)
        print(f"err ntp, retry count: {retry_count}")

def ro_time():
    return time.localtime(time.time() + UTC_OFFSET)