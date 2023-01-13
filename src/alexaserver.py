import time
from gc import collect

import usocket as socket
from machine import freq, idle
from micropython import const

try:
    import ustruct as struct
except:
    import struct

INADDR_ANY = const(0)
class AlexaDiscovery:
    def __init__(self, http_address, port=1900, callbackFn=None):
        self.ip = const("239.255.255.250")
        self.http_address = http_address
        self.callbackFn = callbackFn
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((self.ip, port))
            self.mreq = struct.pack("4sl",self.inet_aton(self.ip),INADDR_ANY)
            self.sock.setsockopt(
                        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq
                    )
        except Exception as  e:
            print(str(e))
        self.timer = time.ticks_ms()
    def inet_aton(self,addr):
        ip_as_bytes = bytes(map(int, addr.split(".")))
        return ip_as_bytes

    def listen(self, timeout = 120000):
        self.sock.setblocking(1)
        while True:
            try:
                data, addr = self.sock.recvfrom(128)
                if data:
                    self.timer = time.ticks_ms()
                    collect()
                    if not self.do_receive_event(data,addr) :
                        break
            except Exception as e:
                print(str(e))
                idle()
                collect()
                time.sleep(0.1)
                self.do_no_data_event(self.timer)
                if timeout and self.checkTimeout(self.timer, timeout): break
        self.sock.setblocking(0)    
        self.sock.close() 
    def checkTimeout(self, tm, dif):
        d = time.ticks_diff(time.ticks_ms(), tm)
        return (d > dif)
    def readFile(self,nome:str):  
        with open(nome, 'r') as f:return f.read()
    def sendto(self, destination, message):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(message, destination)
        idle()
        time.sleep(0.1)
    def do_receive_event(self, data:str, addr):
        print(data)
        if data.startswith(b"M-SEARCH"):
            self.sendto(addr, self.readFile("alexa_search.html").format(self.http_address))
            return True
        return True 
    def do_no_data_event(self, data)        :
        if self.callbackFn:
           return self.callbackFn(data)

def AlexaRun(ip_address, callbackFn):
   server = AlexaDiscovery(ip_address, 1900, None)
   server.listen(None)
   return server