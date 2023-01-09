from time import ticks_diff, ticks_ms

from machine import Pin, unique_id
from ubinascii import hexlify

_N = None
_T = True
_F = False
_cf = 'config.json'
try:
    import esp32
    _maxPins = 40
    defineEsp32 = _T
except:
    _maxPins = 16
    defineEsp32 = _F
constPinOUT = 1
constPinIN = 2
onoff = 7
inited = _F
ifconfig = None
_changed = _F
uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))
pins = {}
gp = 'g_'
trigger = 'tr'
gp_trg = gp+trigger
gp_trg_tbl = gp_trg+'_tab'
gpio_timeoff = 'toff'
gpio_timeon = 'ton'
gp_mde = gp+'mode'
events = 'scene'
modes = ['none','out','in','adc','pwm','dht11','dht12']
_table = ['none','monostable_NC','bistable_NC','monostable_NO', 'bistable_NO']
timeOnOff = {}
mesh = 'ihomeware/'+uid
gpio = 'gpio'
conds = 'conds'
def conf():
    
    return {
        'sleep': 0,
        'led': 255,
        'locked': 0,
        'ssid': 'micasa',
        'password': '3938373635',
        'ap_ssid': 'hm_{}'.format(uid),
        'ap_password': '123456780',
        gp_mde: {},
        gp_trg: {},
        gp_trg_tbl: {},
        gpio_timeoff: {},
        gpio_timeon: {},
        events: {},
        conds:[],
        'stype': {},
        'mqtt_host': 'broker.emqx.io',
        'mqtt_name': uid,
        'mqtt_port': 1883,
        'mqtt_user': uid,
        'mqtt_password': 'anonymous',
        'mqtt_interval': 60,
        'mqtt_prefix': mesh,
        'interval': 0.3,
        # 'sleep':0.0,
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
    except:
        pass
def reset_factory():
    config = conf()
    save()
def save():
    import json as ujson
    with open(_cf, 'w') as f:
        ujson.dump(config, f)
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
    config[gp_mde][i] = constPinIN
    config[gp_trg_tbl][i] = strToTbl(p[4])
def gTrg(p: str):
    return config[gp_trg].get(p)
def gTbl(p: str):
    return config[gp_trg_tbl].get(p)
def sToInt(p3, v):
    if (p3 in ['high', 'ON', 'on', '1']):
        v = 1
    if (p3 in ['low', 'OFF', 'off', '0']):
        v = 0
    return v
def checkTimeout(conn_lst, dif):
    try:
        d = ticks_diff(ticks_ms(), conn_lst)
        return (d > dif)
    except:
        return _F
def gstype(pin):
    return config['stype'].get(pin)
def sstype(pin, stype):
    config['stype'][pin] = stype
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
            config[events][event] = pin
            return 'trigged'
        if cmd == 'clear':
            config[events].pop(event)
            return 'cleaned'
        if cmd == 'set':
            dst = config[events][event]
            vlr = p[3]
            v = spin(dst, vlr)
            return v
    except Exception as e:
        print('{}: {}'.format(p, e))
    return config[events]
def trigg(p: str, v):
    try:
        t = gTrg(p)
        v = sToInt(v, v)
        if t != None:
            if (gTbl(p)) % 2 == 1:
                if v == 1:
                    spin(t, 1-gVlr(t))
            else:
                spin(t, v)
    except Exception as e:
        print('Error trigger:{} pin: {} '.format(e, p))
def spin(pin: str, value, pers = False) -> str:
    global timeOnOff
    try:
        v = sToInt(value, value)
        p = initPin(pin, Pin.OUT)
        p.value(v)
        if pers:
            sVlr(pin, v)
        timeOnOff[pin] = ticks_ms()
    except Exception as e:
        print('Error spin:{} pin: {} value: {} '.format(e, pin, value))
    return str(value)
def gpin(p1: str) -> int:
    try:
        p = initPin(p1, Pin.OUT)
        return p.value()
    except Exception as e:
        print('{} {} {}'.format('gpin: ',p1, e))
def initPin(pin: str, tp):
    global pins
    try:
        if not pin in pins.keys():
            pins[pin] = Pin(int(pin), tp)
            if tp == Pin.IN:
                pins[pin].irq(trigger=Pin.IRQ_RISING,
                              handler=interruptEvent)
        return pins[pin]
    except Exception as e:
        print('{} {}'.format('initPin: ', e))
    return None
def irqEvent(proc):
    global interruptEvent
    interruptEvent = proc
    for p in config[gp_mde]:
        if gMde(p) == constPinIN:
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
        sTrg([gpio, '4',  trigger, md, _table[2]])
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
