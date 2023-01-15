from gc import mem_alloc, mem_free

import commandutils as u
import config as g

_N = None
def show():
    m = {}
    m['time'] = u.now()
    m['ssid'] = g.config['ssid']
    m['free']  = mem_free()
    m['alloc'] = mem_alloc()
    m['id'] = g.uid
    m['ip'] = g.dados[g.IFCONFIG]
    return str(m)
def shMqtt():
    m = {}
    for item in g.config:
        if ('mqtt' in item):
            m[item] = g.config[item]
    return str(m)
def shScene():
    return str(g.config[g.events])
