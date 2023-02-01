from micropython import const

name= 'entrada'
label=const('Luz da Entrada')

ssid = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635']]

mqtt_host ='none' 
#mqtt_host = const('broker.emqx.io')
mqtt_port = const(1883)

set_model = False
auto_pin = const('15')
relay_pin = const('15')

def start():
    #from config import sEvent
    #sEvent('scene noite trigger 5')
    pass
