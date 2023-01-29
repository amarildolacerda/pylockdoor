from micropython import const

#name= const('cafe')
name=None
label=const('Interruptor')

ssids = [["VIVOFIBRA-A360","6C9FCEC12A"],['micasa','3938373635']]

mqtt_host =const('broker.emqx.io')
mqtt_port = const(1883)

set_model = const('15')
auto_pin = const('4')
interval = 0.3
def start():
    pass
