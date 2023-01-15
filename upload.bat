echo %2


if "%2"=="ls" goto :fim  

if "%2"=="upload" goto :upload

echo compilando....

mpy-cross src/app.py

mpy-cross src/boot.py

mpy-cross src/command32.py

mpy-cross src/command8266.py

mpy-cross src/commandutils.py

mpy-cross src/config.py

mpy-cross src/configshow.py

mpy-cross src/csConfig.py

mpy-cross src/csGpio.py


mpy-cross src/event.py

mpy-cross src/eventutils.py

mpy-cross src/mqtt.py

mpy-cross src/ntp.py

mpy-cross src/server.py

mpy-cross src/wifimgr.py

mpy-cross src/umqtt_simple.py

mpy-cross src/alexaserver.py

mpy-cross src/broadcast.py


rem ampy  --port %1 ls
rem echo ERRORLEVEL
rem if ERRORLEVEL 1 goto :fim


if "%2"=="" goto :todos  

goto :so


:todos
:upload
cd src
del *.mpy

ampy -d 0.5 --port %1 put boot.py
ampy -d 0.5 --port %1 put command32.mpy	
ampy -d 0.5 --port %1 put commandutils.mpy	
ampy -d 0.5 --port %1 put command8266.mpy
ampy -d 0.5 --port %1 put config.mpy

ampy -d 0.5 --port %1 put configshow.mpy

ampy -d 0.5 --port %1 put csConfig.mpy
ampy -d 0.5 --port %1 put csGpio.mpy

ampy -d 0.5 --port %1 put event.mpy
ampy -d 0.5 --port %1 put eventutils.mpy
ampy -d 0.5 --port %1 put main.py
ampy -d 0.5 --port %1 put app.mpy
ampy -d 0.5 --port %1 put mqtt.mpy	
ampy -d 0.5 --port %1 put ntp.mpy
ampy -d 0.5 --port %1 put server.mpy
ampy -d 0.5 --port %1 put wifimgr.mpy
ampy -d 0.5 --port %1 put umqtt_simple.mpy
ampy -d 0.5 --port %1 put help.tmpl
ampy -d 0.5 --port %1 put commandutils.mpy
ampy -d 0.5 --port %1 put broadcast.mpy
ampy -d 0.5 --port %1 put erro.html
ampy -d 0.5 --port %1 put eventservice.xml
ampy -d 0.5 --port %1 put help.tmpl
ampy -d 0.5 --port %1 put msearch.html
ampy -d 0.5 --port %1 put setup.xml
ampy -d 0.5 --port %1 put state.soap


cd ..
goto :fix

:so
ampy -d 0.5 --port %1 put .\src\%2

:fix

:fim
esptool.py --port %1 --baud 1000000 run  




