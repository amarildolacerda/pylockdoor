del *.mpy

esptool.py --port %1 --baud 1000000 write_flash  -fm dio --flash_size=detect 0 ../bin/esp8266.bin

echo Compilar
..\mpy-cross config.py

..\mpy-cross wifimgr.py
..\mpy-cross app.py
..\mpy-cross ntp.py
..\mpy-cross server.py
..\mpy-cross broadcast.py
..\mpy-cross commands.py
..\mpy-cross mqtt.py
..\mpy-cross umqtt_simple.py
..\mpy-cross event.py
..\mpy-cross commandutils.py




if "%2"=="" goto :todos
ampy -d 0.5 --port %1 put %2
goto :fix


:todos
ampy -d 0.5 --port %1 put boot.py
ampy -d 0.5 --port %1 put main.py
ampy -d 0.5 --port %1 put app.mpy
ampy -d 0.5 --port %1 put config.mpy
ampy -d 0.5 --port %1 put wifimgr.mpy
ampy -d 0.5 --port %1 put ntp.mpy
ampy -d 0.5 --port %1 put server.mpy
ampy -d 0.5 --port %1 put broadcast.mpy

ampy -d 0.5 --port %1 put erro.html
ampy -d 0.5 --port %1 put state.soap
ampy -d 0.5 --port %1 put eventservice.xml
ampy -d 0.5 --port %1 put msearch.html
ampy -d 0.5 --port %1 put setup.xml

ampy -d 0.5 --port %1 put commands.mpy
ampy -d 0.5 --port %1 put mqtt.mpy
ampy -d 0.5 --port %1 put umqtt_simple.mpy
ampy -d 0.5 --port %1 put event.mpy
ampy -d 0.5 --port %1 put commandutils.mpy



:fix

:fim


esptool.py --port %1 --baud 1000000 run  

