from gc import collect, mem_alloc, mem_free
from time import sleep

from machine import Timer, idle, reset, reset_cause

from mqtt import p as mqttp

_N = None
_T = True
_F = False
try:
    import config as g
    wlan = _N
    def connectWifi():
        global wlan
        from wifimgr import get_connection, isconnected
        if not wlan:
            wlan = get_connection()
            g.dados[g.IFCONFIG] = wlan.ifconfig()
        return isconnected()
    def mqtt_rcv(_t, _p):
        t = _t.decode('utf-8')
        p = _p.decode('utf-8')
        try:
            from command8266 import tpRcv
            tpRcv(t,p)
        except OSError as e:
            mqttp('Invalid', 0)
            pass
    def mqttConnect(ip=''):
        try:
            import mqtt
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
        while _T:
            try:
                gpioLoopCallback()
            except:
                pass
    errCount = 0
    inLoop = False
    def eventLoop(v):
        from event import cv 
        cv(v)
        pass
    def gpioLoopCallback():
        global errCount, inLoop
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
                    if connected:
                        sendStatus()
                        errCount = 0
                except:
                    errCount = errCount + 1
                    if errCount > 10:
                        reset()
                    mqttConnect(wlan.ifconfig()[0])
            else: eventLoop(False)
          finally:
            timerReset(True)
            inLoop = False    
            collect()
            sleep(0.05)
        except Exception as e:
            pass
    def timerLoop(x):
        gpioLoopCallback()
        return True
    timer = None
    def init():
        global timer
        from event import init as ev_init 
        ev_init()
        g.start()

    def doTelnetEvent(server, addr,message):
        print('telnet',addr,message)
        if message.startswith('quit'):
            return True
        from command8266 import rcv
        server.send(rcv(str(message)))
        return False

    def services_run(ip,timeloop):
        import server as services
        telnet = services.Server("",7777, "IHomeware Terminal")
        telnet.autoclose = False
        telnet.listen(doTelnetEvent)

        import broadcast
        web = services.WebServer("", 8080)
        web.listen(broadcast.http)

        udp = services.Broadcast(callbackFn=timeloop)
        udp.listen(broadcast.discovery)
        pass

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
                   period=1000, callback=timerLoop)

            services_run(wlan.ifconfig()[0],timerLoop)
            loop()
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
    sleep(30)
    reset()