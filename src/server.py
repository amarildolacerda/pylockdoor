try:
    import usocket as socket
except:
    import socket

import errno
import time
from os import listdir

from machine import idle

import command8266 as cmd

callback = None
callbackFeed = None
lock = False
class TCPServer:
    def __main__(self):
        self.conn = None
    def callback(self, cb):
        global callback
        callback = cb
    def feed(self, cb):
        global callbackFeed
        callbackFeed = cb
    def start(self, add='0.0.0.0', port=7777):
        self.client = None
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addrinfo = socket.getaddrinfo(add, port)
        self.addr = self.addrinfo[0][-1]
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.setblocking(True)
        self.conn.bind(self.addr)
        try:
            self.conn.listen(1)
            self.conn.setsockopt(socket.SOL_SOCKET, 20, accept_telnet_connect)
            print("\r\nTerm {}".format( self.addr))
        except:
            pass    
    def close(self):
        if (self.conn != None):
            self.conn.close()
        self.conn = None
    def checkTimeout(self, conn_lst, dif):
        d = time.ticks_diff(time.ticks_ms(), conn_lst)
        return (d > dif)
    def wait_msg(self):
        pass
def accept_telnet_connect(sck):
    from json import dumps
    global callback, lock, callbackFeed
    if lock:
        return
    try:
        lock = True
        client, addr = sck.accept()
        client.setblocking(False)
        client.send('ok\r\n')
        data = ''
        bts = b''
        print('term:',addr[0])
        while True:
            try:
                cmd.sendCB = client.send
                if callbackFeed:
                    callbackFeed()
                res = client.recv(32)
            except OSError as e:
                if e.errno in [errno.ECONNABORTED, errno.ECONNRESET, errno.ENOTCONN]:
                    return None
                idle()
                continue
            if res:
                try:
                    if res[0] == 0x08 and len(bts)>0:
                        bts = bts[:-1]
                        continue
                    if (res[:-1]) not in [b'\r',b'\n'] :
                        bts += (res or '')
                        continue
                    data = bts.decode('utf-8')
                    bts = b''
                    if data.startswith('exit'):
                        client.close()
                        return None
                    cmd.sendCB = None
                    client.send(cmd.rcv(data))
                except Exception as e:
                    print(e)
                    continue
    except Exception as x:
        print('telnet:', x)
    finally:
        lock = False
        cmd.sendCB = None