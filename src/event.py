from gc import collect
from time import ticks_diff, ticks_ms

from machine import Pin, idle, reset_cause

import config as g

_N = None
_T = True
_F = False
utm = ticks_ms()
nled = 0
def init():
    pass
def timerEvent(x):
    cv(False)
def led(v):
    pin = int(g.config['led'] or 255)
    if pin > 16:
        return
    Pin(pin, Pin.OUT).value(v)
def spin(p1: str, p3) -> str:
    return g.spin(p1, p3)
def p(pin: str, msg: str):
    try:
        from mqtt import p, tCmdOut
        p(tCmdOut()+'/%s' % pin, msg)
    except:
        pass
def setSleep(n: int):
    pass
def checkTimer(seFor: int, p: str, v, mode: int, lista, force=_F):
    m = 0
    t = 0
    try:
        key = str(p)
        if v == seFor and key in lista:
            t = lista[key] or 0
            if t > 0:
               try: 
                m = g.timeOnOff[key] or 0
                if (m > 0) and (ticks_diff(ticks_ms(), m) > t*1000):
                    g.spin(p, 1-seFor)
                    return True
               except: pass     
    except Exception as e:
        print('Erro Time seFor {} em {}: {} [{},{}] {}'.format(
            seFor, key, p, m, t, e))
    return False

def o(p: str, v, mode: int, force=_F, topic: str = None):
    try:
        if not checkTimer(0, p, v, mode, g.config[g.gpio_timeon], force):
            checkTimer(1, p, v, mode, g.config[g.gpio_timeoff], force)
        key = str(p)
        x = g.gVlr(p)
        if force or (v - x) != 0:
            g.sVlr(p, v)
            g.trigg(p, v)
            from mqtt import p as mqttp
            from mqtt import tCmdOut
            mqttp((topic or tCmdOut())+'/' + p, v)
    except Exception as e:
        print('{} {}'.format('event.switch: ', e))
    idle()
def cv(mqtt_active=False):
    global utm, nled
    try:
        t = ticks_ms()
        if ticks_diff(t, utm) > g.config["interval"]*1000:
            nled += 1
            bled = (nled % 30 == 0)
            if bled:
                led(0)
            utm = t
            for i in g.config[g.gp_mde]:
                stype = g.gstype(i)
                md = g.gMde(i)
                if (md != None):
                    from mqtt import tpfx
                    if (md in [1, 2]):
                        v = g.gpin(i)
                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'gpio'))
                        setSleep(1)
                        continue
                    elif (md == 3):
                        v = ADCRead(i)
                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'adc'))
                        setSleep(1)
                        continue
            if bled:
                led(1)
                if nled > 250:
                    nled = 0

    except Exception as e:
        print('{} {}'.format('event.cv: ', e))
    collect()
    idle()
def ADCRead(pin: str):
    from machine import ADC
    return ADC(int(pin)).read()
def interruptTrigger(pin):
    p = -1
    for key in g.dados[g.PINS]:
        if g.dados[g.PINS][key] == pin:
            p = int(key)
    if p >= 0:
        o(p, pin.value(), None, _T)
        print('gpio {} set {}'.format(p,pin.value()))
g.irqEvent(interruptTrigger)