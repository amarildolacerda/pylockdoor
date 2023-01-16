from gc import collect


def now():
   import utime
   t = utime.localtime()
   return '{}-{}-{}T{}:{}:{}'.format(t[0],t[1],t[2],t[3],t[4],t[5])

class Alexa:
    def __init__(self,ip):
        self.ip = ip
    def readFile(self,nome:str):  
        with open(nome, 'r') as f:return f.read()
    def sendto(self, destination, message):
        from socket import AF_INET, SOCK_DGRAM, socket
        temp_socket = socket(AF_INET, SOCK_DGRAM)
        temp_socket.sendto(message, destination)
        from machine import idle
        idle()
        import time
        time.sleep(0.1)
        temp_socket.close()
    def send_msearch(self,  addr):
        self.sendto(addr, self.readFile("msearch.html").format(self.ip))

def readFile(nome:str):  
        with open(nome, 'r') as f:return f.read()


def discovery(sender,addr, data:str ):
        from config import IFCONFIG, dados
        ip = dados[IFCONFIG][0]
        if data.startswith(b"M-SEARCH"):
                alexa = Alexa(ip)
                alexa.send_msearch(addr)
        elif data.startswith(b"NOTIFY"):
            pass        
        else:        
           print('discoverey',ip, addr,data)
        return True

def getState(pin='4'):
    from config import gtrigg
    return gtrigg(pin)
def action_state(value:int,pin='4'):
    from config import strigg
    strigg(pin,value)
    return True

def make_header(client, status_code, contentType, length):
     client.write("HTTP/1.1 {} OK\r\n".format(status_code) )
     client.write("CONTENT-LENGTH: {}\r\n".format(length))
     client.write('CONTENT-TYPE: {} charset="utf-8"\r\n'.format(contentType))
     client.write("DATE: {}\r\n".format(now()))
     client.write("EXT:\r\n")
     client.write("SERVER: ihomeware UPnP/1.0, Unspecified\r\n")
     client.write("X-User-Agent: ihomeware\r\n")
     client.write("CONNECTION: close\r\n")
     client.write("\r\n")
     collect()
    

def send_response(client, payload, status_code=200, contentType='text/html'):
    z = len(payload)
    make_header(client,status_code,contentType,z )
    for l in payload.split('\r\n'):
       client.write(payload)
       client.write('\r\n')
    collect()   
    return True
    
def handle_not_found(client, url):
    send_response(client, "{}".format(url), 404)
    return True


def label():
    from config import config
    return config['label'] or config['mqtt_name']
def dbg(txt):
    print(txt)
    return True
def handle_request(client, data):
        if (
            data.find(b"POST /upnp/control/basicevent1 HTTP/1.1") == 0
            and data.find(b"#GetBinaryState") != -1
        ):          
           return send_response(client,  readFile('state.soap').format(state=getState()))
        elif data.find(b"GET /eventservice.xml HTTP/1.1") == 0:
           return send_response(client,  readFile('eventservice.xml'),200,'application/xml')
        elif data.find(b"GET /setup.xml HTTP/1.1") == 0:
            from config import uid
            return send_response(client, readFile('setup.xml').format(name=label(), uuid=uid),200,'application/xml' )
        elif (
            data.find(b'#SetBinaryState')
            != -1
        ):
            success = False
            if data.find(b"<BinaryState>1</BinaryState>") != -1:
                success = action_state(1) 
            elif data.find(b"<BinaryState>0</BinaryState>") != -1:
                success = action_state(0)
            else:
                print("Unknown Binary State request:")
            if success:
                 from gc import collect
                 collect()
                 send_response(client,  readFile('state.soap').format(state=getState()))
                 return True
            else: 
                return False    
        else:
            return False


def http(client,addr,request):
        import ure
        try:
                client.setblocking(False)
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                                 request).group(1).decode("utf-8").rstrip("/")
                print('Url',url)
                if not handle_request(client, request):                         
                    if url.endswith('.xml') or url.endswith('.html')   :
                        from config import uid
                        send_response(client,      (readFile(url) or '').format(name=label() or 'indef',uuid= uid, url=url)     ,200,'text/{}'.format(url.split('.')[1]) )
                    else: handle_not_found(client, url)

        except Exception as e:
            print(str(e), ' in ', request)
            send_response(client,readFile('erro.html').format(msg=str(e), url=url) ,500 )
        return True    
