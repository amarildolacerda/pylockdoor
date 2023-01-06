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

mpy-cross src/configutils.py

mpy-cross src/event.py

mpy-cross src/eventutils.py

mpy-cross src/mqtt.py

mpy-cross src/ntp.py

mpy-cross src/server.py

mpy-cross src/wifimgr.py

mpy-cross src/umqtt_simple.py

mpy-cross src/alexaserver.py



rem ampy  --port %1 ls
rem echo ERRORLEVEL
rem if ERRORLEVEL 1 goto :fim


if "%2"=="" goto :todos  

goto :so


:todos
:upload
cd src
ampy -d 1 --port %1 put boot.py
ampy  --port %1 put command32.mpy	
ampy  --port %1 put commandutils.mpy	
ampy  --port %1 put command8266.mpy
ampy  --port %1 put config.mpy

ampy  --port %1 put configshow.mpy

ampy  --port %1 put csConfig.mpy
ampy  --port %1 put csGpio.mpy

ampy  --port %1 put configutils.mpy	
ampy  --port %1 put event.mpy
ampy  --port %1 put eventutils.mpy
ampy  --port %1 put main.py
ampy  --port %1 put app.mpy
ampy  --port %1 put mqtt.mpy	
ampy  --port %1 put ntp.mpy
ampy  --port %1 put server.mpy
ampy  --port %1 put wifimgr.mpy
ampy  --port %1 put umqtt_simple.mpy
ampy  --port %1 put help.tmpl
ampy  --port %1 put commandutils.mpy
ampy  --port %1 put wssid.html
ampy --port %1 put wfalhou.html
ampy --port %1 put alexaserver.mpy
ampy --port %1 put alexa_description.xml
ampy --port %1 put alexa_search.html

cd ..
goto :fim

:so
rem ampy  --port %1 rm ".\src\%2"
ampy -d 0.5 --port %1 put .\src\%2


:fim
rem ampy --port %1 run main.py






