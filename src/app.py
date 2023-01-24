
from machine import Timer, reset

import mqtt as mq

_N = None
_T = True
_F = False
try:
    wlan = _N
    def connectWifi():
        global wlan
        from wifimgr import get_connection, isconnected
        if not wlan:
            from config import IFCONFIG, dados
            wlan = get_connection()
            dados[IFCONFIG] = wlan.ifconfig()
        return isconnected()
    def mqtt_rcv(_t, _p):
        t = _t.decode('utf-8')
        p = _p.decode('utf-8')
        try:
            from command8266 import tpRcv
            return tpRcv(t,p)
        except OSError as e:
            mq.p('Invalid', 0)
            
    def mqttConnect(ip=''):
        try:
            from config import gKey, uid
            mq.topic = mq.tpfx()
            mq.host = gKey('mqtt_host')
            mq.create(uid, gKey('mqtt_host'),
                        gKey('mqtt_user'), gKey('mqtt_password'))
            mq.callback(mqtt_rcv)
            mq.cnt()
            mq.sb(mq.topic_command_in())
            mq.p(mq.tpfx()+'/ip', ip)
        except OSError as e:
            p(e)
    inLoop = False
    def eventLoop(v):
        from event import cv 
        cv(v)
        
    def loop(b=None):
        global inLoop
        if inLoop: return
        try:
          mq.disp()
          try:  
            inLoop = True
            from wifimgr import timerFeed, timerReset
            if wlan.isconnected():
                try:
                    timerFeed()
                    mq.check_msg()
                    eventLoop(mq.connected)
                    mq.sendStatus()
                except:
                    mqttConnect(wlan.ifconfig()[0])
            else: eventLoop(False)
          finally:
            timerReset(True)
            inLoop = False  
            from config import savePins
            savePins()
          return true  
        except Exception as e:
            pass
    timer = None
    def init():
        global timer
        from config import start as config_start
        config_start()
        from event import init as ev_init
        ev_init()

    def doTelnetEvent(server, addr,message):
        from command8266 import cmmd    
        rsp = cmmd(message[:-2].decode('utf-8'))
        if rsp:
           server.write(rsp)
           server.write('\r\n')
        return False

    def srvrun(ip,lp):
        import server as services
        telnet = services.TelnetServer(7777)
        telnet.listen(doTelnetEvent)
        import broadcast
        web = services.WebServer("", 8080)
        web.listen(broadcast.http)
        from config import restorePins
        restorePins()
        udp = services.Broadcast("",lp)
        udp.listen(broadcast.discovery)
        
    def bind():
            global  wlan
            if not connectWifi():
               reset()
            try:
                from ntp import settime
                settime()
            except: pass
            mqttConnect(wlan.ifconfig()[0])
    def run():
        try:
            init()
            bind()
            srvrun(wlan.ifconfig()[0],loop)
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            print(e)
        finally:
            mq.dcnt()
except Exception as e:
    print(e)
    pass