
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
python3 -m mpy_cross ./src/configutils.py
python3 -m mpy_cross ./src/event.py
python3 -m mpy_cross ./src/eventutils.py
python3 -m mpy_cross ./src/mqtt.py
python3 -m mpy_cross ./src/ntp.py
python3 -m mpy_cross ./src/server.py
python3 -m mpy_cross ./src/wifimgr.py
python3 -m mpy_cross ./src/umqtt_simple.py

echo flashing....
esptool.py --chip auto erase_flash
esptool.py  --baud 1000000 write_flash --flash_size=4MB -fm dio 0 bin/esp8266.bin

echo sending src ...
echo boot.py

cd src

ampy -d 0.5 --port /dev/ttyUSB0 put boot.py
echo .
ampy  --port /dev/ttyUSB0 put command32.mpy	
echo .
ampy  --port /dev/ttyUSB0 put commandutils.mpy	
echo .
ampy  --port /dev/ttyUSB0 put command8266.mpy
echo .
ampy  --port /dev/ttyUSB0 put config.mpy
echo .

ampy  --port /dev/ttyUSB0 put configshow.mpy
echo .

ampy  --port /dev/ttyUSB0 put csConfig.mpy
echo .
ampy  --port /dev/ttyUSB0 put csGpio.mpy
echo .

ampy  --port /dev/ttyUSB0 put configutils.mpy	
echo .
ampy  --port /dev/ttyUSB0 put event.mpy
echo .
ampy  --port /dev/ttyUSB0 put eventutils.mpy
echo .
ampy  --port /dev/ttyUSB0 put main.py
echo .
ampy  --port /dev/ttyUSB0 put app.mpy
echo .
ampy  --port /dev/ttyUSB0 put mqtt.mpy	
echo .
ampy  --port /dev/ttyUSB0 put ntp.mpy
echo .
ampy  --port /dev/ttyUSB0 put server.mpy
echo .
ampy  --port /dev/ttyUSB0 put wifimgr.mpy
echo .
ampy  --port /dev/ttyUSB0 put umqtt_simple.mpy
echo .
ampy  --port /dev/ttyUSB0 put help.tmpl
echo .
ampy  --port /dev/ttyUSB0 put commandutils.mpy
echo .
ampy  --port /dev/ttyUSB0 put wssid.html
echo .
ampy --port /dev/ttyUSB0 put wfalhou.html
echo .
cd ..

echo  fim

