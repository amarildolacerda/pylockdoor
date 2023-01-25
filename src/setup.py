from micropython import const

name= None
label=const('Interruptor')

ssid = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635']]

mqtt_host =const('broker.emqx.io')
mqtt_port = const(1883)

set_model = False
auto_pin = const('5')
relay_pin = const('5')

def start():
    from config import sEvent
    sEvent('scene noite trigger 5')
