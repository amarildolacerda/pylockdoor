import gc
import machine
import time
import config as g
import mqtt
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
# check if the device woke from a deep sleep
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('iniciando deep sleep')
# set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, n*1000)
# put the device to sleep
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
    d.temperature()  # eg. 23 (°C)
    d.humidity()
    return {"temp": d.temperature(), "hum": d.humidity()}
def getDht12(pin: str):
    import dht
    d = dht.DHT12(machine.Pin(int(pin)))
    d.measure()
    d.temperature()  # eg. 23 (°C)
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

def localTrig(i: str,stype: str,value: int):
  # if adc 0 lt 500 then trigger 15 to 1
    for j in g.config[g.conds]:
        cmd = j.split(',',6)
        c = cmd[2]
        a = int(cmd[3])
        p = cmd[4]
        v = g.strToNum(cmd[5])
        vo = g.strToNum(g.gpin(p))
        print(j,i,c,a,p,v,vo,stype,value)
        if (cmd[0]==stype) and (cmd[1]==i and (vo!=v)):  
            rsp = None;
            if (c=='lt') and (value < a):
                rsp = g.spin(p, v)
            elif (c=='gt') and (value > a):
                rsp = g.spin(p, v)
            elif (c=='eq') and (value == a):
                rsp = g.spin(p,v)
            if (rsp != None):
                mqtt.p(mqtt.tpfx() +'/{}'.format(stype )+'/' + p, g.gpin(p) )    
            continue   
    gc.collect()
    return 'nok'

g.irqEvent(interruptTrigger)