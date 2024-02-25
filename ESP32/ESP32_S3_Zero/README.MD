
v1.23.0 Preview

micropython\ports\esp32\boards\ESP32_GENERIC_S3\sdkconfig.board
CONFIG_ESPTOOLPY_FLASHMODE_QIO=y
CONFIG_ESPTOOLPY_FLASHFREQ_80M=y
CONFIG_ESPTOOLPY_AFTER_NORESET=y

CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y
CONFIG_ESPTOOLPY_FLASHSIZE_8MB=
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=
CONFIG_PARTITION_TABLE_CUSTOM=y
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions-4MiB.csv"


docker run -ti --rm -v "D:\Diverse\micropython":/micropython -w /micropython espressif/idf:v5.0.4 bash  -c "export MICROPY_PY_BTREE=0 && make -C mpy-cross && make -C ports/esp32 submodules all BOARD=ESP32_GENERIC_S3  -j4"



Burn firmware.bin, not micropython.bin!

"C:\Program Files (x86)\Thonny\python.exe" -u -m esptool --port COM34 --chip esp32s3 --baud 115200 write_flash --erase-all -z 0 D:\Diverse\micropython\ports\esp32\build-ESP32_GENERIC_S3\firmware.bin

