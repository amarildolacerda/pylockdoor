from time import ticks_diff, ticks_ms

from machine import reset

from config import gKey as k
from config import gp_mde, gstype, uid

_N = None
_T = True
_F = False
mq = _N
host = ""
ssid = ""
connected = _F
started_in = ticks_ms()
def tpfx():
    return k('mqtt_prefix')
def trsp(response='/response'):
    return tpfx()+response
def topic_topology():
    return tpfx()+'/topology'
def topic_status():
    return tpfx()+'/status'
def tCmdOut():
    return tpfx()+'/gpio'
def topic_command_in():
    return k('mqtt_prefix')+'/in'
def create(client_id, mqtt_server, mqtt_user, mqtt_password):
    global mq
    if (mq != _N): return mq
    from umqtt_simple import MQTTClient
    mq = MQTTClient(client_id, mqtt_server, 0, mqtt_user,mqtt_password)
    return mq
usnd = ticks_ms()
def sendStatus(force=False):
        global usnd
        d = ticks_diff(ticks_ms(), usnd)
        n = k('mqtt_interval')
        if (not force) and (d < (n or 15)*1000):
            return
        usnd = ticks_ms()
        from configshow import show
        return p(topic_topology(), show(), 0)
def sdPinRsp(pin, sValue, aRetained=0):
    return p((tpfx()+"/out/status/{}").format(pin), str(sValue), aRetained)
def sdRsp(sValue, aRetained=0, response='/response'):
    if sValue == _N:
        return
    usnd = ticks_ms()
    return p(trsp(response), str(sValue), aRetained)
def p(t, p, aRetained=0):
    from commandutils import now
    print(now(), t, ':', p)
    try:
            mq.publish(t, str(p), aRetained)
            return 1
    except Exception as e:
        msg = str(e)
        print('p->',msg)
        if msg.find('UNREACH')>0 or msg.find('CONN')>0:
           cnt(False)
        return 0  # falhou
def send(aTopic, aMessage):
    return p(tpfx()+'/'+aTopic, aMessage)
def publish(tp,msg):
    return p('{}/{}'.format(tpfx().split('/')[0],tp),msg)    
def error(aMessage):
    send('error', aMessage or '?')    
def sb(aSubTopic):
        mq.subscribe(aSubTopic)
        mq.subscribe( '{}/scene/+'.format(tpfx().split('/')[0]))
def callback(aCallback):
        mq.set_callback(aCallback)
def check_msg():
        mq.check_msg()
def cnt(notify=True):
        mq.connect()
        if notify:
          p(topic_status(), 'online', 0)
          sendStatus(True)
        global connected,mqttResetCount
        connected = _T
def disp():
    for i in k(gp_mde):
        x = gstype(str(i))
        if (x != None):
            p(('{}/type/{}').format(tpfx(), i), x, 0)
def dcnt(notify=True):
   try: 
        if notify:
          p(topic_status(), 'offline', 0)
        mq.disconnect()
        global connected
        connected = _F
   except:
        pass