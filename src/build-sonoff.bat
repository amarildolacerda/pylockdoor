esptool.py --chip auto --port %1 erase_flash
esptool.py --port %1 --baud 460800 write_flash --flash_size=detect 0  ../bin/esp8266.bin
.\build.bat %1 %2