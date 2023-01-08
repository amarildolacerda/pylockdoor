import time
from gc import collect

import usocket as socket
from machine import idle, sleep
from micropython import const

try:
    import ustruct as struct
except:
    import struct
INADDR_ANY = const(0)
def inet_aton(addr):
    ip_as_bytes = bytes(map(int, addr.split(".")))
    return ip_as_bytes
def readFile(nome:str):
    with open(nome, 'r') as f:
        return f.read()
def getAlexaDescriptionXML(friendlyName): 
    return readFile('alexa_description.xml').format(friendlyName=friendlyName);
class AlexaUDPServer:
    def __init__(self, port=1900):
        self.ip = const("239.255.255.250")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("", port))
            self.mreq = struct.pack("4sl",inet_aton(self.ip),INADDR_ANY)
            self.sock.setsockopt(
                        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq
                    )
        except Exception as  e:
            print(str(e))
        self.timer = time.ticks_ms()
    def response_search(self,addr,ip_address):
         collect()
         self.sock.sendto(readFile('alexa_search.html').format(ip_address), addr)
    def listen(self, ip_address, callbackFn):
        self.sock.setblocking(1)
        while True:
            try:
                data, addr = self.sock.recvfrom(128)
                if data:
                    print('recv:',data)
                    collect()
                    if data.startswith(b'NOTIFY'): pass
                    elif data.startswith(b'M-SEARCH'):
                        self.response_search(addr,ip_address)
                        break
                if (callbackFn):
                   callbackFn(self.timer)
            except Exception as e:
                print(str(e))
                idle()
                collect()
                if (callbackFn):
                   callbackFn(self.timer)
                pass   
        self.sock.setblocking(0)    
        self.sock.close()  
    def run(self, ip_address, callbackFn):
        self.listen(ip_address,callbackFn)
    def checkTimeout(self, tm, dif):
        d = time.ticks_diff(time.ticks_ms(), tm)
        return (d > dif)
def AlexaRun(ip_address, callbackFn):
   server = AlexaUDPServer(1900)
   server.run(ip_address,callbackFn)
   return server