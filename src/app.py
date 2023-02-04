from machine import reset

import mqtt as mq
from wifimgr import ifconfig
from utime import sleep

_N = None
_T = True
_F = False

try:

    def connectWifi(force=False):
        from wifimgr import get_connection, isconnected

        if force or not isconnected():
            get_connection()
        return isconnected()

    def mqtt_rcv(t, p):
        try:
            from command8266 import tpRcv

            return tpRcv(t.decode("utf-8"), p.decode("utf-8"))
        except OSError as e:
            mq.error("Invalido " + str(e))

    def mqttConnect(ip=""):
        try:
            from config import gKey, uid

            mq.host = gKey("mqtt_host")
            mq.create(uid, gKey("mqtt_host"), gKey("mqtt_user"), gKey("mqtt_password"))
            mq.callback(mqtt_rcv)
            mq.cnt()
            mq.sb(mq.topic_command_in())
            mq.p(mq.tpfx() + "/ip", ip)
            return mq != None
        except OSError as e:
            print(str(e))

    inLoop = False

    def eventLoop(v):
        from event import cv

        cv(v)

    primeira = True

    def loop(b=None):
        global inLoop, primeira
        if inLoop:
            return
        try:

            try:
                inLoop = True
                if connectWifi():
                    try:
                        mq.check_msg()
                        eventLoop(mq.connected)
                        mq.disp()
                        mq.sendStatus()
                    except Exception as e:
                        print(str(e))
                        mqttConnect(ifconfig()[0])
                else:
                    print("sem conexão")
                    eventLoop(False)
            finally:
                inLoop = False
                if primeira:
                    notifypnp()
                    primeira = False

            return True
        except Exception as e:
            pass

    def notifypnp():
        try:
            from broadcast import Alexa
            from server import Broadcast

            Alexa(ifconfig()[0]).send_notify(Broadcast())
        except Exception as e:
            print(str(e))

    def init():
        from config import restore

        restore()
        from event import init as ev_init

        ev_init()

    def doTelnetEvent(server, addr, message):
        from command8266 import rcv

        rsp = rcv(message[:-2].decode("utf-8"))
        if rsp:
            server.write(str(rsp))
            server.write("\r\n")
        return False

    def srvrun(ip, lp):
        import server as services

        telnet = services.TelnetServer(7777)
        telnet.listen(doTelnetEvent)
        import broadcast

        web = services.WebServer("", 8080)
        web.listen(broadcast.http)
        udp = services.Broadcast("", lp)
        udp.listen(broadcast.discovery)

    def bind():
        if not connectWifi(True):
            reset()
        try:
            from ntp import settime

            settime()
        except:
            pass
        mqttConnect(ifconfig()[0])
        from broadcast import Alexa

    def run():
        try:
            init()
            # while True:
            try:
                bind()
                srvrun(ifconfig()[0], loop)
            except:
                reset()
            # while True:
            #    loop()
            #    sleep(5)
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            print(e)

except Exception as e:
    print(e)
    pass
