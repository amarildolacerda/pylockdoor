import time
import mqtt
import wifimgr
import machine
_N = None
_T = True
_F = False
try:
    import esp32
    defineEsp32 = _T
except:
    defineEsp32 = _F
    import esp
try:
    import network
    import command8266 as cm
    import event as ev
    import config as g
    import configshow as show
    import gc
    import server
    import ntp
    wlan = _N
    wdt = _N
    telnet = _N
    def wdt_feed():
        wifimgr.timerFeed()
    def connectWifi():
        global wlan
        wlan = wifimgr.get_connection()
        g.ifconfig = wlan.ifconfig()
        return wlan.isconnected()
    def mqtt_rcv(_t, _p):
        t = _t.decode('utf-8')
        p = _p.decode('utf-8')
        try:
            cmds = p.split(';')
            for item in cmds:
                cm.tpRcv(t, item)
                machine.idle()
                gc.collect()
        except OSError as e:
            mqtt.p('Invalid', 0)
            pass
    def mqttConnect(ip=''):
        try:
            mqtt.topic = mqtt.tpfx()
            mqtt.host = g.config['mqtt_host']
            mqtt.create(g.uid, g.config['mqtt_host'],
                        g.config['mqtt_user'], g.config['mqtt_password'])  # create a mqtt client
            mqtt.callback(mqtt_rcv)  # set callback
            mqtt.cnt()  # connect mqtt
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
    wdt = None
    errCount = 0
    def gpioLoopCallback():
        global errCount
        try:
            if connectWifi():
                try:
                    wdt_feed()
                    mqtt.check_msg()
                    ev.cv(mqtt.connected)
                    if mqtt.connected:
                        mqtt.sendStatus()
                        errCount = 0
                except:
                    errCount = errCount + 1
                    p('Reconectando MQTT...')
                    if errCount > 10:
                        machine.reset()
                    mqttConnect(wlan.ifconfig()[0])
            gc.collect()
        except Exception as e:
            pass
    def telnetCallback(data):
        return cm.rcv(data)
    def p(x):
        print(x)
    def timerLoop(x):
        wifimgr.timerReset(True)
        ev.cv(False)
        gc.collect()
        machine.idle()
    timer = None
    def init():
        global timer
        ev.init()
        g.start()
        timer = machine.Timer(-1)
        timer.init(mode=machine.Timer.PERIODIC,
                   period=500, callback=timerLoop)
    def run():
        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('0.woke from a deep sleep')
            ev.setSleep(-1)
        try:
            init()
            connectWifi()
            try:
                ntp.settime()
            except:
                pass
            telnet = None
            mqttConnect(wlan.ifconfig()[0])
            if (g.config['locked'] == 0):
                gc.collect()
                telnet = server.TCPServer()
                telnet.callback(telnetCallback)
                telnet.feed(gpioLoopCallback)
                telnet.start()
            print('Mem Loop free: {} allocated: {}'.format(
                gc.mem_free(), gc.mem_alloc()))
            loop()
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            print(e)
            machine.reset()
        finally:
            if (telnet is not None):
                telnet.close()
            mqtt.dcnt()
            if (wlan is not None):
                wlan.close()
except Exception as e:
    print('encerrando....')
    print(e)
    time.sleep(30)
    machine.reset()