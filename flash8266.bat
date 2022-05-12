rem esptool.py --chip auto --port %1 --baud 460800 write_flash -z 0x0000 bin/esp8266.bin
esptool.py --port %1 --baud 1000000 write_flash --flash_size=4MB -fm dio 0 bin/esp8266.bin
upload %1 %2
