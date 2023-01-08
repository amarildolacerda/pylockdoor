import time
from gc import collect

import usocket as socket
from machine import idle
from micropython import const

try:
    import ustruct as struct
except:
    import struct
INADDR_ANY = const(0)
def inet_aton(addr):
    ip_as_bytes = bytes(map(int, addr.split(".")))
    return ip_as_bytes
class server:
    def __init__(self, port=1900):
        self.ip = const("239.255.255.250")
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
    def do_receive_event(self, data:str, addr): pass
    def do_no_data_event(self,data): pass
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
                self.do_no_data_event(self.timer)
                if timeout and self.checkTimeout(self.timer, timeout): break
        self.sock.setblocking(0)    
        self.sock.close()  

    def checkTimeout(self, tm, dif):
        d = time.ticks_diff(time.ticks_ms(), tm)
        return (d > dif)


