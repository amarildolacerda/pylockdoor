from micropython import const

name= const('entrada')
#name=None
#label=const('Interruptor')
label = const('Luz da Entrada')
ssids = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635'],['visitante','']]

mqtt_host ='none'
#mqtt_host = const('broker.emqx.io')
mqtt_port = const(1883)

set_model = None #const('15')
auto_pin = '15' #const('4')
interval = 0.3
def start():
    pass
