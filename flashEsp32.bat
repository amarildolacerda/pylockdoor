esptool.py --chip esp32 --port %1 --baud 460800 write_flash -z 0x1000 bin/esp32.bin
upload %1 %2
