
from machine import Timer, reset

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
            from mqtt import p as mqttp
            mqttp('Invalid', 0)
            
    def mqttConnect(ip=''):
        try:
            import mqtt
            from config import config, uid
            mqtt.topic = mqtt.tpfx()
            mqtt.host = config['mqtt_host']
            mqtt.create(uid, config['mqtt_host'],
                        config['mqtt_user'], config['mqtt_password'])
            mqtt.callback(mqtt_rcv)
            mqtt.cnt()
            mqtt.sb(mqtt.topic_command_in())
            mqtt.p(mqtt.tpfx()+'/ip', ip)
        except OSError as e:
            p(e)
    inLoop = False
    def eventLoop(v):
        from event import cv 
        cv(v)
        
    def gpioLoopCallback(b=None):
        global inLoop
        if inLoop: return
        try:
          from mqtt import disp
          disp()
          try:  
            inLoop = True
            from wifimgr import timerFeed, timerReset
            if wlan.isconnected():
                try:
                    timerFeed()
                    from mqtt import check_msg, connected, sendStatus
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

    def doTelnetEvent(server, addr,message):
        s = message.split(' ')
        if s in ['quit','exit','reset']:
            server.close()
            reset()
            return True
        from command8266 import cmmd    
        rsp = cmmd(message[:-2].decode('utf-8'))
        if rsp:
           server.write(rsp)
           server.write('\r\n')
        return False

    def services_run(ip,timeloop):
        import server as services
        telnet = services.TelnetServer(7777)
        telnet.listen(doTelnetEvent)
        import broadcast
        web = services.WebServer("", 8080)
        web.listen(broadcast.http)
        from config import restorePins
        restorePins()
        udp = services.Broadcast(callbackFn=timeloop)
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
            timer = Timer(-1)
            timer.init(mode=Timer.PERIODIC,
                   period=500, callback=gpioLoopCallback)
            services_run(wlan.ifconfig()[0],gpioLoopCallback)

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