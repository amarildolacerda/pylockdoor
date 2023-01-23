
from gc import collect
from time import sleep

from machine import ADC, idle, reset

_N = None
_g = 'get'
_s =  'set'
sendCB = None
def r(p, response='/response'):
    global sendCB
    try:
        if (p != _N):
            from mqtt import sdRsp
            sdRsp(p,0,response)
        if sendCB:
            sendCB(p+'\r\n')
    finally:
        return p
def rPin(pin, p):
    global sendCB
    try:
        if (p != _N):
            from mqtt import sdPinRsp
            sdPinRsp(pin, p)
        if sendCB:
            sendCB(p+'\r\n')
    finally:
        return p
def tpRcv(t, p):
    _c = t.split('/')
    if _c[0] == 'scene':
        return cmd('scene '+_c[1]+' set '+p)
    return rcv(p)    
def rcv(c):
    cmds = c.split(';')
    r = ''
    for item in cmds:
        print(item)
        r += (cmmd(item) or '') + '\r\n'
        idle()
        collect()
    return r
def cmmd(c):
    print('cmd',c)
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
            from config import readFile, reset_factory, save
            if cmd=='open' :
               return r(readFile(cmd1))     
            elif cmd == 'reset' and cmd1 == 'factory':
                reset_factory()
                reset()
                return k
            elif cmd == 'help' :
               return  r(readFile('help.tmpl'))
            elif cmd == "show":
                if cmd1 == 'mqtt':
                    from configshow import shMqtt
                    return r(shMqtt())
                elif cmd1 == "gpio":
                    import csGpio
                    return r(csGpio.shGpio())
                from configshow import show
                return r(show())

            elif cmd == 'save':
                return r(save())
            elif cmd == 'reset':
                reset()
            elif cmd == 'gpio':
                from config import (gKey, gpin, model, save, sKey, sMde, spin,
                                    sstype, sTimeOff, sTimeOn, sTrg, swt)
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
                        return swt(cmd1)
                    else:
                        if cmd2 == _g:
                            v = gpin(p[1])
                            rsp = r(gpin(p[1]))
                            return rsp
                        elif cmd2 == 'mode':
                            return sMde(cmd1, p[3])
                        elif cmd2 == 'trigger':
                            return sTrg(p)
                return k
            elif cmd == "adc":
                if cmd2 == _s:
                    return r(sadc(p))
                elif cmd2 == _g:
                    return r(gadc(p))
                return k
            elif cmd == 'set':
                if cmd1 == 'sleep':
                    sKey('sleep',  int(cmd2))
                    return r(save())
                elif cmd1 == 'model':
                    return model(cmd2)
                return r(sKey(cmd1, cmd2))
            elif cmd == 'get':
                return r(gKey(cmd1))
            return ('invalid:{}->{}'.format(cmd, c))
        except Exception as e:
            from mqtt import error
            error('E {}: {}'.format(c, e))
    finally:
        pass
def sadc(p):
    pass
def gadc(p):
    pin = int(p[1])
    v = ADC(pin).read()
    from config import sVlr
    sVlr(p[1], v)
    return str(v)
