
_N = None
desde = None
def show():
    global desde
    from gc import mem_alloc, mem_free

    import commandutils as u
    desde = desde or u.now()
    import config as g
    m = {}
    m['time'] = u.now()
    m['ssid'] = g.config['ssid']
    m['alloc'] = mem_alloc()
    m['id'] = g.uid
    m['ip'] = g.dados[g.IFCONFIG]
    m['free']  = mem_free()
    m['up'] = desde
    return str(m)
def shMqtt():
    m = {}
    from config import config
    for item in config:
        if ('mqtt' in item):
            m[item] = config[item]
    return str(m)
