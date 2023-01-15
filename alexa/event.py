from gc import collect
from time import ticks_diff, ticks_ms

from machine import ADC, RTC, Pin, idle, reset_cause

import config as g
from mqtt import tCmdOut, tpfx

_N = None
_T = True
_F = False
utm = ticks_ms()
nled = 0
def led(v):
    pin = int(g.config['led'] or 255)
    if pin > 16:
        return
    Pin(pin, Pin.OUT).value(v)
def spin(p1: str, p3) -> str:
    return g.spin(p1, p3)
def p(pin: str, msg: str):
    try:
        from mqtt import p as mqttp
        mqttp(tCmdOut()+'/%s' % pin, msg)
    except:
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
                except:
                    m = 0
                if (m == 0) or (ticks_diff(ticks_ms(), m) > t*1000):
                    g.spin(p, 1-seFor)
                    return True
    except Exception as e:
        print(str(e))
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

            mqttp((topic or tCmdOut())+'/' + p, v)
    except Exception as e:
        print('event.o: {}'.format(str(e)))
def cv(mqtt_active=False):
    global utm, nled
    try:
        t = ticks_ms()
        if ticks_diff(t, utm) > g.config[g.CFG_INTERVAL]*1000:
            nled += 1
            bled = (nled % 30 == 0)
            if bled:
                led(0)
            utm = t
            for i in g.config[g.gp_mde]:
                stype = g.gstype(i)
                md = g.gMde(i)
                if (md != None):
                    if (md in [g.PinOUT, g.PinIN]):
                        v = g.gpin(i)

                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'gpio'))
                        #localTrig(i,'gpio',v)  
                        #setSleep(1)
                        continue
                    elif (md == g.PinADC):
                        v = ADCRead(i)
                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'adc'))
                        #localTrig(i,'adc',v)  
                        #setSleep(1)
                        continue
            if bled:
                led(1)
                if nled > 250:
                    nled = 0

    except Exception as e:
        print('{} {}'.format('event.cv: ', e))
def ADCRead(pin: str):
    return ADC(int(pin)).read()
    
def interruptTrigger(pin: Pin):
    p = -1
    print('PINS:',g.dados[g.PINS])
    for key in g.dados[g.PINS].keys():
        if g.dados[g.PINS][key] == pin:
            p = int(key)
    print('NOTIFY gpio {} get -> {}'.format(p,pin.value()))        
    if p >= 0:
        o(str(p), pin.value(), None, _T)
    collect()


g.irqEvent(interruptTrigger)