
echo compilando....
python3 -m mpy_cross ./src/app.py
python3 -m mpy_cross ./src/boot.py
python3 -m mpy_cross ./src/command32.py
python3 -m mpy_cross ./src/command8266.py
python3 -m mpy_cross ./src/commandutils.py
python3 -m mpy_cross ./src/config.py
python3 -m mpy_cross ./src/configshow.py
python3 -m mpy_cross ./src/csConfig.py
python3 -m mpy_cross ./src/csGpio.py
python3 -m mpy_cross ./src/csHelp.py
python3 -m mpy_cross ./src/configutils.py
python3 -m mpy_cross ./src/event.py
python3 -m mpy_cross ./src/eventutils.py
python3 -m mpy_cross ./src/mqtt.py
python3 -m mpy_cross ./src/ntp.py
python3 -m mpy_cross ./src/server.py
python3 -m mpy_cross ./src/wifimgr.py
python3 -m mpy_cross ./src/umqtt_simple.py

echo flashing....
esptool.py --chip auto --after no_reset_stub  --baud 460800 write_flash -z 0x0000 ./bin/esp8266.bin 

echo sending src ...
echo boot.py
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/boot.py
echo command32
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/command32.mpy	
echo commandutils
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/commandutils.mpy	
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/command8266.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/config.mpy

ampy -d 0.5 --port /dev/ttyUSB1 put ./src/configshow.mpy

ampy -d 0.5 --port /dev/ttyUSB1 put ./src/csConfig.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/csGpio.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/csHelp.mpy

ampy -d 0.5 --port /dev/ttyUSB1 put ./src/configutils.mpy	
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/event.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/eventutils.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/main.py
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/app.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/mqtt.mpy	
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/ntp.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/server.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/wifimgr.mpy
ampy -d 0.5 --port /dev/ttyUSB1 put ./src/umqtt_simple.mpy

