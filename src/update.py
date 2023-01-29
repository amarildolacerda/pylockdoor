import socket
import ssl


class github:
    def __init__(self,host=None,port=80, url=None):
        self.HOST, self.PORT = host or "raw.githubusercontent.com", port or 443
        self.url = url or "/amarildolacerda/pylockdoor/main/src/{file}"
    def get(self,file):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
           try: 
            sock.connect((self.HOST, self.PORT))
            sock.sendall(b"GET " + self.url.format(file=file).encode() + b" HTTP/1.1\r\nHost: " + self.HOST.encode() + b"\r\n\r\n")
            sock.settimeout(5)
            data = b""
            while True:
                packet = sock.recv(1024)
                if not packet:
                    break
                print(packet)
                data += packet
            header, body = data.split(b"\r\n\r\n", 1)
            return body.decode()
           finally:
            sock.close() 


# requer autenticacao https
# # HTTP/1.1 301 Moved Permanently\r\nConnection: close\r\nContent-Length: 0\r\
def update():
    g = github()
    lst = g.get('update.list')
    print(lst)  

update()    