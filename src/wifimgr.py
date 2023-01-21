import socket
from gc import collect
from time import sleep, ticks_diff, ticks_ms

import network
import ure
from machine import reset
from micropython import const

import config as g
import configshow as show

_N = const(None)
_F = const(False)
_T = const(True)
wlan_sta = network.WLAN(network.STA_IF)
wlan_ap =  network.WLAN(network.AP_IF)
server_socket = _N
conn_lst = ticks_ms()
c_ssid = None
c_pass = None
c_id = None
def getConfig():
    global c_ssid, c_pass, c_id
    c_ssid = g.config['ssid']
    c_pass = g.config['password']
    c_id = g.config['mqtt_prefix']
def setConfig(s, p):
    global c_id
    g.config['ssid'] = s
    g.config['password'] = p
    g.config['mqtt_prefix'] = c_id
    getConfig()

def isconnected():
    return wlan_sta.isconnected()
def ifconfig():
    global wlan_sta
    return wlan_sta.ifconfig()
suspendreset = False
def timerReset(x):
    global suspendreset, conn_lst
    if (not suspendreset and  (not checkTimeout(conn_lst, 120000))):
        return
    sleep(10)
    print('timerReset')
    reset()
def checkTimeout(tm, dif):
    return  ticks_diff(ticks_ms(), tm)> dif
def timerFeed():
    global conn_lst 
    conn_lst = ticks_ms()
    collect()
def get_connection():
    global wlan_sta
    global c_ssid, c_pass
    if wlan_sta.isconnected():
        return wlan_sta
    connected = _F
    try:
        if wlan_sta.isconnected():
            return wlan_sta
        getConfig()
        timerFeed()    
        wlan_sta.active(_T)
        connected = do_connect(c_ssid, c_pass)
        if connected:
               if (wlan_ap):
                    wlan_ap.active(_F)
               print('\r\nConectou:{} '.format( c_ssid))
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
    wlan_ap.config(essid=g.config['ap_ssid'], password=g.config['ap_password'], authmode=3)
    print('ssid: {} pass: {}'.format(g.config['ap_ssid'], g.config['ap_password']))

