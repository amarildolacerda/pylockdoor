
import socket
import time

import ure
from machine import idle

import config as g


class Alexa:
    def __init__(self,ip):
        self.ip = ip
    def readFile(self,nome:str):  
        with open(nome, 'r') as f:return f.read()
    def sendto(self, destination, message):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(message, destination)
        idle()
        time.sleep(0.1)
    def send_msearch(self,  addr):
        self.sendto(addr, self.readFile("msearch.html").format(self.ip))

def readFile(nome:str):  
        with open(nome, 'r') as f:return f.read()


def discovery(sender,addr, data:str ):
        ip = g.ifconfig[0]
        if data.startswith(b"M-SEARCH"):
                print('m-search',addr)
                alexa = Alexa(ip)
                alexa.send_msearch(addr)
        else:        
           print('broadcast',ip, addr,data)
        return True
    

def _send_header(client, status_code, content_length, contentType):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: {}; charset=utf-8\r\n".format(contentType))
    if content_length :
        client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")
    time.sleep(0.2) 

def send_response(client, payload, status_code=200, contentType='text/html'):
    content_length = len(payload)
    _send_header(client, status_code, content_length, contentType)
    if content_length > 0:
        client.sendall(payload)
def handle_not_found(client, url):
    send_response(client, "{}".format(url), 404)


def http(client,addr,request):
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP",
                                 request).group(1).decode("utf-8").rstrip("/")
                print('Url',url)
                if url.endswith('.xml') or url.endswith('.html')   :
                    try:    
                       print('responder com',url) 
                       send_response(client,  
readFile(url).format(name=g.config['mqtt_name'] or 'indef',uuid= g.uid, url=url) 
,200,'application/xml' )
                    except Exception as e:
                       print(str(e))
                       send_response(client,readFile('erro.html').format(msg=str(e), url=url) ,200 )

                else:
                       handle_not_found(client, url)
                time.sleep(0.2) 
                client.close()       
                return true

