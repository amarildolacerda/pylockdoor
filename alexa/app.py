from gc import collect, mem_alloc, mem_free
from os import uname
from time import sleep

import broadcast
import commands as cm
from machine import DEEPSLEEP_RESET, Timer, idle, reset, reset_cause
from micropython import const

import config as g
import event as ev
import mqtt
import ntp
import server as services
import wifimgr


def doTelnetEvent(server, addr,message):
    print('telnet',addr,message)
    return True


def services_run(ip,timeloop):
   telnet = services.Server("",7777, "IHomeware Terminal")
   telnet.listen(doTelnetEvent)

   web = services.WebServer("", 8080)
   web.listen(broadcast.http)

   udp = services.Broadcast(callbackFn=timeloop)
   udp.listen(broadcast.discovery)
   pass

wlan = None
def connectWifi():
        global wlan
        if not wlan:
           wlan = wifimgr.get_connection()
        return wlan and wlan.isconnected()


class mainApp:
    def start(self, port ):
        self.port = port
        self.init()
        self.bind()
        pass
    def timerLoop(self,x):
        #collect()
        #idle()
        #print('timerloop', mem_free())
        pass   
    def init(self):
        g.start()

        #timer = Timer(-1)
        #timer.init(mode=Timer.PERIODIC,
        #           period=5000, callback=self.timerLoop)
        pass
    def bind(self):
            global wlan
            wlan = None
            if not connectWifi():
               reset()
            try: 
                ntp.settime()
            except: 
                pass
            mqttConnect(wifimgr.ifconfig()[0])
            services_run(wifimgr.ifconfig()[0], self.timerLoop)


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
            mqtt.host = g.config[g.CFG_MQTTHOST]
            mqtt.create(g.uid, g.config[g.CFG_MQTTHOST],
                        g.config[g.CFG_MQTTUSER], g.config[g.CFG_MQTTPASS])
            mqtt.callback(mqtt_rcv)
            mqtt.cnt()
            mqtt.sb(mqtt.topic_command_in())
            mqtt.p(mqtt.tpfx()+'/ip', ip)
        except OSError as e:
            p(e)


def start(port = 8080):
    mainApp().start(port)
