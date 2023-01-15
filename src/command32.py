
_N = None
_g = 'get'
_s = 'set'

import mqtt

ultimo = 0
def cv(mqtt_active=False):
    from command8266 import cv
    return cv(mqtt_active)
def r(p):
    if (p!=_N):
      from mqtt import sdRsp  
      return sdRsp(p)
def rcv(cmd):
    from command8266 import rcv
    return rcv(cmd)