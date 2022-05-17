try:
    import usocket as socket
except:
    import socket
import command8266 as cmd
import time
import errno
import machine
callback = None
callbackFeed = None
lock = False
class TCPServer:
    def __main__(self):
        self.conn = None
        pass
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
        self.conn.listen(1)
        self.conn.setsockopt(socket.SOL_SOCKET, 20, accept_telnet_connect)
        print("Escutando em ", self.addr)
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
    global callback, lock, callbackFeed
    if lock:
        return
    try:
        lock = True
        client, addr = sck.accept()
        client.setblocking(True)
        # client.sendall(bytes([255, 251, 34]))  # allow line mode
        # client.sendall(bytes([255, 251, 1]))  # turn off local echo
        client.send('OK\r\n')
        time.sleep(1)
        data = ''
        bts = b''
        is_telnet = False
        while True:
            try:
                if callbackFeed:
                    callbackFeed()
                res = client.recv(32)
            except OSError as e:
                if e.errno in [errno.ECONNABORTED, errno.ECONNRESET, errno.ENOTCONN]:
                    return None
                machine.idle()
                continue
            try:
                if res[0] > 0xd0:
                    is_telnet = True
                    client.send('cmd:\r\n')
                    continue
                bts += res
                if (len(res) == 1):
                    continue
                data = bts.decode('utf-8')
                if data in ['exit', 'quit']:
                    client.close()
                    return None
                bts = b''
                cmd.sendCB = client.send
                client.send(cmd.rcv(data)+'\r\n')
            except Exception as e:
                print(e)
                continue
    except Exception as x:
        print('telnet:', x)
    finally:
        lock = False
        cmd.sendCB = None