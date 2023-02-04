from utime import ticks_diff, ticks_ms

from config import (PINADC, PININ, PINOUT, gKey, gMde, gp_mde, gpin,
                    gpio_timeoff, gpio_timeon, gstype, gVlr, spin , sVlr,
                    timeOnOff, trigg)

_N = None
_T = True
_F = False
nled = 0
utm = None
def timerEvent(x):
    cv(False)
def led(v):
    p = int(gKey('led') or 255)
    if p > 16:
        return
    spin('{}'.format(p),v)    
def p(pin: str, msg: str):
    try:
        from mqtt import p as cmd
        from mqtt import tCmdOut
        cmd(tCmdOut()+'/%s' % pin, msg)
    except:
        pass
def setSleep(n: int):
    pass
def checkTimer(seFor: int, p: str, v, mode: int, lista, force=_F):
    m = 0
    t = 0
    key = str(p)
    try:
        if v == seFor and key in lista:
            t = lista[key] or 0
            if t > 0:
               try: 
                m = timeOnOff[key] or 0
                if (m > 0) and (ticks_diff(ticks_ms(), m) > t*1000):
                    spin(key, 1-seFor)
                    return True
               except: pass     
    except Exception as e:
        print('Erro Timer seFor {} em {}: {} [{},{}] {}'.format(
            seFor, key, p, m, t, e))
    return False

semaforo = []
def o(p1: str, v, mode, force=_F, topic=None):
    if p1 in semaforo: return
    try:
        semaforo.append(p1)
        if p1==None: return 'event.o.p is None'

        if not checkTimer(0, p1, v, mode, gKey(gpio_timeon), force):
            checkTimer(1, p1, v, mode, gKey(gpio_timeoff), force)
        key = str(p1)
        x = gVlr(key)
        if force or (v - x) != 0:
            sVlr(key, v)
            trigg(key, v)
            from mqtt import p as mqttp
            from mqtt import tCmdOut
            mqttp((topic or tCmdOut())+'/' + key, str(v))
            from setup import changed
            changed(key,v)  

    except Exception as e:
        print('{} {}'.format('event.switch: ', e))
    finally:
        semaforo.remove(p1)    
def cv(mqtt_active=False):
    global utm, nled, inCV
    try:
        t = ticks_ms()
        if ticks_diff(t, utm) > gKey("interval")*1000:
            nled += 1
            bled = (nled % 30 == 0)
            if bled:
                led(0)
            utm = t
            
            for i in gKey(gp_mde).keys():
                md = gMde(i)
                if (md != None):
                    from mqtt import tpfx
                    if (md in [PININ, PINOUT]):
                        o(i, gpin(i), md, False, tpfx() +
                          '/{}'.format( 'gpio'))
                        continue
                    elif (md == PINADC):
                        v = ADCRead(i)
                        from config import trigPub
                        if (v>0):
                            o(i, v, md, False,  '{}/{}'.format(tpfx(), 'adc'))
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
    utm = ticks_ms()
