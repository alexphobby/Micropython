import ntptime,time
UTC_OFFSET = 3 * 60 * 60

print("Get ntp time")
err=True
retry_count = 50
while err and retry_count > 0:
    try:
        ##ntptime.host="ro.pool.ntp.org"
        ntptime.settime()
        print(f"NTP OK, Time: {time.localtime()}")
        err=False
        #return
    except:
        retry_count-=1
        time.sleep(0.6)
        print(f"err ntp, retry count: {retry_count}")

def ro_time():
    return time.localtime(time.time() + UTC_OFFSET)
def ro_time_epoch():
    return time.time() + UTC_OFFSET
