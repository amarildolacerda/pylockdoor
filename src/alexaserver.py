import time
from gc import collect

import usocket as socket
from machine import idle, sleep

try:
    import ustruct as struct
except:
    import struct



INADDR_ANY = 0

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
        self.ip = "239.255.255.250"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        try:
            self.sock.bind((self.ip, port))
            self.mreq = struct.pack("4sl",inet_aton(self.ip),INADDR_ANY)
            self.sock.setsockopt(
                        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq
                    )
        except Exception as  e:
            print(str(e))

        self.timer = time.ticks_ms()

    def listen(self, ip_address, callbackFn):
   
        self.sock.setblocking(1)
        print('listen')
        while True:
            try:
                #conn, addr = self.sock.accept()
                #print('accepted')
                data, addr = self.sock.recvfrom(1024)
                print(data)
                if data:
                    print('recv:',data)
                    if data.startswith(b'M-SEARCH * HTTP/1.1'):
                        self.sock.sendto(readFile('alexa_search.html').format(ip=ip_address), addr)
                    break
                if (callbackFn):
                   callbackFn(self.timer)
            except :
                idle()
                collect()
                print('alexa wainting {}'.format(time.ticks_ms()))
                if (callbackFn):
                   callbackFn(self.timer)
                #if not self.checkTimeout(self.timer, 120000): break   
                pass   
        self.sock.blocking(0)    
        self.sock.close()  
        print('encerrou espera pela alexa')   
        pass

    def run(self, ip_address, callbackFn):
        print('Alexa binding')
        self.listen(ip_address,callbackFn)


    def checkTimeout(self, tm, dif):
        d = time.ticks_diff(time.ticks_ms(), tm)
        return (d > dif)


def AlexaRun(ip_address, callbackFn):
   server = AlexaUDPServer(1900)
   server.run(ip_address,callbackFn)
   return server
