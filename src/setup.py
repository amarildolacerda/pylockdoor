from micropython import const

name= None
label=const('Interruptor')

#ssid =const('micasa')
#password=const('3938373635')
ssid = "VIVOFIBRA-A360"
password = "6C9FCEC12A"

mqtt_host =const('broker.emqx.io')
mqtt_port = const(1883)

auto_pin = const('4')
relay_pin = const('15')


