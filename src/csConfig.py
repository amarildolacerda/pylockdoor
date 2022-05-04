from machine import RTC
import gc
import config as g


def getRTCNow():
    return RTC().datetime()


def shConfig(x=False):
    m = {}
    try:
        m['ip'] = g.ifconfig
 #       for item in g.config:
 #           if not ('gpio' in item) and (not ('mqtt' in item)):
 #               m[item] = g.config[item]
        m['free'] = gc.mem_free()
        m['alloc'] = gc.mem_alloc()
        m['time'] = str(getRTCNow())
        if not x:
            m.pop('password')

    except:
        pass
    return str(m)
