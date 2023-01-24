
_N = None
desde = None
def show():
    global desde
    from gc import mem_alloc, mem_free

    import commandutils as u
    desde = desde or u.now()
    from config import IFCONFIG, dados, gKey, uid
    m = '{'
    m += '"ip":"{}",'.format(dados[IFCONFIG][0])
    m += '"uid":"{}",'.format(uid)
    m += '"free":{},'  .format(   mem_free())
    m += '"up":"{}"' .format(   desde)
    m+='}'
    return m
def shMqtt():
    m = '{'
    from config import config
    for item in config:
        if ('mqtt' in item):
            m += '"item":"{}", ' .format(   confg[item])
    m+='}'        
    return m
