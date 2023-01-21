from time import ticks_diff, ticks_ms

from machine import ADC, Pin, unique_id
from micropython import const

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

from ubinascii import hexlify

uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))



IFCONFIG = const(0)
PINS = const(1)
dados = {
   IFCONFIG:None,
   PINS : {}
}

gp = 'g_'
trigger = 'tr'
gp_trg = const('1')
gp_trg_tbl = const('4')
gpio_timeoff = const('2')
gpio_timeon = const('3')
gp_mde = const('0')
PINOUT = const(1)
PININ = const(2)
PINADC = const(3)
modes = ['none','out','in','adc']
_table = ['none','monostable','bistable']
timeOnOff = {}
gpio = const('gpio')
import setup

mesh = 'mesh/'+(setup.name or uid)

def conf():
    return {
        'sleep': 0,
        'led': 255,
        'label':setup.label,
        'ssid':setup.ssid,
        'password':setup.password,
        'ap_ssid': 'hm_{}'.format(uid),
        'ap_password': '123456780',
        gp_mde: {},
        gp_trg: {},
        gp_trg_tbl: {},
        gpio_timeoff: {},
        gpio_timeon: {},
        'stype': {},
        'mqtt_host': setup.mqtt_host,
        'mqtt_name': uid,
        'mqtt_port': setup.mqtt_port,
        'mqtt_user': uid,
        'mqtt_password': 'anonymous',
        'mqtt_interval': 60,
        'mqtt_prefix': mesh,
        'interval': 0.3,
        'auto-pin' : setup.auto_pin,
    }
config = conf()
def restore():
    from json import load
    global config
    try:
        cfg = {}
        try:
          with open(_cf, 'r') as f:
            cfg = load(f)
        except: cfg = {}    
        config = conf()
        model(setup.relay_pin)
        for item in cfg:  # pega os que faltam na configuracao
                config[item] = cfg[item]
        print(config)        
    except:
        pass
def reset_factory():
    config = conf()
    save()
def save():
    cfg = conf()
    rst = {}
    for k in cfg.keys():
       if config[k]!=cfg[k]:
        rst[k]=config[k]
    from json import dump
    with open(_cf, 'w') as f:
        dump(rst, f)
    return "Saved"
def start():
    try:
        restore()
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
    config[gp_mde][i] = PININ
    config[gp_trg_tbl][i] = strToTbl(p[4])
def gTrg(p: str):
    return config[gp_trg].get(p)
def gTbl(p: str):
    return config[gp_trg_tbl].get(p)

def sToInt(p3, v):
    try:
     if (p3 in ['high', 'ON', 'on', '1']):
        v = 1
     if (p3 in ['low', 'OFF', 'off', '0']):
        v = 0
     return v   
    except:
      print('sToInt',p3,v)
    return int(v)
 
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
 
def trigg(p: str, v):
    try:
        t = gTrg(p)
        v = sToInt(v, v)
        if t != None:
            old =gpin(t)
            if (gTbl(p)) == 2:
                if v == 1:
                    spin(t, 1-old)
            else:
                spin(t, v)
    except Exception as e:
        print('E tr:{} pin:{} '.format(e, p))

def strigg(p: str, v):
        t = gTrg(p)
        v = sToInt(v, v)
        if t != None:
            initPin(t,Pin.OUT)
            return spin(t, v)
        else:
            return spin(p, v)

def gtrigg(p: str):
        t = gTrg(p)
        if t != None:
            return gpin(t)
        else:
            return gpin(p)


def spin(p1: str, value, pers = False) -> str:
    global timeOnOff
    x = sToInt(p1,p1)
    s1 = str(x)
    try:
        if x == 0: #ADC
            return 0
        v = sToInt(value, value)
        p = initPin(s1, PINOUT)
        p.value(v)
        try:
            if pers:
                sVlr(s1, v)
            timeOnOff[s1] = ticks_ms()
        except:
            pass
    except Exception as e:
        print('E spin:{} pin: {} value: {} '.format(e, s1, value))
    return value
def gpin(p1: str) -> int:
    try:
        x = sToInt(p1,p1)
        if x == 0: 
            from machine import ADC
            return ADC(x).read()
        p = initPin(p1, PININ)
        return p.value()
    except Exception as e:
        print('{} {} {}'.format('gpin: ',p1, e))
       
def initPin(p1, tp):
    p = str(p1)
    try:
        x = sToInt(p,p)
        if tp == PINOUT:
            return Pin(int(x),Pin.OUT)
        global dados
        if not p in dados[PINS].keys():
                r = Pin(int(x), Pin.IN)
                if tp == PININ:
                  r.irq(trigger=Pin.IRQ_RISING,
                                handler=interruptEvent)
                dados[PINS][p] = r
        return dados[PINS][p] or Pin(int(x),Pin.OUT)
    except Exception as e:
        print('{} {} {}'.format('initPin ',p, e))
def irqEvent(proc):
    global interruptEvent
    interruptEvent = proc
    for p in config[gp_mde]:
        if gMde(p) == PININ:
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
        sTrg([gpio, config['auto-pin'],  trigger, md, _table[2]])
        sMde(md, 'out')
        return sTimeOff([gpio, md, gpio_timeoff, 3600*5])
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
def readFile(nome:str):
    with   open(nome, 'r')  as f:
        return f.read()
