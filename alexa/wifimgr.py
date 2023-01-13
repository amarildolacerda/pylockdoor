import socket
import time
from gc import collect

import machine
import network
import ure
from micropython import const

import config as g

_N = const(None)
_F = const(False)
_T = const(True)
wlan_sta = network.WLAN(network.STA_IF)
wlan_ap =  network.WLAN(network.AP_IF)
server_socket = _N
conn_lst = time.ticks_ms()
c_ssid = None
c_pass = None
c_id = None
_port = 8080
connected = None
def getConfig():
    global c_ssid, c_pass, c_id
    c_ssid = g.config['ssid']
    c_pass = g.config['password']
    c_id = g.config['mqtt_prefix']
    return g.config
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
    if suspendreset:
        return
    if (not checkTimeout(conn_lst, 60000)):
        return
    time.sleep(10)
    machine.reset()
def checkTimeout(tm, dif):
    d = time.ticks_diff(time.ticks_ms(), tm)
    return (d > dif)
def timerFeed():
    global conn_lst
    conn_lst = time.ticks_ms()
def get_connection():
    global wlan_sta,_port, c_ssid, c_pass, connected
    if connected and wlan_sta.isconnected():
        return wlan_sta
    try:
        getConfig()
        connected = do_connect(c_ssid, c_pass)
        if connected:
               if (wlan_ap):
                    wlan_ap.active(_F)
               print('\r\nConectou: {} {} '.format(c_ssid, ifconfig()))
               timerFeed()    
    except Exception as e:
        print(e)
    if not connected:
        connected = start(_port)
    return wlan_sta
def do_connect(ssid, password):
    global wlan_sta
    print('connecting')
    wlan_sta.active(_T)
    wlan_sta.connect(ssid, password)
    for retry in range(100):
        if wlan_sta.isconnected(): break
        time.sleep(0.2)
        print('.', end='')
    return wlan_sta.isconnected()

def _send_header(client, status_code, content_length, contentType):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: {}; charset=utf-8\r\n".format(contentType))
    if content_length is not _N:
        client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")
    time.sleep(0.1) 


def send_response(client, payload, status_code=200, contentType='text/html'):
    content_length = len(payload)
    _send_header(client, status_code, content_length, contentType)
    if content_length > 0:
        client.sendall(payload)
    time.sleep(0.2) 
    machine.idle()
    client.close()
def handle_not_found(client, url):
    send_response(client, "{}".format(url), 404)
def readFile(n:str):  
        with open(n, 'r') as f:
            return f.read()
def accept_http(sock):
    try:
        while _T:
            client, addr = sock.accept()
            try:
                request = b""
                request = client.recv(32)
                if "HTTP" not in request:
                        break
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                                 request).group(1).decode("utf-8").rstrip("/")
                print(request)
                collect()
                if url.startswith('description.xml') :
                       send_response(client,  
readFile('alexa_description.xml').format(g.config['mqtt_name'], g.uid) 
,200,'application/xml' )
                else:
                       handle_not_found(client, url)
                break
            except OSError as e:
                if client: client.close()
                return None
            except KeyboardInterrupt as e:
                if client: client.close()
                return None
            except Exception as x:
                print(x)
                continue
    finally:
           pass
def start(port):
    global server_socket, suspendreset, wlan_sta, _port
    _port = port
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    wlan_sta.active(_T)
    wlan_ap.active(_T)
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    server_socket.listen(1)
    server_socket.setsockopt(socket.SOL_SOCKET, 20, accept_http)
 