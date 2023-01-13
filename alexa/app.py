from gc import collect, mem_alloc, mem_free
from os import uname
from time import sleep

import broadcast
from machine import DEEPSLEEP_RESET, Timer, idle, reset, reset_cause
from micropython import const

import ntp
import server as services
import wifimgr


def doTelnetEvent(server, addr,message):
    print('telnet',addr,message)
    return True

def doWebEvent(server, addr,message):
    print('web',addr,message)
    return True


def services_run(ip,timeloop):
   telnet = services.Server("",7777, "IHomeware Terminal")
   telnet.listen(doTelnetEvent)

   web = services.WebServer("", 8080)
   web.listen(doWebEvent)

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
        collect()
        idle()
        print('timerloop', mem_free())
        pass   
    def init(self):
        timer = Timer(-1)
        timer.init(mode=Timer.PERIODIC,
                   period=1000, callback=self.timerLoop)
 
    def bind(self):
            global wlan
            wlan = None
            if not connectWifi():
               reset()
            #print(wifimgr.c_ssid, wifimgr.ifconfig())
            try: 
                ntp.settime()
            except: 
                pass
            #wifimgr.start(self.port)    
            services_run(wifimgr.ifconfig()[0], self.timerLoop)


def start(port = 8080):
    mainApp().start(port)
