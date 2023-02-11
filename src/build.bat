echo %2

set b=%3
if "%3"=="" set b=115200

del *.mpy




echo compilando....

..\mpy-cross app.py

..\mpy-cross boot.py


..\mpy-cross command8266.py

..\mpy-cross commandutils.py

..\mpy-cross config.py

..\mpy-cross configshow.py

..\mpy-cross csConfig.py

..\mpy-cross csGpio.py

..\mpy-cross event.py


..\mpy-cross mqtt.py

..\mpy-cross ntp.py

..\mpy-cross server.py

..\mpy-cross wifimgr.py

..\mpy-cross umqtt_simple.py

..\mpy-cross broadcast.py
..\mpy-cross setup.py
..\mpy-cross gpio.py



if "%2"=="all" goto :todos
if "%2"=="" goto :todos
ampy -b %b% --port %1 put %2
goto :fix


:todos
ampy -b %b% --port %1 ls
ampy -b %b% --port %1 put boot.py
ampy -b %b% --port %1 put commandutils.mpy	
ampy -b %b% --port %1 put command8266.mpy
ampy -b %b% --port %1 put config.mpy

ampy -b %b% --port %1 put configshow.mpy

ampy -b %b% --port %1 put csConfig.mpy
ampy -b %b% --port %1 put csGpio.mpy

ampy -b %b% --port %1 put event.mpy
ampy -b %b% --port %1 put main.py
ampy -b %b% --port %1 put app.mpy
ampy -b %b% --port %1 put mqtt.mpy	
ampy -b %b% --port %1 put ntp.mpy
ampy -b %b% --port %1 put server.mpy
ampy -b %b% --port %1 put wifimgr.mpy
ampy -b %b% --port %1 put umqtt_simple.mpy
ampy -b %b% --port %1 put help.tmpl
ampy -b %b% --port %1 put commandutils.mpy
ampy -b %b% --port %1 put broadcast.mpy
ampy -b %b% --port %1 put erro.html
ampy -b %b% --port %1 put eventservice.xml
ampy -b %b% --port %1 put help.tmpl
ampy -b %b% --port %1 put msearch.html
ampy -b %b% --port %1 put setup.xml
ampy -b %b% --port %1 put state.soap
ampy -b %b% --port %1 put setup.mpy
ampy -b %b% --port %1 put pins.json
ampy -b %b% --port %1 put gpio.mpy



:fix

:fim
esptool.py --port %1 --baud 1000000 run  




