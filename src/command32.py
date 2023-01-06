_N = None
_g = 'get'
_s = 'set'
from gc import collect

import command8266 as esp8266
import mqtt

collect()
ultimo = 0
def cv(mqtt_active=False):
    return esp8266.cv(mqtt_active)
def r(p):
    if (p!=_N):
      return mqtt.sdRsp(p)
def rcv(cmd):
    return esp8266.rcv(cmd)