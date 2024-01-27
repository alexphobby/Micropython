from bmp280 import *
bme280 = BME280(i2c=i2c)
bme280.read_compensated_data()
print(bme280.values)
