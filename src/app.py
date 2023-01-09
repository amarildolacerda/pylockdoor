from gc import collect, mem_alloc, mem_free
from time import sleep

from machine import DEEPSLEEP_RESET, Timer, idle, reset, reset_cause
from micropython import const

import mqtt
import wifimgr
from alexaserver import AlexaRun

_N = const(None)
_T = const(True)
_F = const(False)
try:
    import gc

    import network

    import command8266 as cm
    import config as g
    import configshow as show
    import event as ev
    import ntp
    import server
    wlan = _N
    telnet = _N
    def connectWifi():
        global wlan
        if not wlan:
            wlan = wifimgr.get_connection()
            g.ifconfig = wlan.ifconfig()
        return wlan.isconnected()
    def mqtt_rcv(_t, _p):
        t = _t.decode('utf-8')
        p = _p.decode('utf-8')
        try:
            cm.tpRcv(t,p)
        except OSError as e:
            mqtt.p('Invalid', 0)
            pass
    def mqttConnect(ip=''):
        try:
            mqtt.topic = mqtt.tpfx()
            mqtt.host = g.config['mqtt_host']
            mqtt.create(g.uid, g.config['mqtt_host'],
                        g.config['mqtt_user'], g.config['mqtt_password'])
            mqtt.callback(mqtt_rcv)
            mqtt.cnt()
            mqtt.sb(mqtt.topic_command_in())
            mqtt.p(mqtt.tpfx()+'/ip', ip)
        except OSError as e:
            p(e)
    def loop():
        mqtt.disp()
        while _T:
            try:
                gpioLoopCallback()
            except:
                pass
    errCount = 0
    inLoop = False
    def gpioLoopCallback():
        global errCount, inLoop
        if inLoop: return
        try:
          try:  
            inLoop = True
            if wlan.isconnected():
                try:
                    wifimgr.timerFeed()
                    mqtt.check_msg()
                    ev.cv(mqtt.connected)
                    if mqtt.connected:
                        mqtt.sendStatus()
                        errCount = 0
                except:
                    errCount = errCount + 1
                    if errCount > 10:
                        reset()
                    mqttConnect(wlan.ifconfig()[0])
            else: ev.cv(False)
          finally:
            wifimgr.timerReset(True)
            inLoop = False    
            collect()
            idle()
        except Exception as e:
            pass
    def telnetCallback(data):
        return cm.rcv(data)
    def p(x):
        print(x)
    def timerLoop(x):
        gpioLoopCallback()
        return True
    timer = None
    def init():
        global timer
        ev.init()
        g.start()
        timer = Timer(-1)
        timer.init(mode=Timer.PERIODIC,
                   period=1000, callback=timerLoop)
    def bind():
            global telnet, wlan
            if not connectWifi():
               reset()
            try: ntp.settime()
            except: pass
            mqttConnect(wlan.ifconfig()[0])
            if (g.config['locked'] == 0):
                collect()
                telnet = server.TCPServer()
                telnet.callback(telnetCallback)
                telnet.feed(gpioLoopCallback)
                telnet.start()
            wifimgr.start(8080)    
            AlexaRun(wlan.ifconfig()[0], timerLoop)
    def run():
        global telnet
        if reset_cause() == DEEPSLEEP_RESET:
            ev.setSleep(-1)
        try:
            init()
            bind()
            loop()
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            print(e)
            reset()
        finally:
            if (telnet is not None):
                telnet.close()
            mqtt.dcnt()
            try:
                wlan.close()
            except:
                pass    
except Exception as e:
    print(e)
    sleep(30)
    reset()