import time
from gc import collect

import usocket as socket
from machine import idle, sleep


def readFile(nome:str):
    with open(nome, 'r') as f:
        return f.read()


def getAlexaDescriptionXML(friendlyName): 
    return readFile('alexa_description.xml').format(friendlyName=friendlyName);

class AlexaUDPServer:
    def __init__(self, port=1900):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))
        print('biding')
        self.sock.setblocking(0)
        print('blocking 0')
        self.timer = time.ticks_ms()

    def listen(self, ip_address, callbackFn):
        #self.sock.listen(1)
        print('listen')
        while True:
            try:
                print('accept')
                conn, addr = self.sock.accept()
                print('accepted')
                data = conn.recv(1024)
                print('recv:',data)
                if data.startswith(b'M-SEARCH * HTTP/1.1'):
                   conn.sendto(readFile('alexa_search.html').format(ip=ip_address), addr)
                   break
            except :
                idle()
                collect()
                sleep(1)
                if (callbackFn):
                   callbackFn(self.timer)
                if not self.checkTimeout(self.timer, 120000): break   
                pass   
        self.sock.close()     
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
