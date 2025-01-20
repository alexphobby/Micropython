# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#import dormitor_light
import time
time.sleep(2)
try:
    print("import test_bleradio_1")
    import test_bleradio_1
    print("import test_bleradio_1")
except Exception as ex:
    print(f"import test_bleradio_1 failed: {ex}")
try:
    import test_bleradio_2
    print("import test_bleradio_2")
except Exception as ex:
    print(f"import test_bleradio_2 failed: {ex}")

