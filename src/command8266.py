
from gc import collect
from time import sleep

from machine import ADC, idle, reset

import config as g

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
            if cmd=='open' :
               return r(g.readFile(cmd1))     
            if cmd == 'reset' and cmd1 == 'factory':
                g.reset_factory()
                reset()
                return k
            if cmd == 'help' :
               return  r(g.readFile('help.tmpl'))
            if cmd == "show":
                if cmd1 == 'config':
                    return r(str(g.config))
                elif cmd1 == 'mqtt':
                    from configshow import shMqtt
                    return r(shMqtt())
                elif cmd1 == "gpio":
                    import csGpio
                    return r(csGpio.shGpio())
                elif cmd1 == 'scene':
                    from configshow import shScene
                    return r(shScene())
                from configshow import show
                return r(show())

            elif cmd == 'save':
                return r(g.save())
            elif cmd == 'reset':
                reset()
            elif cmd == g.events:
                return g.sEvent(p)
            elif cmd == 'gpio':
                if cmd1 == 'clear':
                   return r( g.model('clear'))
                if cmd2 == 'timeoff':
                    return r(g.sTimeOff(p))
                elif cmd2 == 'timeon':
                    return r(g.sTimeOn(p))
                elif cmd2 == 'type':
                    return r(g.sstype(cmd1, p[3]))
                else:
                    if cmd2 == _s:
                        rsp = r(g.spin(cmd1, p[3]))
                        if g.gpin(cmd1) == 1:
                            import event
                            event.setSleep(None)
                        return rsp
                    elif cmd2 == 'switch':
                        return g.swt(cmd1)
                    else:
                        if cmd2 == _g:
                            v = g.gpin(p[1])
                            rsp = r(g.gpin(p[1]))
                            return rsp
                        elif cmd2 == 'mode':
                            return g.sMde(cmd1, p[3])
                        elif cmd2 == 'trigger':
                            return g.sTrg(p)
                return k
            elif cmd == "adc":
                if cmd2 == _s:
                    return r(sadc(p))
                elif cmd2 == _g:
                    return r(gadc(p))
                return k
            elif cmd == 'set':
                if cmd1 == 'sleep':
                    g.config['sleep'] = int(cmd2)
                    return r(g.save())
                elif cmd1 == 'model':
                    return g.model(cmd2)
                return r(g.sKey(cmd1, cmd2))
            elif cmd == 'get':
                return r(g.gKey(cmd1))
            elif cmd == 'clean':
                g.model('clear')
                return r(g.clearCond())
            elif cmd == 'if':
                return r(g.gpioCond(c))        
            ('invalid:{}->{}'.format(cmd, c))
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
    g.sVlr(p[1], v)
    return str(v)
