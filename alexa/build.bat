del *.mpy

esptool.py --port %1 --baud 1000000 write_flash  -fm dio --flash_size=detect 0 ../bin/esp8266.bin

echo Compilar
..\mpy-cross config.py

..\mpy-cross udp.py
..\mpy-cross wifimgr.py
..\mpy-cross app.py
..\mpy-cross ntp.py
..\mpy-cross server.py


if "%2"=="" goto :todos
ampy -d 1 --port %1 put %2
goto :fim


:todos
ampy -d 1 --port %1 put boot.py
ampy -d 1 --port %1 put main.py
ampy -d 1 --port %1 put app.mpy
ampy -d 1 --port %1 put config.mpy
ampy -d 1 --port %1 put wifimgr.mpy
ampy -d 1 --port %1 put ntp.mpy
ampy -d 1 --port %1 put server.mpy

:fim

esptool.py --port %1 --baud 1000000 run  
