import os


os.system("esptool.py --port /dev/cu.usbserial-AK0730II write_flash -fs 1MB -fm dout 0x0 .pioenvs/sonoff/firmware.bin")
