echo %2

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




if "%2"=="" goto :todos
ampy -d 0.5 --port %1 put %2
goto :fix


:todos

ampy -d 0.5 --port %1 put boot.py
ampy -d 0.5 --port %1 put commandutils.mpy	
ampy -d 0.5 --port %1 put command8266.mpy
ampy -d 0.5 --port %1 put config.mpy

ampy -d 0.5 --port %1 put configshow.mpy

ampy -d 0.5 --port %1 put csConfig.mpy
ampy -d 0.5 --port %1 put csGpio.mpy

ampy -d 0.5 --port %1 put event.mpy
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
ampy -d 0.5 --port %1 put setup.mpy
ampy -d 0.5 --port %1 put pins.json



:fix

:fim
esptool.py --port %1 --baud 1000000 run  




