import socket
import struct
import time
from gc import collect, mem_free

import network
import uselect
from machine import DEEPSLEEP_RESET, Timer, idle, reset, reset_cause


class Server:
    def __init__(self, host,port, welcome=None, socketType=socket.SOCK_STREAM):
        self.autoclose = False
        self.host = host
        self.port = port
        self.welcome = welcome
        self.socketType = socketType
        self.sock = socket.socket(socket.AF_INET, self.socketType)
        self.sock.setblocking(True)
        self.sock.bind((self.host, self.port))

    def listen(self, messageEvent, end=b'\r\n'):
        self.end = end
        self.messageEvent = messageEvent
        self.sock.listen(1)
        self.sock.setsockopt(socket.SOL_SOCKET, 20, self.receive_data)
        print('Listen {}:{}'.format(self.host,self.port))
        pass
    def next(self):
        idle()
        collect()

      
    def receive_data(self,sck):
        try:
            conn, addr = self.sock.accept()
            conn.settimeout(1)

            print("Connected by",self.__class__.__name__,addr)
            if self.welcome:
               conn.send("{} MemFree: {} \r\n".format(self.welcome,mem_free()))
            bts = b''
            sck.setblocking(False)
            while True:
                try: 
                        res = conn.recv(8)
                        if res:
                            if res[0] == 0x08 and len(bts)>0:
                                    bts = bts[:-1]
                                    continue
                            bts += (res or '')
                            
                except Exception as e:
                    if str(e).find('ETIME') < 0:
                       print(self.__class__.__name__,str(e))
                       print(self.autoclose,bts.endswith(self.end),self.end,bts)
                    else:   
                    #if bts.endswith(self.end):
                            if (self.messageEvent): 
                               if  self.messageEvent(conn,addr,bts):
                                  break
                            bts=b''
                    if self.autoclose: break
                    self.next()
                       
        finally:
            sck.setblocking(True)  
            return conn and conn.close()


class Broadcast(Server):
    def __init__(self,host="", callbackFn=None):
         super().__init__(host, 1900,None,socket.SOCK_DGRAM)
         self.bindBroadcast()
         self.callbackFn = callbackFn
   
    def bindBroadcast(self,addr="239.255.255.250"):
        try:
            INADDR_ANY = 0
            ip_as_bytes = bytes(map(int, addr.split(".")))    
            self.mreq = struct.pack("4sl",ip_as_bytes,INADDR_ANY)
            self.sock.setsockopt(
                        socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq
                    )
        except Exception as  e:
            print(str(e))
    def listen(self, messageEvent):
        self.messageEvent = messageEvent
        self.receive_data(self.sock)

    def receive_data(self,sck):
        self.sock.setblocking(1)
        while True:
            try:
                data, addr = self.sock.recvfrom(128)
                if data:
                    if self.messageEvent: 
                      if not self.messageEvent(sck,addr,data) :
                        break
                    if self.autoclose: break
                    self.next()
            except Exception as e:
                print(str(e))
                self.next()
                if self.callbackFn: self.callbackFn(self)
                else:
                  time.sleep(0.1)
        self.sock.setblocking(0)    
        self.sock.close() 

class WebServer(Server):
    def __init__(self, host, port):
        super().__init__(host, port, None,socket.SOCK_STREAM)
        self.autoclose = True
    def listen(self, messageEvent):
        return super().listen(messageEvent,end=b'\r\n')
    
