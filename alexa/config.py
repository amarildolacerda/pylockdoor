from gc import collect
from time import ticks_diff, ticks_ms

from machine import Pin, unique_id
from ubinascii import hexlify

CFG_LABEL = 1
CFG_SSID = 2
CFG_PASS = 3
CFG_APSSID = 4
CFG_APPASS = 5

CFG_MQTTPREFIX = 6
CFG_MQTTNAME = 7
CFG_MQTTINTERNAL = 8
CFG_MQTTHOST = 9
CFG_MQTTUSER = 10
CFG_MQTTPASS = 11
CFG_MQTTPORT = 12
CFG_INTERVAL = 13
CFG_LED = 14
CFG_SLEEP = 15
CFG_LOCKED = 16
CFG_STYPE = 'stype'
CFG_EVENTS = 'scene'
CFG_CONDS = 'conds'
uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))

_N = None
_T = True
_F = False
_cf = 'c.json'
maxPins = 16
defineEsp32 = _F

#Pin Mode
PinOUT = 1
PinIN = 2
PinADC = 3

onoff = 7

inited = _F
ifconfig = None
_changed = _F
uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))
gp_trg = 101
gp_trg_tbl = 102
gpio_timeoff = 103
gpio_timeon = 104
gp_mde = 105


PINS = 0
IFCONFIG = 1
dados = {
  PINS:{},
  IFCONFIG:None
}

modes = ['none','out','in','adc']
_table = ['none','monostable','bistable']

timeOnOff = {}
mesh = 'mesh/'+uid
gpio = 'gpio'
def conf():
    return {
        CFG_SLEEP: 0,
        CFG_LED: 2,
        CFG_LOCKED: 0,
        CFG_LABEL:'Luz escritório',
        CFG_SSID : 'VIVOFIBRA-A360',
        CFG_PASS : '6C9FCEC12A', 
        CFG_APSSID: 'hm_{}'.format(uid),
        CFG_APPASS: '123456780',
        gp_mde: {},
        gp_trg: {},
        gp_trg_tbl: {},
        gpio_timeoff: {},
        gpio_timeon: {},
        CFG_EVENTS: {},
        CFG_CONDS: [],
        CFG_STYPE: {},
        CFG_MQTTHOST: 'broker.emqx.io',
        CFG_MQTTNAME: uid,
        CFG_MQTTPREFIX: mesh,
        CFG_MQTTPORT: 1883,
        CFG_MQTTUSER: uid,
        CFG_MQTTPASS: 'anonymous',
        CFG_MQTTINTERNAL: 10,
        CFG_INTERVAL: 0.3,
    }
config = conf()
def restore():
    import json as ujson
    global config
    try:
        cfg = {}
        with open(_cf, 'r') as f:
            cfg = ujson.load(f)
        config = conf()
        for item in config:  # pega os que faltam na configuracao
            if item in cfg:
                config[item] = cfg[item]
        cfg = None
        collect()        
    except:
        pass
def reset_factory():
    config = conf()
    save()
def save():
    #import json as ujson
    #with open(_cf, 'w') as f:
    #    ujson.dump(config, f)
    return "Saved"
def changed(bChanged):
    _changed = bChanged
def start():
    model('15')
    try:
        _changed = _F
        restore()
        inited = _T
    except:
        pass
def mdeTs(mode):
    return modes[mode]
def sToMde(smode):
    try:
        return modes.index(smode)
    except:
        return _N
def sMde(p: str, v):
    config[gp_mde][p] = sToMde(v)
    return v
def gMdes():
    return config[gp_mde]
def gMde(p: str):
    return config[gp_mde].get(p)
def tblToStr(t: int) -> str:
    return _table[t]
def strToTbl(t: str) -> int:
    try:
        return _table.index(t)
    except:
        return _N
def sTrg(p):
    i = str(p[1])
    config[gp_trg][i] = int(p[3])
    config[gp_mde][i] = PinIN
    config[gp_trg_tbl][i] = strToTbl(p[4])
def gTrg(p: str):
    return config[gp_trg].get(p)
def gTbl(p: str):
    return config[gp_trg_tbl].get(p)
def sToInt(p3, v):
    if (p3 in ['high', 'ON', 'on', '1']):
        return 1
    else: return 0
def checkTimeout(conn_lst, dif):
    try:
        d = ticks_diff(ticks_ms(), conn_lst)
        return (d > dif)
    except:
        return _F
def gstype(pin):
    return config[CFG_STYPE].get(pin)
def sstype(pin, stype):
    config[CFG_STYPE][pin] = stype
    return stype
def gateway(n):
    pass
gp_vlr = {}
interruptEvent = None
def led(v):
    pin = int(config['led'] or 255)
    if pin <= _maxPins:
        return
    Pin(pin, Pin.OUT).value(v)
