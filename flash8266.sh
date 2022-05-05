esptool.py --chip auto  --baud 460800 write_flash -z 0x0000 bin/esp8266.bin

./upload.sh %1 %2
