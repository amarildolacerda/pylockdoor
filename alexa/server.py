import socket
import struct
from gc import mem_free
from time import sleep

import network
from machine import DEEPSLEEP_RESET, Timer, idle, reset, reset_cause


class Server:
    def __init__(self, host,port, welcome=None, socketType=socket.SOCK_STREAM):
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
    def receive_data(self,sck):
        sck.setblocking(True)
        try:
            conn, addr = self.sock.accept()
            print("Connected by", addr)
            if self.welcome:
               conn.send("{} MemFree: {} \r\n".format(self.welcome,mem_free()))
            bts = b''
            while True:
                try: 
                        res = conn.recv(16)
                        if res:
                            if res[0] == 0x08 and len(bts)>0:
                                    bts = bts[:-1]
                                    continue
                            bts += (res or '')
                            if not bts.endswith(self.end):
                                    continue
                            if bts.startswith('quit'):
                                    return None
                            if (self.messageEvent): self.messageEvent(conn,addr,bts)
                            bts = b''
                        # close connection
                except EAGAIN:
                    idle()
                    collect()
                    continue        
                except Exception as e:
                    print(str(e))
                    idle()
                    sleep(0.1)    
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
                      if not self.messageEvent(sck,data,addr) :
                        break
            except Exception as e:
                print(str(e))
                idle()
                collect()
                if self.callbackFn: self.callbackFn(self)
                else:
                  time.sleep(0.1)
        self.sock.setblocking(0)    
        self.sock.close() 

class WebServer(Server):
    def __init__(self, host, port):
        super().__init__(host, port, None,socket.SOCK_STREAM)
    def listen(self, messageEvent):
        return super().listen(messageEvent,end=b'\r\n\r\n')
    