def sEvent(p):
    try:
        event = p[1]
        cmd = p[2]
        pin = int(p[3])
        if cmd == 'trigger':
            config[CFG_EVENTS][event] = pin
            return 'trigged'
        if cmd == 'clear':
            config[CFG_EVENTS].pop(event)
            return 'cleaned'
        if cmd == 'set':
            dst = config[CFG_EVENTS][event]
            vlr = p[3]
            v = spin(dst, vlr)
            return v
    except Exception as e:
        print('{}: {}'.format(p, e))
    return config[CFG_EVENTS]
def trigg(p: str, v):
    try:
        t = gTrg(p)
        v = sToInt(v, v)
        print('trigger {} set {}'.format(t,v))
        if t != None:
            if (gTbl(p)) % 2 == 1:
                if v == 1:
                    spin(t, 1-gVlr(t),False,False)
            else:
                spin(t, v, False,False)
    except Exception as e:
        print('Error trigger:{} pin: {} '.format(e, p))
def spin(pin_: str, value, pers = False, doTrigg = True) -> str:
    global timeOnOff #,interruptEvent
    try:
        v = sToInt(value, value)
        p = initPin(str(pin_), Pin.OUT)
        p.value(v)
        if pers:
            sVlr(pin_, v)
#        if doTrigg:    
#           trigg(pin,value)
        print('gpio {} set {}'.format(pin_,value))   
        timeOnOff[pin_] = ticks_ms()
        #if doTrigg and interruptEvent:
        #   interruptEvent(p)
    except Exception as e:
        print('Error spin:{} pin: {} value: {} '.format(e, pin_, value))
    return str(value)
def gpin(p1: str) -> int:
    try:
        p = initPin(p1, Pin.OUT)
        print('gpio {} get -> {}'.format(p1,p.value()))
        return p.value()
    except Exception as e:
        print('{} {} {}'.format('gpin: ',p1, e))
def initPin(pin, tp):
    global dados,interruptEvent
    try:
        p = str(pin)
        if not p in dados[PINS].keys():
            dados[PINS][p] = Pin(int(pin), tp)
            if tp == Pin.IN or tp==Pin.OUT:
                dados[PINS][p].irq(trigger=Pin.IRQ_RISING,
                              handler=_doEvent)
        return dados[PINS][p]
    except Exception as e:
        print('{} {}'.format('initPin: ', e))
    return None
def _doEvent(x):
    print('doEvent {}'.format(x))
    global interruptEvent
    if interruptEvent: return interruptEvent(x)    
def irqEvent(proc):
    global interruptEvent
    interruptEvent = proc
    for p in config[gp_mde]:
        if gMde(p) == PinIN:
            initPin(p, Pin.IN)
def strToNum(v):
    try:
        f = float(v)
        if f > (255*255):
            return v
        return f
    except:
        try:
            f = int(v)
            return f
        except:
            pass
    return v
def sKey(p: str, v):
    config[p] = strToNum(v)
    return v
def gKey(p: str):
    return config[p]
def swt(_p: int):
    v = 1-gpin(_p)
    return spin(_p, v)
def sTmDly(p):
    v = 0
    try:
        v = strToNum(p[3])
        if v > 0 and v < 0.3:
            v = 0.3
    except Exception as e:
        print('{}'.format(e))
        v = None
    return v
def sTimeOn(p):
    config[gpio_timeon][p[1]] = sTmDly(p)
def sTimeOff(p):
    config[gpio_timeoff][p[1]] = sTmDly(p)
def model(md: str):
    if md == 'clear':
        config[gp_mde] = {}
        config[gp_trg] = {}
        config[gp_trg_tbl] = {}
        config[gpio_timeoff] = {}
        config[gpio_timeon] = {}
        return 'cleared'
    n = int(md)
    if n > 4:
        sTrg([gpio, '4',  'trigger', md, _table[2]])
        sMde(md, 'out')
        return sTimeOff([gpio, md, gpio_timeoff, 3600])
def gVlrs():
    return gp_vlr
def sVlr(p: str, v):
    gp_vlr[p] = strToNum(v)
    return v
def gVlr(p: str):
    try:
        v = gp_vlr.get(p)
        if (v == None):
            v = 0
        return v
    except:
        return 0
def gpioCond(cmd:str):
    s = cmd.split(' ')
    cmd = s[6][0]
    ss = '{},{},{},{},{},{},{}'.format(s[1], s[2], s[3],s[4],cmd,s[7],s[9])
    config[conds].append( ss )
    return config[conds]
def clearCond():
    config[conds] = []
    return 'OK'
def readFile(nome:str):
    with open(nome, 'r') as f:
        return f.read()


model(15)