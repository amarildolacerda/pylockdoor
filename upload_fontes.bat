
:todos

ampy -d 0.5 --port %1 put ./src/boot.py
ampy -d 0.5 --port %1 put ./src/command32.py	
ampy -d 0.5 --port %1 put ./src/commandutils.py	
ampy -d 0.5 --port %1 put ./src/command8266.py
ampy -d 0.5 --port %1 put ./src/config.py
ampy -d 0.5 --port %1 put ./src/configshow.py
ampy -d 0.5 --port %1 put ./src/configutils.py	
ampy -d 0.5 --port %1 put ./src/event.py
ampy -d 0.5 --port %1 put ./src/eventutils.py
ampy -d 0.5 --port %1 put ./src/main.py
ampy -d 0.5 --port %1 put ./src/app.py
ampy -d 0.5 --port %1 put ./src/mqtt.py	
ampy -d 0.5 --port %1 put ./src/ntp.py
ampy -d 0.5 --port %1 put ./src/server.py
ampy -d 0.5 --port %1 put ./src/wifimgr.py
rem ampy -d 0.5 --port %1 put ./src/umqtt_simple.py
goto :fim

:so
rem ampy -d 0.5 --port %1 rm ".\src\%2"
ampy -d 0.5 --port %1 put .\src\%2


:fim
rem ampy --port %1 run main.py






