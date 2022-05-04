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
python -m mpy_cross src/csHelp.py
python -m mpy_cross src/configutils.py
python -m mpy_cross src/event.py
python -m mpy_cross src/eventutils.py
python -m mpy_cross src/mqtt.py
python -m mpy_cross src/ntp.py
python -m mpy_cross src/server.py
python -m mpy_cross src/wifimgr.py
python -m mpy_cross src/umqtt_simple.py



rem ampy -d 0.5 --port %1 ls
rem echo ERRORLEVEL
rem if ERRORLEVEL 1 goto :fim


if "%2"=="" goto :todos  

goto :so


:todos
:upload

ampy -d 0.5 --port %1 put ./src/boot.py
ampy -d 0.5 --port %1 put ./src/command32.mpy	
ampy -d 0.5 --port %1 put ./src/commandutils.mpy	
ampy -d 0.5 --port %1 put ./src/command8266.mpy
ampy -d 0.5 --port %1 put ./src/config.mpy

ampy -d 0.5 --port %1 put ./src/configshow.mpy

ampy -d 0.5 --port %1 put ./src/csConfig.mpy
ampy -d 0.5 --port %1 put ./src/csGpio.mpy
ampy -d 0.5 --port %1 put ./src/csHelp.mpy

ampy -d 0.5 --port %1 put ./src/configutils.mpy	
ampy -d 0.5 --port %1 put ./src/event.mpy
ampy -d 0.5 --port %1 put ./src/eventutils.mpy
ampy -d 0.5 --port %1 put ./src/main.py
ampy -d 0.5 --port %1 put ./src/app.mpy
ampy -d 0.5 --port %1 put ./src/mqtt.mpy	
ampy -d 0.5 --port %1 put ./src/ntp.mpy
ampy -d 0.5 --port %1 put ./src/server.mpy
ampy -d 0.5 --port %1 put ./src/wifimgr.mpy
ampy -d 0.5 --port %1 put ./src/umqtt_simple.mpy

goto :fim

:so
rem ampy -d 0.5 --port %1 rm ".\src\%2"
ampy -d 0.5 --port %1 put .\src\%2


:fim
rem ampy --port %1 run main.py






