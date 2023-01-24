

def getRTCNow():
    from machine import RTC
    return RTC().datetime()
def shConfig(x=False):
    m = {}
    try:
        from gc import mem_alloc, mem_free

        from config import IFCONFIG, dados
        m['ip'] = dados[IFCONFIG][0]        
        m['free'] = mem_free()
        m['alloc'] = mem_alloc()
        m['time'] = str(getRTCNow())
        if not x:
            m.pop('password')
    except:
        pass
    return str(m)