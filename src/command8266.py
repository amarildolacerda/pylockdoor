

from machine import ADC, reset

from config import (gKey, gpin, model, readFile, reset_factory, save, sKey,
                    sMde, spin, sstype, sTimeOff, sTimeOn, sTrg, sVlr, swt)

_N = None
_g = 'get'
_s =  'set'
def r(m, response='/response'):
        from mqtt import sdRsp
        sdRsp(m,0,response)
        return m
def rPin(pin, m):
        from mqtt import sdPinRsp
        return sdPinRsp(pin, m)
def tpRcv(t, p):
    _c = t.split('/')
    if len(_c)>2 and  _c[1] == 'scene':
        return cmmd('scene '+_c[2]+' set '+p)
    return rcv(p)    
def rcv(c):
    cmds = c.split(';')
    r = ''
    from gc import collect
    for item in cmds:
        r += (cmmd(item) or '') + '\r\n'
        collect()
    return r
def cmmd(c):
    k = 'OK'
    c = c.strip()
    cmd = ''
    cmd1 = ''
    cmd2 = ''
    try:
        try:
            p = c.split(' ', 5)
            cmd = p[0]
            if (len(p) > 1):
                cmd1 = p[1]
            if (len(p) > 2):
                cmd2 = p[2]
            if cmd == 'help' :
               return  r(readFile('help.tmpl'))
            elif cmd == 'scan':
                from wifimgr import wlan_sta     
                rsp =[]
                for n in wlan_sta.scan():
                    rsp.append("{}:{}".format(n[0].decode(),n[3]))
                return r(rsp)    
            elif cmd == 'open':
                    with open(cmd1,'r') as f:
                        return r(f.read())    
            elif cmd == "show":
                if cmd1=='scene':
                    from config import events
                    return r(gKey(events))
                elif cmd1 =='config':
                    from config import config
                    return r(config)
                elif cmd1 == 'mqtt':
                    from configshow import shMqtt
                    return r(shMqtt())
                elif cmd1 == "gpio":
                    import csGpio
                    return r(csGpio.shGpio())
                from configshow import show
                return r(show())

            elif cmd == 'save':
                return r(save())
            elif cmd=='collect()':
                from gc import collect

                from machine import idle, soft_reset
                idle()
                collect()
                return r(k)
            elif cmd == 'reset':
               #if cmd1=='factory':
               #   from config import reset_factory
               #   return reset_factory()
               #else:   
               # return reset()
                pass
            elif cmd == 'gpio':
                if cmd1 == 'clear':
                   return r( model('clear'))
                elif cmd2 == 'timeoff':
                    return r(sTimeOff(p))
                elif cmd2 == 'timeon':
                    return r(sTimeOn(p))
                elif cmd2 == 'type':
                    return r(sstype(cmd1, p[3]))
                else:
                    if cmd2 == _s:
                        return r(spin(cmd1, p[3]))
                    elif cmd2 == 'switch':
                        return r(swt(cmd1))
                    else:
                        if cmd2 == _g:
                            return r(gpin(p[1]))
                        elif cmd2 == 'mode':
                            return r(sMde(cmd1, p[3]))
                        elif cmd2 == 'trigger':
                            return r(sTrg(p))
                return k
            elif cmd == "scene":
                from config import sEvent
                return r(sEvent(p))
            elif cmd =='pub':
                from config import sPub
                return r(sPub(p))    
            elif cmd == "adc":
                if cmd2 == _s:
                    return r(sadc(p))
                elif cmd2 == _g:
                    return r(gadc(p))
                return k
            elif cmd == 'set' or cmd=='setvar':
                if cmd1 == 'model':
                    return model(cmd2)
                return r(sKey(cmd1, cmd2))
            elif cmd == 'get' or cmd=='getvar':
                return r(gKey(cmd1))
            return r('{}{}'.format(cmd, c),'/error')
        except Exception as e:
            print(e)
            return r('E {}: {}'.format(c, e),'/error')
    finally:
        pass
def sadc(p):
    pass
def gadc(p):
    pin = int(p[1])
    v = ADC(pin).read()
    sVlr(p[1], v)
    return str(v)
