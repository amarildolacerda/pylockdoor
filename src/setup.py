from micropython import const

name = const("ldr")
# name = None
deviceType = const("ldr")
# label=const('Interruptor')
label = const("bancada")
ssids = [["VIVOFIBRA-A360", "6C9FCEC12A"], ["micasa", "3938373635"], ["visitante", ""]]

mqtt_host = "none"
mqtt_port = const(1883)
set_model = "15"
auto_pin = "4"
interval = 0.3


def configurar():
    from config import sKey, sMde

    sMde("0", "adc")
    # sKey('interval',60)
    # from command8266 import cmmd
    # cmmd('gpio 4 trigger 15 bistable')
    pass


def changed(pin, value):
    if deviceType == "ldr":

        if value > 600:
            from config import strigg

            strigg(auto_pin, 1)
        elif value < 400:
            from config import strigg

            strigg(auto_pin, 0)
    pass
