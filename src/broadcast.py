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

def timerFeedSet():
        from wifimgr import timerFeed
        timerFeed()


def discovery(sender,addr, data:str ):
        from config import IFCONFIG, dados
        if data.startswith(b"M-SEARCH"):
                alexa = Alexa(dados[IFCONFIG][0])
                alexa.send_msearch(addr)
        else:        
           print( addr,data)
        timerFeedSet()
        return True

def getState(pin=None):
    from config import gtrigg
    return gtrigg(pin or g.config['auto-pin'])
def action_state(value:int,pin=None):
    from config import strigg
    strigg(pin or g.config['auto-pin'] ,value)
    return True

def mkhdr(client, status_code, contentType, length):
     client.write("HTTP/1.1 {} OK\r\n".format(status_code) )
     client.write("CONTENT-LENGTH: {}\r\n".format(length))
     client.write('CONTENT-TYPE: {} charset="utf-8"\r\n'.format(contentType))
     client.write("DATE: {}\r\n".format(now()))
     client.write("EXT:\r\n")
     client.write("SERVER: ihomeware UPnP/1.0, Unspecified\r\n")
     client.write("X-User-Agent: ihomeware\r\n")
     client.write("CONNECTION: close\r\n")
     client.write("CACHE-CONTROL: no-cache\r\n")
     client.write("\r\n")
     collect()
    

def mkrsp(client, payload, status_code=200, contentType='text/html'):
    z = len(payload)
    mkhdr(client,status_code,contentType,z )
    client.write(payload)
    return True
    
def notfnd(client, url):
    mkrsp(client, "{}".format(url), 404)
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
           return mkrsp(client,  readFile('state.soap').format(state=getState()))
        elif data.find(b"GET /eventservice.xml HTTP/1.1") == 0:
           return mkrsp(client,  readFile('eventservice.xml'),200,'application/xml')
        elif data.find(b"GET /setup.xml HTTP/1.1") == 0:
            from config import uid
            return mkrsp(client, readFile('setup.xml').format(name=label(), uuid=uid),200,'application/xml' )
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
                 mkrsp(client,  readFile('state.soap').format(state=getState()))
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
                    ext = url.split('.')
                    if len(ext)>1:
                       if  ext[1] in ['xml','html','json']   :
                          from config import uid
                          mkrsp(client,      (readFile(url) or '').format(name=label() or 'indef',uuid= uid, url=url)     ,200,'text/{}'.format(ext[1]) )
                    else: notfnd(client, url)

        except Exception as e:
            print(str(e), ' in ', request)
            mkrsp(client,readFile('erro.html').format(msg=str(e), url=url) ,500 )
        timerFeedSet()        
        return True    
