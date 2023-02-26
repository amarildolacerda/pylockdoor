esptool --port %1 --baud 1000000 write_flash  -fm dio --flash_size=detect 0 .pio/build/d1/firmware.bin
