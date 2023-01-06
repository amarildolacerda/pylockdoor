import usocket as socket


def readFile(nome:str):
    with open(nome, 'r') as f:
        return f.read()


def getAlexaDescriptionXML(friendlyName): 
    return readFile('alexa_description.xml').format(friendlyName=friendlyName);

class AlexaUDPServer:
    def __init__(self, port=1900):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', port))
        self.sock.setblocking(False)

    def accept_connection(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print('alexa',data)
                if data.startswith(b'M-SEARCH * HTTP/1.1'):
                   self.sock.sendto(readFile('alexa_search.html').format(ip=ip_address), addr)
                pass 
            except :
                pass    
        pass

    def run(self, ip_address):
        print('Alexa binding')
        #self.sock.listen(1)
        #print('b1')
        #self.sock.setsockopt(socket.SOL_SOCKET, 20, accept_alexa_connect)
        #self.accept_connection()
        #print('b2')

    def get_msg(self):
        if self.sock:
            data, addr = self.sock.recv()
            if not data:
                return None
            print(addr[0],data)
            pass    

def accept_alexa_connect(client): 
        client, addr = client.accept()
        while True:
          try:  
            data, addr = client.recvfrom( 1024)
            print('alexa',data)
            if data.startswith(b'M-SEARCH * HTTP/1.1'):
                client.sendto(readFile('alexa_search.html').format(ip=ip_address), addr)
          except Exception as e:
            pass
               
def AlexaRun(ip_address):
   server = AlexaUDPServer(1900)
   server.run(ip_address)
   return server
