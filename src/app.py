
from machine import Timer, reset

import mqtt as m

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
    def mq_rcv(_t, _p):
        t = _t.decode('utf-8')
        p = _p.decode('utf-8')
        try:
            from command8266 import tpRcv
            return tpRcv(t,p)
        except OSError as e:
            mqp('Invalid', 0)
            
    def mqConnect(ip=''):
        try:
            from config import gKey, uid
            m.topic = m.tpfx()
            m.host = gKey('mqtt_host')
            m.create(uid, gKey('mqtt_host'),
                        gKey('mqtt_user'), gKey('mqtt_password'))
            m.callback(mqtt_rcv)
            m.cnt()
            m.sb(m.topic_command_in())
            m.p(m.tpfx()+'/ip', ip)
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
          disp()
          try:  
            inLoop = True
            from wifimgr import timerFeed, timerReset
            if wlan.isconnected():
                try:
                    timerFeed()
                    check_msg()
                    eventLoop(connected)
                    sendStatus()
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
    def tn(server, addr,message):
        from command8266 import cmmd    
        rsp = cmmd(message[:-2].decode('utf-8'))
        if rsp:
           server.write(rsp)
           server.write('\r\n')
        return False
    def srvrun(ip,lp):
        import server as services
        telnet = services.TelnetServer(7777)
        telnet.listen(tn)
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
            reset()
        finally:
            from mqtt import dcnt
            dcnt()
            try:
                wlan.close()
            except:
                pass    
except Exception as e:
    print(e)
    reset()