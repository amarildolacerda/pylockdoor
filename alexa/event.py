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
        print(str(e))
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
                    if (md in [1, 2]):
                        v = g.gpin(i)

                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'gpio'))
                        localTrig(i,'gpio',v)  
                        #setSleep(1)
                        continue
                    elif (md == 3):
                        v = ADCRead(i)
                        o(i, v, md, False, tpfx() +
                          '/{}'.format(stype or 'adc'))
                        localTrig(i,'adc',v)  
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
    for key in g.pins:
        if g.pins[key] == pin:
            p = int(key)
    if p >= 0:
        o(p, pin.value(), None, _T)
    collect()
  
sv = {"none":None}  
def localTrig(i: str,stype: str,value: int):
    global sv 
    for j in g.config[g.conds]:
        cmd = j.split(',',8)
        c = cmd[2]
        a = int(cmd[3])
        tp = cmd[4] 
        p = cmd[5]
        v = g.strToNum(cmd[6] or str(value))
        if (tp=='s'):
          try: 
            x = sv.get('{}'.format(p)) or '-1'
            if (cmd[0]==stype)  and cmd[1]==i and x != cmd[6]: # and vo != value   :  
                rsp = None
                vo = g.strToNum('{}'.format(value))
                va = g.strToNum('{}'.format(a))
                if (c == 'eq' and vo == va):
                    rsp = 'eq'
                elif (c == 'lt' and vo < va):
                    rsp = 'lt'
                elif (c == 'gt' and vo > va):
                    rsp = 'gt'        
                elif (c == 'ne' and vo != va):
                    rsp = 'ne'

                if (rsp != None):
                    from mqtt import p as mqttp

                    mqttp(tpfx()+'/scene/'+p,cmd[6])
                    _p = 'scene '+p+' set '+cmd[6]
                    print(_p)
                    sv['{}'.format(p)] =cmd[6]
                    from commands import rcv
                    rcv(_p)
            continue
          except Exception as e: 
                print('error {}, {}=={} and {}=={} {} '.format(cmd,cmd[0],stype,cmd[1],i,e))
        elif (tp=='t'):
            vo = g.strToNum(g.gpin(p))
            if (cmd[0]==stype)  and (cmd[1]==i and (vo != v)):  
                rsp = None;
                if (c=='lt') and (value < a):
                    rsp = g.spin(p, v, True)
                elif (c=='gt') and (value > a):
                    rsp = g.spin(p, v,True)
                elif (c=='eq') and (value == a):
                    rsp = g.spin(p,v, True)
                elif (c=='ne') and (value != a):
                    rsp = g.spin(p,v, True)
                if (rsp != None):
                    from mqtt import p as mqttp

                    mqttp(tpfx() +'/gpio/' + p, g.gpin(p) )    
            continue   
    collect()
    return 'nok'

g.irqEvent(interruptTrigger)