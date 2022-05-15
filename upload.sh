
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
#esptool.py --chip auto --after no_reset_stub  --baud 460800 write_flash -z 0x0000 ./bin/esp8266.bin 
esptool.py  --baud 1000000 write_flash --flash_size=4MB -fm dio 0 bin/esp8266.bin

echo sending src ...
echo boot.py
ampy -d 0.5 --port /dev/ttyUSB0 --baud 115200 put ./src/boot.py
echo command32
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/command32.mpy	
echo commandutils
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/commandutils.mpy	
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/command8266.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/config.mpy
echo .

ampy -d 0.5 --port /dev/ttyUSB0 put ./src/configshow.mpy
echo .

ampy -d 0.5 --port /dev/ttyUSB0 put ./src/csConfig.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/csGpio.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/csHelp.mpy
echo .

ampy -d 0.5 --port /dev/ttyUSB0 put ./src/configutils.mpy	
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/event.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/eventutils.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/main.py
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/app.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/mqtt.mpy	
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/ntp.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/server.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/wifimgr.mpy
echo .
ampy -d 0.5 --port /dev/ttyUSB0 put ./src/umqtt_simple.mpy
echo  fim

