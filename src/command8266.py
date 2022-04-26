
import config as g
import mqtt
import machine
import time
_N = None
_g = 'get'
_s = 'set'

sendCB = None


def r(p):
    global sendCB
    try:
        if (p != _N):
            mqtt.sdRsp(p)
        if sendCB:
            sendCB(p+'\r\n')
    finally:
        return p


def rPin(pin, p):

    global sendCB
    try:
        if (p != _N):
            mqtt.sdPinRsp(pin, p)
        if sendCB:
            sendCB(p+'\r\n')
    finally:
        return p


def gpwm(p):
    p(g.config['pwm_duty'][int(p[1])])


def tpRcv(t, p):
    _c = t.split('/')
    _p = p
    if _c[0] == 'scene':
        _p = 'scene '+_c[1]+' set '+_p
    rcv(_p)


def rcv(c):
    k = 'OK'
    c = c.strip()
    cmd = ''
    cmd1 = ''
    cmd2 = ''
    try:
        try:
            if c == 'reset factory':
                g.reset_factory()
                machine.reset()
                return k
            p = c.split(' ', 5)
            cmd = p[0]
            if (len(p) > 1):
                cmd1 = p[1]
            if (len(p) > 2):
                cmd2 = p[2]

            if cmd == "show":
                if cmd1 == 'config':
                    # import csConfig
                    return r(g.config)  # r(csConfig.shConfig(True))
                elif cmd1 == 'mqtt':
                    import configshow
                    return r(configshow.shMqtt())
                elif cmd1 == "gpio":
                    import csGpio
                    return r(csGpio.shGpio())
                elif cmd1 == 'help':
                    import csHelp
                    return r(csHelp.shHelp())
                elif cmd1 == 'scene':
                    import configshow
                    return r(configshow.shScene())
                elif cmd1 == 'stats':
                    return mqtt.sendStatus(True)
                import configshow as cs
                return r(cs.show())

            elif cmd == 'save':
                return r(g.save())
            elif cmd == 'reset':
                machine.reset()
            elif cmd == 'dht11':
                import event
                r(event.getDht11(cmd1))
            elif cmd == 'dht12':
                import event
                r(event.getDht12(cmd1))
            elif cmd == g.events:  # scene
                return g.sEvent(p)
            elif cmd == 'delay':
                time.sleep(g.strToNum(cmd1))
            elif cmd == 'gpio':
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
                            if v == 0:
                                import event
                                event.setSleep(1)
                            return rsp

                        elif cmd2 == 'mode':
                            return g.sMde(cmd1, p[3])
                        elif cmd2 == 'trigger':
                            return g.sTrg(p)
                return k
            elif cmd == 'pwm':
                if cmd2 == _g:
                    return r(gpwm(p))
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
                elif cmd1 == 'account':
                    return mqtt.account(cmd2)
                return r(g.sKey(cmd1, cmd2))
            elif cmd == 'get':
                return r(g.gKey(cmd1))
            elif cmd == 'sleep':
                r('sleeping')
                return event.deepsleep(int(cmd1))
            r('invalido: {}'.format(c))
        except Exception as e:
            print('Command {}: {}'.format(c, e))

    finally:
        pass


def sadc(p):
    pass


def gadc(p):
    pin = int(p[1])
    v = machine.ADC(pin).read()
    g.sVlr(p[1], v)
    return str(v)
