from gc import collect
from utime import sleep, ticks_diff, ticks_ms

from machine import reset
from micropython import const
from network import AP_IF, STA_IF, WLAN

from config import gKey, sKey

_N = const(None)
_F = const(False)
_T = const(True)
wlan_sta = WLAN(STA_IF)
wlan_ap =  WLAN(AP_IF)
def setConfig(s, p):
    sKey('ssid' , s)
    sKey('password',  p)
    from config import IFCONFIG, dados
    dados[IFCONFIG] = wlan_sta.ifconfig()
def isconnected():
    return wlan_sta.isconnected()
def ifconfig():
    global wlan_sta
    return wlan_sta.ifconfig()
def checkTimeout(tm, dif):
    return  ticks_diff(ticks_ms(), tm)> dif
def get_connection():
    global wlan_sta
    if wlan_sta and  wlan_sta.isconnected():
        return wlan_sta
    connected = _F
    try:
        wlan_sta.active(_T)
        sc =  sorted(wlan_sta.scan(), key=lambda x: x[3], reverse=True)
        from setup import ssids  
        for ssid, bssid, channel, rssi, authmode, hidden in sc:
            pos = [i for i, sublist in enumerate(ssids) if sublist[0] == str(ssid)]
            if len(pos)==0:continue
            i = pos[0]
            connected = do_connect(ssids[i][0], ssids[i][1] if authmode==3 else None)    
            if connected: break
        if not connected: 
                for ap in ssids:
                    connected = do_connect(ap[0], ap[1])
                    if connected:
                        break
    except Exception as e:
        print(e)
    if not connected:
        connected = start()
        return wlan_ap
    return wlan_sta
def do_connect(ssid, password):
    global wlan_sta
    wlan_sta.connect(ssid, password)
    print('\r\b{}'.format(ssid))
    for retry in range(100):
        if wlan_sta.isconnected(): break
        sleep(0.2)
        print('.', end='')
    if wlan_sta.isconnected:
        setConfig(ssid,password)
        print('\r\nConectou:{} '.format( ssid))
    return wlan_sta.isconnected()
def start():
    wlan_ap.active(True)
    wlan_ap.config(essid=gKey('ap_ssid'), password=gKey('ap_password'), authmode=3)
    print('ssid: {} pass: {}'.format(gKey('ap_ssid'), gKey('ap_password')))

