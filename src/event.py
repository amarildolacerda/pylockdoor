from config import (PINADC, gKey, gMde, gp_mde, gpin, gpio_timeoff,
                    gpio_timeon, gstype, gVlr, spin, sVlr, timeOnOff, trigg)

_N = None
_T = True
_F = False
nled = 0
utm = None
def timerEvent(x):
    cv(False)
def led(v):
    pin = int(gKey('led') or 255)
    if pin > 16:
        return
    spin(pin,v)    
def spin(p1: str, p3) -> str:
    return spin(p1, p3)
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
                m = timeOnOff[key] or 0
                from time import ticks_diff, ticks_ms
                if (m > 0) and (ticks_diff(ticks_ms(), m) > t*1000):
                    spin(key, 1-seFor)
                    return True
               except: pass     
    except Exception as e:
        print('Erro Timer seFor {} em {}: {} [{},{}] {}'.format(
            seFor, key, p, m, t, e))
    return False

def o(p: str, v, mode: int, force=_F, topic: str = None):
    try:
        if p==None: return 'event.o.p is None'
        if not checkTimer(0, p, v, mode, gKey(gpio_timeon), force):
            checkTimer(1, p, v, mode, gKey(gpio_timeoff), force)
        key = str(p)
        x = gVlr(key)
        if force or (v - x) != 0:
            sVlr(key, v)
            trigg(key, v)
            from mqtt import p as mqttp
            from mqtt import tCmdOut
            mqttp((topic or tCmdOut())+'/' + key, str(v))
    except Exception as e:
        print('{} {}'.format('event.switch: ', e))
def cv(mqtt_active=False):
    global utm, nled
    try:
        from time import ticks_diff, ticks_ms
        t = ticks_ms()
        if ticks_diff(t, utm) > gKey("interval")*1000:
            nled += 1
            bled = (nled % 30 == 0)
            if bled:
                led(0)
            utm = t
            
            for i in gKey(gp_mde).keys():
                stype = gstype(i)
                md = gMde(i)
                if (md != None):
                    from mqtt import tpfx
                    if (md in [1, 2]):
                        o(i, gpin(i), md, False, tpfx() +
                          '/{}'.format(stype or 'gpio'))
                        continue
                    elif (md == PINADC):
                        v = ADCRead(i)
                        from config import trigPub
                        if (v>0):
                            o(i, v, md, False,  '{}/{}'.format(tpfx(),stype or 'adc'))
                        trigPub(i, v)
                        continue
            if bled:
                led(1)
                if nled > 250:
                    nled = 0

    except Exception as e:
        print('{} {}'.format('event.cv: ', e))
    from gc import collect
    collect()    
def ADCRead(pin: str):
    from machine import ADC
    return ADC(int(pin)).read()
def interruptTrigger(pin):
    p = None
    from config import PINS, dados
    for k in dados[PINS].keys():
        if dados[PINS][k] == pin:
            p = k
        if p:    
            o(str(p), pin.value(), None, _T)

def init():
    global utm
    from config import irqEvent
    irqEvent(interruptTrigger)
    from time import ticks_ms
    utm = ticks_ms()
