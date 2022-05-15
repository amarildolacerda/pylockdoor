echo %2


if "%2"=="ls" goto :fim  

if "%2"=="upload" goto :upload

echo compilando....
python -m mpy_cross src/app.py
python -m mpy_cross src/boot.py
python -m mpy_cross src/command32.py
python -m mpy_cross src/command8266.py
python -m mpy_cross src/commandutils.py
python -m mpy_cross src/config.py
python -m mpy_cross src/configshow.py
python -m mpy_cross src/csConfig.py
python -m mpy_cross src/csGpio.py
python -m mpy_cross src/configutils.py
python -m mpy_cross src/event.py
python -m mpy_cross src/eventutils.py
python -m mpy_cross src/mqtt.py
python -m mpy_cross src/ntp.py
python -m mpy_cross src/server.py
python -m mpy_cross src/wifimgr.py
python -m mpy_cross src/umqtt_simple.py



rem ampy  --port %1 ls
rem echo ERRORLEVEL
rem if ERRORLEVEL 1 goto :fim


if "%2"=="" goto :todos  

goto :so


:todos
:upload
cd src
ampy -d 0.5 --port %1 put boot.py
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

cd ..
goto :fim

:so
rem ampy  --port %1 rm ".\src\%2"
ampy  --port %1 put .\src\%2


:fim
rem ampy --port %1 run main.py






