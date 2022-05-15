#esptool.py --chip auto  --baud 460800 write_flash -z 0x0000 bin/esp8266.bin
esptool.py --port %1 --baud 1000000 write_flash --flash_size=4MB -fm dio 0 bin/esp8266.bin

./upload.sh %1 %2
