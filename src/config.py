from time import ticks_diff, ticks_ms

from machine import Pin, unique_id

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
PinOUT = 1
PinIN = 2

from ubinascii import hexlify

uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))



IFCONFIG = 0
PINS = 1
dados = {
   IFCONFIG:None,
   PINS : {}
}

gp = 'g_'
trigger = 'tr'
gp_trg = '1'
gp_trg_tbl = '4'
gpio_timeoff = '2'
gpio_timeon = '3'
gp_mde = '0'
modes = ['none','out','in','adc']
_table = ['none','monostable','bistable']
timeOnOff = {}
gpio = 'gpio'
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
        'mqtt_interval': 30,
        'mqtt_prefix': mesh,
        'interval': 0.3,
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
        for item in cfg:  # pega os que faltam na configuracao
                config[item] = cfg[item]
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
    if setup.relay_pin:
        model(setup.relay_pin)
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
    config[gp_mde][i] = PinIN
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

def spin(pin: str, value, pers = False) -> str:
    global timeOnOff
    try:
        print('spin')
        v = sToInt(value, value)
        p = initPin(pin, Pin.IN)
        p.value(v)
        print(p,v)
        if pers:
            sVlr(pin, v)
        timeOnOff[pin] = ticks_ms()
        print('timeonoff')
    except Exception as e:
        print('E spin:{} pin: {} value: {} '.format(e, pin, value))
    return value
def gpin(p1: str) -> int:
    try:
        p = initPin(p1, Pin.IN)
        return p.value()
    except Exception as e:
        print('{} {} {}'.format('gpin: ',p1, e))
def initPin(pin: str, tp):
    global dados
    try:
        if not pin in dados[PINS].keys():
            dados[PINS][pin] = Pin(int(pin), tp)
            if tp == Pin.IN:
                dados[PINS][pin].irq(trigger=Pin.IRQ_RISING,
                              handler=interruptEvent)
        return dados[PINS][pin]
    except Exception as e:
        print('{} {}'.format('initPin: ', e))
    return None
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
def readFile(nome:str):
    with   open(nome, 'r')  as f:
        return f.read()
