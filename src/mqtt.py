from time import ticks_diff, ticks_ms

from machine import reset

import config as g

_N = None
_T = True
_F = False
mq = _N
host = ""
ssid = ""
connected = _F
started_in = ticks_ms()
def hostname():
    return g.config['ap_ssid']
def deviceId():
    return g.uid
def interval():
    return g.config['mqtt_interval']
def tpfx():
    return g.config['mqtt_prefix']
def trsp(response='/response'):
    return tpfx()+response
def topic_topology():
    return tpfx()+'/topology'
def topic_status():
    return tpfx()+'/status'
def tCmdOut():
    return tpfx()+'/gpio'
def topic_command_in():
    return g.config['mqtt_prefix']+'/in'
def topic_alive():
    return tpfx().split('/')[0]+'/alive'    
def debug(txt):
    g.debug(txt)
def create(client_id, mqtt_server, mqtt_user, mqtt_password):
    global mq
    if (mq != _N):
        return mq
    from umqtt_simple import MQTTClient
    mq = MQTTClient(client_id, mqtt_server, 0, mqtt_user,mqtt_password)
    return mq
usnd = ticks_ms()
mqttResetCount = 0
def sendStatus(force=False):
    global usnd, mqttResetCount
    try:
        if (mq == _N):
            return
        d = ticks_diff(ticks_ms(), usnd)
        n = interval()
        if (not force) and (d < (n or 15)*1000):
            return
        usnd = ticks_ms()
        global host
        from configshow import show
        rsp = p(topic_topology(), show(), 0)
        mqttResetCount += (1-rsp)
        #if (mqttResetCount > 0):
            #cnt()
            #reset()
        if g.defineEsp32:
            p(tpfx()+'/sensor/temp',
              str(round((esp32.raw_temperature() - 32) / 1.8, 1)), 1)
    except:
        pass
def sdPinRsp(pin, sValue, aRetained=0):
    if sValue == _N:
        return
    p((tpfx()+"/out/status/{}").format(pin), str(sValue), aRetained)
def sdRsp(sValue, aRetained=0, response='/response'):
    if sValue == _N:
        return
    usnd = ticks_ms()
    p(trsp(response), str(sValue), aRetained)
def account(account):
    send('account', account)
def p(t, p, aRetained=0):
    global mqttResetCount
    from commandutils import now
    print(now(), t, ':', p)
    try:
        if mq != _N:
            mq.publish(t, str(p), aRetained)
            mqttResetCount = 0
            return 1
        return 0  # sucesso
    except Exception as e:
        print('mqtt: {}'.format(e))
        return 0  # falhou
def send(aTopic, aMessage):
    p(tpfx()+'/'+aTopic, aMessage)
def error(aMessage):
    send('error', aMessage or '?')    
def sdOut(p, v):
    p(tCmdOut()+'/0', 'x')
def sb(aSubTopic):
    if mq != _N:
        mq.subscribe(aSubTopic)
        mq.subscribe(topic_alive())

def callback(aCallback):
    if mq != _N:
        mq.set_callback(aCallback)
def check_msg():
    if mq != _N:
        mq.check_msg()
def cnt():
    if mq != _N:
        mq.connect()
        p(topic_status(), 'online', 0)
        sendStatus(True)
        global connected
        connected = _T
def disp():
    for i in g.config[g.gp_mde]:
        x = g.gstype(str(i))
        if (x != None):
            p(('{}/type/{}').format(tpfx(), i), x, 0)
def dcnt():
    if mq != _N:
        p(topic_status(), 'offline', 0)
        mq.disconnect()
        global connected
        connected = _F
