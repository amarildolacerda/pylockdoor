from machine import RTC
import gc
import config as g
import commandutils as u
_N = None
def show():
    m = {}
    m['time'] = u.now()
    m['ssid'] = g.config['ssid']
    m['free'] =gc.mem_free()
    m['alloc'] = gc.mem_alloc()
    m['id'] = g.uid
    m['ip'] = g.ifconfig
    return str(m)
def shMqtt():
    m = {}
    for item in g.config:
        if ('mqtt' in item):
            m[item] = g.config[item]
    return str(m)
def shScene():
    return str(g.config[g.events])
