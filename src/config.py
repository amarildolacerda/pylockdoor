
from time import ticks_diff, ticks_ms

from micropython import const

_N = None
_T = True
_F = False
_cf = 'config.json'
_maxPins = 16
_defineEsp32 = _F

uid = None
def _init():
  global uid  
  from machine import unique_id
  from ubinascii import hexlify
  uid = '{}'.format(hexlify(unique_id()).decode('utf-8'))
_init()

IFCONFIG = const(0)
PINS = const(1)
dados = {
   IFCONFIG:None,
   PINS : {}
}

trigger = 'tr'

# config
gp_mde = const('0')
gp_trg = const('1')
gpio_timeoff = const('2')
gpio_timeon = const('3')
gp_trg_tbl = const('4')
events = const('5')
pub = const('6')
# fim

PINOUT = const(1)
PININ = const(2)
PINADC = const(3)
modes = ['none','out','in','adc','pwm']
_table = ['none','monostable','bistable']
timeOnOff = {}
gpio = const('gpio')
mesh = None

def conf():
    global mesh
    import setup
    mesh = 'mesh/'+(setup.name or uid)
    return {
        'sleep': 0,
        'led': 255,
        'label':setup.label,
        'ssid':setup.ssids[0][0],
        'password':setup.ssids[0][1],
        'ap_ssid': '{}'.format(uid),
        'ap_password': '123456780',
        gp_mde: {},
        gp_trg: {},
        gp_trg_tbl: {},
        gpio_timeoff: {},
        gpio_timeon: {},
        events:{},
        'stype': {},
        'mqtt_host': setup.mqtt_host,
        'mqtt_name': uid,
        'mqtt_port': setup.mqtt_port,
        'mqtt_user': uid,
        'mqtt_password': 'anonymous',
        'mqtt_interval': 60,
        'mqtt_prefix': mesh,
        'interval': setup.interval,
        'auto-pin' : setup.auto_pin,
        pub:{}
    }
config = conf()
def restore():
        from json import load
        global config
        cfg = {}
        try:
          with open(_cf, 'r') as f:
            cfg = load(f)
        except: cfg = {}
        config = conf()
        from setup import set_model, start
        if set_model:
           model(set_model)
        start()   
        for item in cfg: 
                config[item] = cfg[item]
def reset_factory():
    global config
    config = conf()
    save()
def save():
    cfg = conf()
    rst = {}
    for k in cfg.keys():
       if gKey(k)!=cfg[k]:
        rst[k]=config[k]
    from json import dump
    with open(_cf, 'w') as f:
        dump(rst, f)
    return "Saved"
def start():
        restore()
def mdeTs(mode):
    return modes[mode]
def sToMde(smode):
    try:
        return modes.index(smode)
    except:
        return _N
def sMde(p: str, v):
    gKey(gp_mde)[p] = sToMde(v)
    return v
def gMdes():
    return gKey(gp_mde)
def gMde(p: str):
    return gKey(gp_mde).get(p)
def tblToStr(t: int) -> str:
    return _table[t]
def strToTbl(t: str) -> int:
    try:
        return _table.index(t)
    except:
        return _N
def sTrg(p):
    i = str(p[1])
    gKey(gp_trg)[i] = int(p[3])
    gKey(gp_mde)[i] = PININ
    gKey(gp_trg_tbl)[i] = strToTbl(p[4])
def gTrg(p: str):
    return gKey(gp_trg).get(p)
def gTbl(p: str):
    return gKey(gp_trg_tbl).get(p)

def sToInt(p3, v):
    try:
     if (p3 in ['high', 'on', '1']):
        v = 1
     if (p3 in ['low', 'off', '0']):
        v = 0
     return v   
    except:
      raise TypeError('sToInt {} {}'.format(p3,v))
    return int(v)
 
def checkTimeout(conn_lst, dif):
    try:
        d = ticks_diff(ticks_ms(), conn_lst)
        return (d > dif)
    except:
        return _F
