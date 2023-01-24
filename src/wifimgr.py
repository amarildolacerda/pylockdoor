from gc import collect
from time import sleep, ticks_diff, ticks_ms

from machine import reset
from micropython import const
from network import AP_IF, STA_IF, WLAN

from config import gKey, sKey

_N = const(None)
_F = const(False)
_T = const(True)
wlan_sta = WLAN(STA_IF)
wlan_ap =  WLAN(AP_IF)
conn_lst = ticks_ms()

def getConfig():
    pass
def setConfig(s, p):
    sKey('ssid' , s)
    sKey('password',  p)
    getConfig()

def isconnected():
    return wlan_sta.isconnected()
def ifconfig():
    global wlan_sta
    return wlan_sta.ifconfig()
suspendreset = False
def timerReset(x):
    pass
def checkTimeout(tm, dif):
    return  ticks_diff(ticks_ms(), tm)> dif
def timerFeed():
    global conn_lst 
    conn_lst = ticks_ms()
    collect()
def get_connection():
    global wlan_sta
    
    if wlan_sta.isconnected():
        return wlan_sta
    connected = _F
    try:
        if wlan_sta.isconnected():
            return wlan_sta
        getConfig()
        timerFeed()    
        wlan_sta.active(_T)
        connected = do_connect(gKey('ssid'), gKey('password'))    
        if not connected: 
          for ap in setup.ssid:
            connected = do_connect(ap[0], ap[1])
            if connected:
                break
        if connected:
               if (wlan_ap):
                    wlan_ap.active(_F)
               print('\r\nConectou:{} '.format( gKey('ssid')))
               timerFeed()    
    except Exception as e:
        print(e)
    if not connected:
        connected = start()
        return wlan_ap
    if connected:
        return wlan_sta
    return _N
def do_connect(ssid, password):
    global wlan_sta
    connected = False
    wlan_sta.active(_T)
    if wlan_sta.isconnected():
        return _N
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        if wlan_sta.isconnected(): break
        sleep(0.2)
        print('.', end='')
    return wlan_sta.isconnected()


def start():
    wlan_ap.active(True)
    wlan_ap.config(essid=gKey('ap_ssid'), password=gKey('ap_password'), authmode=3)
    print('ssid: {} pass: {}'.format(gKey('ap_ssid'), gKey('ap_password')))

