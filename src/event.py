import gc
import machine
import time
import config as g
import mqtt
import command8266 as ev
_N = None
_T = True
_F = False
utm = time.ticks_ms()
nled = 0
go_sleep = 0
def init():
    pass
def timerEvent(x):
    cv(False)
def led(v):
    pin = int(g.config['led'] or 255)
    if pin > 16:
        return
    machine.Pin(pin, machine.Pin.OUT).value(v)
def spin(p1: str, p3) -> str:
    return g.spin(p1, p3)
def p(pin: str, msg: str):
    try:
        mqtt.p(mqtt.tCmdOut()+'/%s' % pin, msg)
    except:
        pass
def setSleep(n: int):
    global go_sleep
    if (n == None):
        go_sleep = 0
    else:
        go_sleep += n
def checkTimer(seFor: int, p: str, v, mode: int, lista, force=_F):
    global go_sleep
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
                if (m == 0) or (time.ticks_diff(time.ticks_ms(), m) > t*1000):
                    g.spin(p, 1-seFor)
                    return True
        if (go_sleep > 1):
            if (go_sleep < 2 and g.config['sleep'] > 0):
                mqtt.p(mqtt.tCmdOut()+'/sleep', str(g.config['sleep']))
            go_sleep += 1
            if go_sleep > 60:
                go_sleep = 0
                if (g.config['sleep'] > 0):
                    gc.collect()
                    machine.idle()
                    deepsleep(g.config['sleep'])
    except Exception as e:
        print('Erro Time seFor {} em {}: {} [{},{}] {}'.format(
            seFor, key, p, m, t, e))
    return False
def deepsleep(n):
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('iniciando deep sleep')
    rtc.alarm(rtc.ALARM0, n*1000)
    machine.deepsleep()
def o(p: str, v, mode: int, force=_F, topic: str = None):
    try:
        if not checkTimer(0, p, v, mode, g.config[g.gpio_timeon], force):
            checkTimer(1, p, v, mode, g.config[g.gpio_timeoff], force)
        key = str(p)
        x = g.gVlr(p)
        if force or (v - x) != 0:
            g.sVlr(p, v)
            g.trigg(p, v)
            mqtt.p((topic or mqtt.tCmdOut())+'/' + p, v)
    except Exception as e:
        print('{} {}'.format('event.switch: ', e))
    machine.idle()
def cv(mqtt_active=False):
    global utm, nled, go_sleep
    try:
        t = time.ticks_ms()
        if time.ticks_diff(t, utm) > g.config["interval"]*1000:
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
                        o(i, v, md, False, mqtt.tpfx() +
                          '/{}'.format(stype or 'gpio'))
                        localTrig(i,'gpio',v)  
                        setSleep(1)
                        continue
                    elif (md == 3):
                        v = ADCRead(i)
                        o(i, v, md, False, mqtt.tpfx() +
                          '/{}'.format(stype or 'adc'))
                        localTrig(i,'adc',v)  
                        setSleep(1)
                        continue
                    elif (md == 5):
                        o(i, getDht11(i), md, False, mqtt.tpfx() +
                          '/{}'.format(stype or 'dht11'))
                        setSleep(1)
                        continue
                    elif (md == 6):
                        o(i, getDht12(i), md, False, mqtt.tpfx() +
                          '/{}'.format(stype or 'dht12'))
                        setSleep(1)
                        continue
            if bled:
                led(1)
                if nled > 250:
                    nled = 0

    except Exception as e:
        print('{} {}'.format('event.cv: ', e))
    gc.collect()
    machine.idle()
def ADCRead(pin: str):
    return machine.ADC(int(pin)).read()
def getDht11(pin: str):
    import dht
    d = dht.DHT11(machine.Pin(int(pin)))
    d.measure()
    d.temperature()  # eg. 23 (??C)
    d.humidity()
    return {"temp": d.temperature(), "hum": d.humidity()}
def getDht12(pin: str):
    import dht
    d = dht.DHT12(machine.Pin(int(pin)))
    d.measure()
    d.temperature()  # eg. 23 (??C)
    d.humidity()
    return {"temp": d.temperature(), "hum": d.humidity()}
def interruptTrigger(pin: machine.Pin):
    p = -1
    for key in g.pins:
        if g.pins[key] == pin:
            p = int(key)
    if p >= 0:
        o(p, pin.value(), None, _T)
    gc.collect()
  
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
                if (c == 'lt' and vo < va):
                    rsp = 'lt'
                if (c == 'gt' and vo > va):
                    rsp = 'gt'        
                if (c == 'ne' and vo != va):
                    rsp = 'ne'

                if (rsp != None):
                    mqtt.p(mqtt.tpfx()+'/scene/'+p,cmd[6])
                    _p = 'scene '+p+' set '+cmd[6]
                    print(_p)
                    sv['{}'.format(p)] =cmd[6]
                    ev.rcv(_p)
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
                    mqtt.p(mqtt.tpfx() +'/gpio/' + p, g.gpin(p) )    
            continue   
    gc.collect()
    return 'nok'

g.irqEvent(interruptTrigger)