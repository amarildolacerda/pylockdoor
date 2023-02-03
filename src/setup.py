from micropython import const

name= const('bancada')
#name=None
#label=const('Interruptor')
label = const('Sensor Bancada')
ssids = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635'],['visitante','']]

mqtt_host ='none'
#mqtt_host = const('broker.emqx.io')
#mqtt_host = "test.mosquitto.org"
mqtt_port = const(1883)

set_model = const('15')
auto_pin = const('4')
interval = 0.3
def configurar():
    #from config import sKey, sMde 
    #sMde('0', 'adc')
    #sKey('interval',60)
    #from command8266 import cmmd
    #cmmd('gpio 4 trigger 15 bistable')
    pass
