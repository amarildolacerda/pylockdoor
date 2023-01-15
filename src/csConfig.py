from gc import mem_alloc, mem_free

from machine import RTC

import config as g


def getRTCNow():
    return RTC().datetime()
def shConfig(x=False):
    m = {}
    try:
        m['ip'] = g.dados[g.IFCONFIG]        
        m['free'] = mem_free()
        m['alloc'] = mem_alloc()
        m['time'] = str(getRTCNow())
        if not x:
            m.pop('password')
    except:
        pass
    return str(m)