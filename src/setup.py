from micropython import const

name= const('cafe')
#name=None
#label=const('Interruptor')
label = const('Café')
ssids = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635'],['visitante','']]

mqtt_host =const('broker.emqx.io')
mqtt_port = const(1883)

set_model = const('15')
auto_pin = const('4')
interval = 0.3
def start():
    pass
