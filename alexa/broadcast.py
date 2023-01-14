
import socket
import time
from gc import collect, mem_free

import ure
import utime
from machine import Pin, idle

import config as g


def now():
   t = utime.localtime()
   return '{}-{}-{}T{}:{}:{}'.format(t[0],t[1],t[2],t[3],t[4],t[5])

class Alexa:
    def __init__(self,ip):
        self.ip = ip
    def readFile(self,nome:str):  
        with open(nome, 'r') as f:return f.read()
    def sendto(self, destination, message):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(message, destination)
        idle()
        time.sleep(0.1)
    def send_msearch(self,  addr):
        self.sendto(addr, self.readFile("msearch.html").format(self.ip))

def readFile(nome:str):  
        with open(nome, 'r') as f:return f.read()


def discovery(sender,addr, data:str ):
        ip = g.ifconfig[0]
        if data.startswith(b"M-SEARCH"):
                alexa = Alexa(ip)
                alexa.send_msearch(addr)
        elif data.startswith(b"NOTIFY"):
            pass        
        else:        
           print('discoverey',ip, addr,data)
        return True

def getState(pin=4):
    return g.gpin(pin)
def action_state(value:int,pin=4):
    g.spin(pin,value)
    return True

def make_header(soap, status_code, contentType):
    return      ("HTTP/1.1 {code} OK\r\n"
                "CONTENT-LENGTH: {len}\r\n"
                'CONTENT-TYPE: {type} charset="utf-8"\r\n'
                "DATE: {data}\r\n"
                "EXT:\r\n"
                "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                "X-User-Agent: redsonic\r\n"
                "CONNECTION: close\r\n"
                "\r\n"
                "{payload}").format(len=len(soap), data=now(),payload=soap,code=status_code,type=contentType)
    

def send_response(client, payload, status_code=200, contentType='text/html'):
    client.sendall(make_header(payload,status_code,contentType ))
    collect()
    return True
    
def handle_not_found(client, url):
    send_response(client, "{}".format(url), 404)
    return True


def label():
    return g.config[g.CFG_LABEL] or g.config[g.CFG_MQTTNAME]
def dbg(txt):
    print(txt)
    return True
def handle_request(client, data):
        if (
            data.find(b"POST /upnp/control/basicevent1 HTTP/1.1") == 0
            and data.find(b"#GetBinaryState") != -1
        ):          
           return send_response(client,  readFile('state.soap').format(state=getState()))
        elif data.find(b"GET /eventservice.xml HTTP/1.1") == 0:
           return send_response(client,  readFile('eventservice.xml'),200,'application/xml')
        elif data.find(b"GET /setup.xml HTTP/1.1") == 0:
            return send_response(client, readFile('setup.xml').format(name=label(), uuid=g.uid),200,'application/xml' )
        elif (
            data.find(b'#SetBinaryState')
            != -1
        ):
            print(data)
            success = False
            if data.find(b"<BinaryState>1</BinaryState>") != -1:
                # on
                print("Responding to ON for %s" )
                success = action_state(1) 
            elif data.find(b"<BinaryState>0</BinaryState>") != -1:
                # off
                print("Responding to OFF for %s")
                success = action_state(0)
            else:
                print("Unknown Binary State request:")
            collect()
            if success:
                 send_response(client,  readFile('state.soap').format(state=getState()))
                 return True
            else: 
                return False    
        else:
            return False


def http(client,addr,request):
        try:
                client.setblocking(False)
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                                 request).group(1).decode("utf-8").rstrip("/")
                print('Url',url)
                if not handle_request(client, request):                         
                    if url.endswith('.xml') or url.endswith('.html')   :
                        send_response(client,      (readFile(url) or '').format(name=label() or 'indef',uuid= g.uid, url=url)     ,200,'text/{}'.format(url.split('.')[1]) )
                    else: handle_not_found(client, url)

        except Exception as e:
            print(str(e), ' in ', request)
            send_response(client,readFile('erro.html').format(msg=str(e), url=url) ,500 )
        finally:
            time.sleep(0.2) 
            client.close()       
        return true    
