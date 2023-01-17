
_N = None
def show():
    from gc import mem_alloc, mem_free

    import commandutils as u
    import config as g
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
    from config import config
    for item in config:
        if ('mqtt' in item):
            m[item] = config[item]
    return str(m)