def gstype(pin):
    return gKey('stype').get(pin)
def sstype(pin, stype):
    gKey('stype')[pin] = stype
    return stype
gp_vlr = {}
interruptEvent = None
def led(v):
    pin = int(gKey('led') or 255)
    if pin <= _maxPins:
        return
    spin(pin,v)
 
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
        raise TypeError('E tr:{} pin:{} '.format(e, p))

def strigg(p: str, v):
        t = gTrg(p)
        v = sToInt(v, v)
        return spin(t or p, v)
def gtrigg(p: str):
        t = gTrg(p)
        return gpin(t or p)
def spin(p1: str, value, pers = True) -> str:
    x = sToInt(p1,p1)
    s1 = str(x)
    try:
        if x == 0: #ADC
            return 0
        v = sToInt(value, value)
        p = initPin(s1, PINOUT)
        p.value(v)
        trigPub(p1,v)
        print(p1,v)
        try:
            if pers: 
              sVlr(s1, v)
            timeOnOff[s1] = ticks_ms()
        except:
            pass
    except Exception as e:
        raise TypeError('E spin:{} p:{} v:{}'.format(e, s1, value))
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
        raise TypeError('{} {} {}'.format('gpin: ',p1, e))
def initPin(p1, tp):
    p = str(p1)
    try:
        x = sToInt(p,p)
        from machine import Pin
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
        raise TypeError('{} {} {}'.format('initPin ',p, e))
def irqEvent(proc):
    global interruptEvent
    interruptEvent = proc
    for p in gKey(gp_mde):
        if gMde(p) == PININ:
            initPin(p, PININ)
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
            return v    
def sKey(p: str, v):
    config[p]=strToNum(v)  
    return v
def gKey(p: str):
    return config[p]
def swt(_p: int):
    v = 1-gpin(_p)
    return spin(_p, v)
def sTmDly(p):
        v = 0
        v = strToNum(p[3])
        if v > 0 and v < 0.3:
            v = 0.3
def sTimeOn(p):
    gKey(gpio_timeon)[p[1]] = sTmDly(p)
def sTimeOff(p):
    gKey(gpio_timeoff)[p[1]] = sTmDly(p)
def model(md: str):
    if md == 'clear':
        sKey(gp_mde, {})
        sKey(gp_trg,  {})
        sKey(gp_trg_tbl, {})
        sKey(gpio_timeoff, {})
        sKey(gpio_timeon, {})
        return 'cleared'
    n = int(md)
    if n > 4:
        sTrg([gpio, gKey('auto-pin'),  trigger, md, _table[2]])
        sMde(md, 'out')
        return sTimeOff([gpio, md, gpio_timeoff, 3600*5])
def gVlrs():
    return gp_vlr
def sVlr(p: str, v):
    gp_vlr[p] = strToNum(v)
    global  pinChanged
    pinChanged = True
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
def sEvent(p):
    try:
        event = p[1]
        cmd = p[2]
        pin = sToInt( p[3], p[3] )
        if cmd == 'trigger':
            gKey(events)[event] = pin
            return 'trigged'
        if cmd == 'clear':
            gKey(events).pop(event)
            return 'cleaned'
        if cmd == 'set':
            if event in gKey(events).keys():
                v = spin(gKey(events)[event], pin)
                return v
    except:
        raise TypeError( 'inválido '+p)    

def trigPub(pin,v):
    for it in gKey(pub).keys():
        if str(gKey(pub)[it])==pin:
            from mqtt import publish
            publish(it,v)
            return v

def sPub(p):  #pub 0 trigger scene/noite     
        cmd = p[1]
        if cmd == 'clear':
            return sKey(pub,{})
        tp = p[3]
        pin = sToInt( p[1], p[1] )
        if p[2]=='trigger':
            gKey(pub)[tp] = pin
            return gKey(pub)
        raise TypeError('invalido '+p)